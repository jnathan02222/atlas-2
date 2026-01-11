from integrations.base import Base
from wikipedia_api.client import Client

import logging

logger = logging.getLogger(__name__)


class Wikipedia(Base):
    def __init__(self):
        self.api_client: Client = Client()
        # A useful addition would be to have deeper links (ie. the works of Radiohead and The Cardigans both appear in Romeo + Juliet)

    async def get_vertices(self):
        # Scrape all pages that use the 'Template:Infobox musical artist' template
        async for artist in self.api_client.transcludedin(
            "Template:Infobox musical artist"
        ):
            yield artist

    async def get_edges(self, node):
        try:
            page_wikitext = await self.api_client.wikitext(node["title"])
            edges = []
            async for link in self.api_client.links(node["title"]):
                if link["title"] in self.artists and link["title"] in page_wikitext:
                    description = []
                    for paragraph in page_wikitext.split("\n\n"):
                        if link["title"] in paragraph:
                            description.append(paragraph)
                    edges.append(
                        {
                            "target": self.artists[link["title"]]["pageid"],
                            "description": description,
                        }
                    )

            self.nodes.append({"id": node["pageid"], "edges": edges})
        except Exception as e:
            logger.error(
                f"Processing links for {node['title']} failed with error {str(e)}"
            )
            return
