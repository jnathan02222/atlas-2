from neo4j import GraphDatabase
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class DB:
    URI = f"neo4j://{os.environ['NEO4J_HOST']}:7687"
    AUTH = (os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
    DB = os.environ["NEO4J_DB"]

    @staticmethod
    def reset():
        with GraphDatabase.driver(DB.URI, auth=DB.AUTH) as driver:
            driver.execute_query("MATCH (a:Artist) DETACH DELETE a", database_=DB.DB)

    @staticmethod
    def add_artists(artists):
        with GraphDatabase.driver(DB.URI, auth=DB.AUTH) as driver:
            summary = driver.execute_query(
                """
                UNWIND $artists AS artist
                MERGE (n:Artist {title: artist.title})
                SET n = artist
                """,
                artists=artists,
                database_=DB.DB,
            ).summary
            logger.info(
                "Created {nodes_created} nodes in {time} ms.".format(
                    nodes_created=summary.counters.nodes_created,
                    time=summary.result_available_after,
                )
            )

    @staticmethod
    def add_edges(nodes):
        with GraphDatabase.driver(DB.URI, auth=DB.AUTH) as driver:
            summary = driver.execute_query(
                """
                UNWIND $nodes AS node
                MATCH (s:Artist { pageid: node.id })
                UNWIND node.edges AS edge
                MATCH (t:Artist { pageid: edge.target }) 
                MERGE (s)-[r:RELATED]->(t)
                SET r.description = edge.description
                """,
                nodes=nodes,
                database_=DB.DB,
            ).summary
            logger.info(f"Query counters: {summary.counters}.")

    @staticmethod
    def get_neighbours(title):
        with GraphDatabase.driver(DB.URI, auth=DB.AUTH) as driver:
            # Currently just outward links
            records = driver.execute_query(
                """
                MATCH (a:Artist {title: $title})-[r:RELATED]->(b:Artist) RETURN b.title AS title, b.description as description,(startNode(r) = a) as outward
                """,
                title=title,
                database_=DB.DB,
            ).records
            return records

    @staticmethod
    def get_edge_description(source, target):
        with GraphDatabase.driver(DB.URI, auth=DB.AUTH) as driver:
            # Currently just outward links
            records = driver.execute_query(
                """
                MATCH (a:Artist {title: $source})-[r:RELATED]->(b:Artist {title: $target}) RETURN r.description as description
                """,
                source=source,
                target=target,
                database_=DB.DB,
            ).records
            return records

    @staticmethod
    def search_for_artist(name):
        with GraphDatabase.driver(DB.URI, auth=DB.AUTH) as driver:
            records = driver.execute_query(
                """
                MATCH (a:Artist) WHERE toLower(a.title) CONTAINS toLower($name) RETURN a LIMIT 10
                """,
                name=name,
                database_=DB.DB,
            ).records
            return records

    @staticmethod
    def shortest_path(start_title, end_title):
        with GraphDatabase.driver(DB.URI, auth=DB.AUTH) as driver:
            records = driver.execute_query(
                """
                MATCH p = ALL SHORTEST (start:Artist { title: $start_title })((:Artist)-[:RELATED]-(:Artist)){1, 3}(end:Artist { title: $end_title })
                RETURN [n in nodes(p) | n.title] AS stops
                """,
                start_title=start_title,
                end_title=end_title,
                database_=DB.DB,
            ).records
            return records
