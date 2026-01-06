from integrations.base import Base
import itertools
import asyncio
import logging
from db import DB
from tqdm import tqdm
from wikipedia_api.client import Client

logger = logging.getLogger(__name__)


class Wikipedia(Base):
    def __init__(self):
        self.api_client: Client = Client()

    async def sync(self):
        DB.reset()
        # Scrape all pages that use the 'Template:Infobox musical artist' template
        await self.create_vertices()

        # Generate edges by scraping pages for links to each other
        await self.create_edges()

        # A useful addition would be to have deeper links (ie. the works of Radiohead and The Cardigans both appear in Romeo + Juliet)

    async def create_vertices(self):
        self.artists = {}

        async for artist in self.api_client.transcludedin(
            "Template:Infobox musical artist"
        ):
            self.artists[artist["title"]] = artist

        DB.add_artists([value for value in self.artists.values()])

    async def create_edges(self):
        batches = list(itertools.batched(self.artists.values(), 60))

        for i, batch in enumerate(tqdm(batches)):
            self.edges = []
            await asyncio.gather(*[self.get_node_edges(node) for node in batch])
            logger.info(
                f"Generated edges for {i + 1}/{len(batches)} batches of artists"
            )

            DB.add_edges(self.edges)

    async def get_node_edges(self, node):
        try:
            page_wikitext = await self.api_client.wikitext(node["title"])
            targets = []
            async for link in self.api_client.links(node["title"]):
                if link["title"] in self.artists and link["title"] in page_wikitext:
                    targets.append(self.artists[link["title"]]["pageid"])

            self.edges.append({"source": node["pageid"], "targets": targets})
        except Exception as e:
            logger.error(
                f"Processing links for {node['title']} failed with error {str(e)}"
            )
            return
