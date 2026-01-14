from neo4j import AsyncGraphDatabase
import logging
import os
from dotenv import load_dotenv
from integrations.types import Artist, Edge, ArtistId, Relation
from typing import AsyncGenerator

load_dotenv()

logger = logging.getLogger(__name__)


class DB:
    URI = f"neo4j://{os.environ['NEO4J_HOST']}:7687"
    AUTH = (os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
    DB = os.environ["NEO4J_DB"]

    # todo: seems fast in practice, but is it idiomatic to initialize a driver every time?
    # also, there may be problems with closing the driver in parallel

    async def init_index(self) -> None:
        async with AsyncGraphDatabase.driver(DB.URI, auth=DB.AUTH) as driver:
            await driver.execute_query(
                "CREATE INDEX id_index IF NOT EXISTS FOR (n:Artist) ON (n.id)",
            )
            # Search index :)
            await driver.execute_query(
                "CREATE FULLTEXT INDEX name_index IF NOT EXISTS FOR (n:Artist) ON EACH [n.name]",
            )

    async def all_artists(self) -> AsyncGenerator[Artist]:
        # Warning: untested, potentially very slow in practice
        # Todo: look into if there is a way to call a generator for the response
        # loading ~100000 records seems kinda crazy
        async with AsyncGraphDatabase.driver(DB.URI, auth=DB.AUTH) as driver:
            records = (
                await driver.execute_query(
                    """
                    MATCH (a:Artist) return a
                    """,
                    database_=DB.DB,
                )
            ).records
            for record in records:
                yield Artist(**record.data())

    async def add_artists(self, artists: list[Artist]) -> None:
        async with AsyncGraphDatabase.driver(DB.URI, auth=DB.AUTH) as driver:
            # exclude_none=True allows us to avoid deleting properties that aren't in the object
            # SET += will delete any properties that are null in Artist
            summary = (
                await driver.execute_query(
                    """
                UNWIND $artists AS artist
                MERGE (n:Artist {id: artist.id})
                SET n += artist
                """,
                    artists=[
                        artist.model_dump(exclude_none=True) for artist in artists
                    ],
                    database_=DB.DB,
                )
            ).summary
            logger.info(
                "Created {nodes_created} nodes in {time} ms.".format(
                    nodes_created=summary.counters.nodes_created,
                    time=summary.result_available_after,
                )
            )

    async def add_edges(
        self, source: Artist, edges: list[Edge], relation: Relation
    ) -> None:
        # Probably the biggest bottleneck in a scrape due to the sheer volume of edges
        async with AsyncGraphDatabase.driver(DB.URI, auth=DB.AUTH) as driver:
            summary = (
                await driver.execute_query(
                    """
                    MATCH (s:Artist { id: $source.id })
                    UNWIND $edges AS edge
                    MATCH (t:Artist { id: edge.target_id }) 
                    MERGE (s)-[r:$($relation)]->(t)
                    SET r += edge.data
                    """,
                    source=source.model_dump(),
                    edges=[
                        {
                            "data": edge.model_dump(
                                exclude={"source", "target"},
                                exclude_none=True,  # exclude_none=True allows us to avoid deleting properties that aren't in the object
                            ),
                            "target_id": edge.target.id,
                        }
                        for edge in edges
                    ],
                    relation=relation,
                    database_=DB.DB,
                )
            ).summary
            logger.info(f"Query counters: {summary.counters}.")

    async def get_edges(
        self, artist_id: ArtistId, relations: list[Relation] = [Relation.WIKIPEDIA]
    ) -> list[Edge]:
        async with AsyncGraphDatabase.driver(DB.URI, auth=DB.AUTH) as driver:
            # Currently just outward links
            # Avoid returning the edge data here: just the vertices
            records = (
                await driver.execute_query(
                    """
                    MATCH (a:Artist {id: $artist_id})-[r: $any($relations)]->(b:Artist) RETURN a as source, b as target
                    """,
                    artist_id=artist_id,
                    relations=relations,
                    database_=DB.DB,
                )
            ).records
        return [Edge(**record.data()) for record in records]

    async def get_edge_data(self, source: ArtistId, target: ArtistId) -> list[Edge]:
        async with AsyncGraphDatabase.driver(DB.URI, auth=DB.AUTH) as driver:
            records = (
                await driver.execute_query(
                    """
                    MATCH (a:Artist {id: $source})-[r]-(b:Artist {id: $target}) RETURN r{.*, source: startNode(r), target: endNode(r)}
                    """,
                    source=source,
                    target=target,
                    database_=DB.DB,
                )
            ).records
        return [Edge(**record.data()["r"]) for record in records]

    async def get_artists(self, name: str) -> list[Artist]:
        # todo: write a better search engine. Should ideally match commonly used aliases
        # For example, the band Frankie Cosmos is redirected to Greta Kline, the lead singer
        # This should be captured
        # Look into elastisearch? Or is that overkill
        async with AsyncGraphDatabase.driver(DB.URI, auth=DB.AUTH) as driver:
            records = (
                await driver.execute_query(
                    """
                    MATCH (a:Artist) WHERE toLower(a.name) CONTAINS toLower($name) RETURN a LIMIT 10
                    """,
                    name=name,
                    database_=DB.DB,
                )
            ).records
        return [Artist(**record.data()["a"]) for record in records]

    # def shortest_path(start_title: str, end_title: str) -> list[Record]:
    #     with AsyncGraphDatabase.driver(DB.URI, auth=DB.AUTH) as driver:
    #         records = driver.execute_query(
    #             """
    #             MATCH p = ALL SHORTEST (start:Artist { title: $start_title })((:Artist)-[:RELATED]-(:Artist)){1, 3}(end:Artist { title: $end_title })
    #             RETURN [n in nodes(p) | n.title] AS stops
    #             """,
    #             start_title=start_title,
    #             end_title=end_title,
    #             database_=DB.DB,
    #         ).records
    #         return records
