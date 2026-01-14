from typing import Optional
from pydantic import BaseModel
from enum import StrEnum

type ArtistId = int


class Relation(StrEnum):
    WIKIPEDIA = "WIKIPEDIA"


class Artist(BaseModel):
    id: ArtistId  # A unique id to identify an artist
    name: str  # Display name - potentially not unique, don't use as identifier
    wikipedia_title: Optional[str] = None
    wikipedia_description: Optional[str] = None
    wikipedia_summary: Optional[str] = None


class Edge(BaseModel):
    source: Artist
    target: Artist
    wikipedia_description: Optional[str] = None
