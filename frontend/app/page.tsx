"use client";
import { useState } from "react";
import SearchBar from "@/common/SearchBar";
import Map from "@/common/Map";
import { Artist } from "@/api-codegen/client";

export default function Home() {
  const [selectedArtist, setSelectedArtist] = useState<Artist | undefined>();
  const [searchValue, setSearchValue] = useState("");

  return (
    <div>
      <div className="p-12 absolute z-10 w-full">
        <SearchBar
          placeholder="Enter a musician..."
          onSelect={(value) => {
            setSelectedArtist(value);
          }}
          searchValue={searchValue}
          setSearchValue={setSearchValue}
        />
      </div>
      <Map
        artist={selectedArtist}
        onSelect={(artist: Artist) => {
          setSearchValue(artist.title);
          setSelectedArtist(artist);
        }}
      />
    </div>
  );
}
