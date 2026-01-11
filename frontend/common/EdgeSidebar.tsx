import { graphUrlsEdgeDescription } from "@/api-codegen/client";
import { Link } from "./Map";
import { useCallback, useEffect, useRef, useState } from "react";
import { debounce } from "@tanstack/react-pacer";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";

export default function EdgeSidebar({ edge }: { edge: Link | undefined }) {
  const [edgeDescription, setEdgeDescription] = useState<string | undefined>();
  const latestTimestamp = useRef(0);
  const [isLoading, setIsLoading] = useState(false);

  function setResultsLatest(result: string | undefined, timestamp: number) {
    if (timestamp >= latestTimestamp.current) {
      latestTimestamp.current = timestamp;

      setEdgeDescription(result);
    }
  }

  const getEdgeDescription = useCallback(
    debounce(
      async (edge: Link | undefined) => {
        const timestamp = Date.now();
        setResultsLatest(undefined, timestamp);
        setIsLoading(true);
        if (!edge) {
          return;
        }
        const response = await graphUrlsEdgeDescription({
          query: { source: edge.sourceTitle, target: edge.targetTitle },
        });
        setIsLoading(false);

        if (response.data) {
          for (const item of response.data) {
            for (const paragraph of item.description) {
              if (paragraph.trim() === "") continue;

              setResultsLatest(paragraph, timestamp);
              break;
            }
          }
        }
      },
      { wait: 100 }
    ),
    []
  );

  useEffect(() => {
    getEdgeDescription(edge);
  }, [edge]);
  return (
    <>
      {edge && (
        <div className="absolute w-128 max- w-128 right-0 h-screen max-h-screen p-12 z-10 bg-white opacity-90 overflow-y-scroll overflow-x-hidden">
          <div className="font-bold">{`${edge.sourceTitle} → ${edge.targetTitle}`}</div>
          {isLoading && (
            <div className="w-full">
              <Skeleton count={5} />
            </div>
          )}

          <div
            dangerouslySetInnerHTML={{ __html: edgeDescription ?? "" }}
          ></div>
        </div>
      )}
    </>
  );
}
