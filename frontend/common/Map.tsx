import { useEffect, useState } from "react";
import { Artist } from "@/api-codegen/client";
import dynamic from "next/dynamic";
import { graphUrlsNeighbours } from "@/api-codegen/client";
import { GraphData } from "react-force-graph-2d";
// Import dynamically because it uses canvas, which requires window
const ForceGraph = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
});

type MapProps = {
  artist?: Artist;
  onSelect: (artist: Artist) => void;
};
export default function Map({ artist, onSelect }: MapProps) {
  const [graphData, setGraphData] = useState<GraphData<Artist> | undefined>();

  useEffect(() => {
    async function fetchNeighbours() {
      if (!artist) return;

      const response = await graphUrlsNeighbours({
        query: { title: artist.title },
      });
      const neighbours = response.data ?? [];

      function updateGraphData(prev: GraphData<Artist> | undefined) {
        if (!artist) return;

        const links = [];
        const nodes = [];
        debugger;

        // If the previous graph contains the current node, append previous nodes + links
        if (prev) {
          const prevNodes = prev.nodes.map((node) => node.title);
          if (prevNodes.includes(artist.title)) {
            nodes.push(...prev.nodes);
            links.push(...prev.links);
          }
        }

        // Add new links (bug - duplicate link)
        links.push(
          ...neighbours.map((neighbour) => ({
            source: artist.title,
            target: neighbour.title,
          }))
        );

        // Add new nodes if they don't aready exist
        const nodeSet = new Set(nodes.map((node) => node.title));
        [
          artist.title,
          ...neighbours.map((neighbour) => neighbour.title),
        ].forEach((title) => {
          if (!nodeSet.has(title)) {
            nodes.push({ title: title });
            nodeSet.add(title);
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
      nodeCanvasObject={(node, ctx, globalScale) => {
        const label = node.title;
        const fontSize = 12 / globalScale;
        ctx.font = `${fontSize}px Montserrat`;
        const textWidth = ctx.measureText(label).width;
        const bckgDimensions = [textWidth, fontSize].map(
          (n) => n + fontSize * 0.2
        ); // some padding

        ctx.fillStyle = "white";
        ctx.fillRect(
          (node.x ?? 0) - bckgDimensions[0] / 2,
          (node.y ?? 0) - bckgDimensions[1] / 2,
          bckgDimensions[0],
          bckgDimensions[1]
        );

        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillStyle = node.color;
        ctx.fillText(label, node.x ?? 0, node.y ?? 0);

        node.__bckgDimensions = bckgDimensions; // to re-use in nodePointerAreaPaint
      }}
      nodePointerAreaPaint={(node, color, ctx) => {
        ctx.fillStyle = color;
        const bckgDimensions = node.__bckgDimensions;
        bckgDimensions &&
          ctx.fillRect(
            (node.x ?? 0) - bckgDimensions[0] / 2,
            (node.y ?? 0) - bckgDimensions[1] / 2,
            bckgDimensions[0],
            bckgDimensions[1]
          );
      }}
      onNodeClick={(node) => {
        if (artist?.title === node.title) return;
        onSelect({ title: node.title });
      }}
    />
  );
}
