from neo4j import GraphDatabase
import json

class Neo4jMethods:

    # Initialize Neo4j Driver
    def __init__(self, uri, username, password = None):
        # Exmaple - "bolt://10.0.1.238:7687"
        self.uri = "bolt://" + uri
        self.driver = GraphDatabase.driver(self.uri, auth=(username, password))
        self.session = self.driver.session()

    # Execute a given query
    def executeQuery(self, query):
        tx = self.session.begin_transaction()
        result = tx.run(query)
        tx.commit()
        return result
    