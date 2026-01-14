"use client";
import { useState } from "react";
import SearchBar from "@/common/SearchBar";
import Map from "@/common/Map";
import EdgeSidebar from "@/common/EdgeSidebar";
import { Artist, Edge } from "@/api-codegen/client";

export default function Home() {
  const [selectedArtist, setSelectedArtist] = useState<Artist | undefined>();
  const [searchValue, setSearchValue] = useState("");
  const [showDescription, setShowDescription] = useState(false);

  const [selectedEdge, setSelectedEdge] = useState<Edge | undefined>();
  return (
    <div>
      <div className="p-12 absolute z-10">
        <SearchBar
          placeholder="Enter a musician"
          onSelect={(value) => {
            setSelectedArtist(value);
            setShowDescription(true);
          }}
          searchValue={searchValue}
          setSearchValue={(value) => {
            setSearchValue(value);
            setShowDescription(false);
          }}
        />
        {showDescription && (
          <div className="text-gray-500">
            {selectedArtist?.wikipedia_description}
          </div>
        )}
      </div>
      <EdgeSidebar edge={selectedEdge}></EdgeSidebar>
      <Map
        artist={selectedArtist}
        onSelect={(artist: Artist) => {
          setSearchValue(artist.name);
          setSelectedArtist(artist);
        }}
        onEdgeClick={(edge: Edge | undefined) => {
          setSelectedEdge(edge);
        }}
      />
    </div>
  );
}
