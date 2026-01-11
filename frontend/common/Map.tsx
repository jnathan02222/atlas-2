import { useEffect, useState, useRef } from "react";
import { Artist } from "@/api-codegen/client";
import dynamic from "next/dynamic";
import { graphUrlsNeighbours } from "@/api-codegen/client";
import { GraphData, LinkObject } from "react-force-graph-2d";
import { text } from "stream/consumers";
// Import dynamically because it uses canvas, which requires window
const ForceGraph = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
});

export type Link = {
  sourceTitle: string;
  targetTitle: string;
};
type MapProps = {
  artist?: Artist;
  onSelect: (artist: Artist) => void;
  onEdgeHover: (edge: Link | undefined) => void;
};
export default function Map({ artist, onSelect, onEdgeHover }: MapProps) {
  const [graphData, setGraphData] = useState<
    GraphData<Artist, Link> | undefined
  >();
  const graphRef = useRef<any>(undefined);
  const [focusedLink, setFocusedLink] = useState<LinkObject | undefined>();

  const [vinylImages, setVinylImages] = useState<Array<HTMLImageElement>>([]);
  useEffect(() => {
    const imgs = [
      "vinyl1.svg",
      "vinyl2.svg",
      "vinyl3.svg",
      "vinyl4.svg",
      "vinyl5.svg",
    ];
    setVinylImages(
      imgs.map((src) => {
        const img = new Image();
        img.src = `./${src}`;
        return img;
      })
    );
  }, []);

  useEffect(() => {
    async function fetchNeighbours() {
      if (!artist) return;

      const response = await graphUrlsNeighbours({
        query: { title: artist.title },
      });
      const neighbours = response.data ?? [];

      function updateGraphData(prev: GraphData<Artist, Link> | undefined) {
        if (!artist) return;

        const links = [];
        const nodes = [];

        // If the previous graph contains the current node, append previous nodes + links
        let joined = false;
        if (prev) {
          for (const node of prev.nodes) {
            if (node.title === artist.title) {
              nodes.push(...prev.nodes);
              links.push(...prev.links);
              joined = true;
              break;
            }
          }
        }
        if (!joined) {
          graphRef.current.zoom(5, 1000);
          graphRef.current.centerAt(0, 0, 1000);
        }

        // Add new links (bug - duplicate link)
        links.push(
          ...neighbours.map((neighbour) => ({
            source: artist.title,
            target: neighbour.title,
            sourceTitle: artist.title,
            targetTitle: neighbour.title,
          }))
        );

        // Add new nodes if they don't aready exist
        const nodeSet = new Set(nodes.map((node) => node.title));
        [artist, ...neighbours].forEach((neighbour) => {
          if (!nodeSet.has(neighbour.title)) {
            nodes.push({
              title: neighbour.title,
              description: neighbour.description,
            });
            nodeSet.add(neighbour.title);
          }
        });

        return { nodes: nodes, links: links };
      }
      setGraphData(updateGraphData);
    }
    fetchNeighbours();
  }, [artist]);
  return (
    <ForceGraph
      graphData={graphData}
      nodeId="title"
      nodeLabel="title"
      nodeAutoColorBy="title"
      maxZoom={10}
      linkColor={(link) => (link === focusedLink ? "gray" : "")}
      linkWidth={(link) => (link === focusedLink ? 2 : 1)}
      // linkDirectionalParticles={(link) => (link === focusedLink ? 3 : 0)}
      // linkDirectionalParticleWidth={2}
      nodeCanvasObject={(node, ctx, globalScale) => {
        const label = node.title;
        const fontSize = 12 / globalScale;
        ctx.font = `${fontSize}px Noto Serif`;
        const textWidth = ctx.measureText(label).width;
        const bckgDimensions = [textWidth, fontSize].map(
          (n) => n + fontSize * 0.2
        ); // some padding

        const imgSize = 6;
        ctx.drawImage(
          vinylImages[label.length % 5],
          (node.x ?? 0) - imgSize / 2,
          (node.y ?? 0) - imgSize / 2,
          imgSize,
          imgSize
        );

        ctx.fillStyle = "white";
        ctx.fillRect(
          (node.x ?? 0) - bckgDimensions[0] / 2,
          (node.y ?? 0) + imgSize / 2,
          bckgDimensions[0],
          bckgDimensions[1]
        );

        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillStyle = "black";
        ctx.fillText(
          label,
          node.x ?? 0,
          (node.y ?? 0) + imgSize / 2 + bckgDimensions[1] / 2
        );

        node.__imgSize = imgSize; // to re-use in nodePointerAreaPaint
      }}
      nodePointerAreaPaint={(node, color, ctx) => {
        ctx.fillStyle = color;
        const imgSize = node.__imgSize;
        ctx.fillRect(
          (node.x ?? 0) - imgSize / 2,
          (node.y ?? 0) - imgSize / 2,
          imgSize,
          imgSize
        );
      }}
      onNodeClick={(node) => {
        if (artist?.title === node.title) return;
        onSelect({ title: node.title, description: node.description });
      }}
      ref={graphRef}
      onLinkClick={(link) => {
        if (link) {
          onEdgeHover({
            sourceTitle: link.sourceTitle,
            targetTitle: link.targetTitle,
          });
          setFocusedLink(link);
        } else {
          setFocusedLink(undefined);
          onEdgeHover(undefined);
        }
      }}
    />
  );
}
