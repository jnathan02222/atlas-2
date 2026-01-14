import { useState, useRef, Dispatch, SetStateAction } from "react";
import { Artist } from "@/api-codegen/client";
import { graphUrlsSearch } from "@/api-codegen/client";
type SearchBarProps = {
  placeholder: string;
  onSelect: (value: Artist) => void;
  searchValue: string;
  setSearchValue: (value: string) => void;
  results: Artist[];
  setResults: (value: Artist[], timestamp: number) => void;
};
export default function SearchBar({
  placeholder,
  onSelect,
  searchValue,
  setSearchValue,
  results,
  setResults,
}: SearchBarProps) {
  async function handleSearch(value: string) {
    const timestamp = Date.now();
    setSearchValue(value);
    if (value == "") {
      setResults([], timestamp);
      return;
    }
    // TODO: debounce?
    const response = await graphUrlsSearch({ query: { name: value } });
    setResults(response.data ?? [], timestamp);
  }

  return (
    <div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (results.length > 0) {
            onSelect(results[0]);
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
              key={value.name}
              onClick={() => {
                onSelect(value);
              }}
            >
              {value.name}
            </div>
          );
        })}
      </div>
    </div>
  );
}
