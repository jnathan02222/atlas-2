from abc import ABC, abstractmethod
from db import DB
import itertools
import asyncio
from tqdm import tqdm

import logging

logger = logging.getLogger(__name__)


class Base(ABC):
    async def sync(self):
        self.artists = {}

        async for artist in self.get_vertices():
            self.artists[artist["title"]] = artist

        batches = list(itertools.batched(self.artists.values(), 500))
        for batch in tqdm(batches):
            DB.add_artists([value for value in batch])

        batches = list(itertools.batched(self.artists.values(), 60))

        for i, batch in enumerate(tqdm(batches)):
            self.nodes = []
            await asyncio.gather(*[self.get_edges(node) for node in batch])
            logger.info(
                f"Generated edges for {i + 1}/{len(batches)} batches of artists"
            )

            DB.add_edges(self.nodes)

    @abstractmethod
    async def get_vertices(self): ...

    @abstractmethod
    async def get_edges(self, node): ...
