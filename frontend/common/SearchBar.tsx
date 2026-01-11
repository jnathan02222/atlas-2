import { useState, useRef, Dispatch, SetStateAction } from "react";
import { Artist } from "@/api-codegen/client";
import { graphUrlsSearch } from "@/api-codegen/client";
type SearchBarProps = {
  placeholder: string;
  onSelect: (value: Artist) => void;
  searchValue: string;
  setSearchValue: (value: string) => void;
};
export default function SearchBar({
  placeholder,
  onSelect,
  searchValue,
  setSearchValue,
}: SearchBarProps) {
  const [results, setResults] = useState<Artist[]>([]);
  const latestTimestamp = useRef(0);

  function setResultsLatest(results: Artist[], timestamp: number) {
    if (timestamp > latestTimestamp.current) {
      latestTimestamp.current = timestamp;
      setResults(results);
    }
  }
  function handleSelect(artist: Artist) {
    setSearchValue(artist.title);
    setResultsLatest([], Date.now());
    onSelect(artist);
  }

  async function handleSearch(value: string) {
    const timestamp = Date.now();
    setSearchValue(value);
    if (value == "") {
      setResultsLatest([], timestamp);
      return;
    }
    // TODO: debounce?
    const response = await graphUrlsSearch({ query: { name: value } });
    setResultsLatest(response.data ?? [], timestamp);
  }

  return (
    <div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (results.length > 0) {
            handleSelect(results[0]);
          }
        }}
      >
        <input
          type="text"
          id="name"
          placeholder={placeholder}
          className="text-5xl outline-none font-medium field-sizing-content pr-12"
          autoComplete="off"
          value={searchValue}
          onChange={(e) => {
            handleSearch(e.target.value);
          }}
        />
      </form>
      <div className="absolute w-128">
        {results.map((value) => {
          return (
            <div
              className="cursor-pointer"
              key={value.title}
              onClick={() => {
                handleSelect(value);
              }}
            >
              {value.title}
            </div>
          );
        })}
      </div>
    </div>
  );
}
