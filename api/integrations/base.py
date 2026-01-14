import itertools
from typing import AsyncGenerator
from abc import ABC, abstractmethod
from db import DB
import asyncio
from tqdm import tqdm
import logging
from integrations.types import Artist, Edge, Relation

logger = logging.getLogger(__name__)


class Base(ABC):
    async def sync(self) -> None:
        db = DB()
        artists = []

        # Grab all artists
        async for artist in self.get_vertices():
            artists.append(artist)
            logger.warning(f"{len(artists)} artists scraped")

        batches: list[tuple[Artist]] = list(itertools.batched(artists, 500))
        for batch in tqdm(batches):
            await db.add_artists([value for value in batch])

        # Makes adding edges up to 4x faster
        # todo: may be useful to create before adding artists, as it could speed up that too
        await db.init_index()

        # Grab edges in batches of 60 to avoid hammering whatever API is used
        # todo: make it possible to override this
        batches: list[tuple[Artist]] = list(itertools.batched(artists, 60))
        for i, batch in enumerate(tqdm(batches)):
            edge_lists: list[list[Edge]] = await asyncio.gather(
                *[self.get_edges(artist) for artist in batch]
            )
            logger.info(
                f"Generated edges for {i + 1}/{len(batches)} batches of artists"
            )

            for edge_list in edge_lists:
                if len(edge_list) > 0:
                    # Assumes all the sources in a list are the same, for optimization (only have to match the source node once)
                    await db.add_edges(
                        edge_list[0].source, edge_list, self.get_relationship_label()
                    )

    # Must be defined by subclasses
    @abstractmethod
    async def get_edges(self, artist: Artist) -> list[Edge]: ...

    @abstractmethod
    def get_relationship_label(self) -> Relation: ...

    # Untested - default behavior of retrieving from database
    # The idea is that other integrations may need to do something like this to match
    # artists scraped to artists that are already in the db
    # New artists will need a way to get a unique id
    # Potentially very slow
    async def get_vertices(self) -> AsyncGenerator[Artist]:
        async for artist in DB().all_artists():
            yield artist
