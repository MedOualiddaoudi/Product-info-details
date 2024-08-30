from neo4j import GraphDatabase

class Neo4jSchemaExtractor:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def get_node_schema(self):
        with self.driver.session() as session:
            return session.read_transaction(self._get_schema_nodes)

    def get_relationship_schema(self):
        with self.driver.session() as session:
            return session.read_transaction(self._get_schema_relationships)

    @staticmethod
    def _get_schema_nodes(tx):
        query = "CALL db.schema.nodeTypeProperties()"
        result = tx.run(query)
        return [record for record in result]

    @staticmethod
    def _get_schema_relationships(tx):
        query = "CALL db.schema.relTypeProperties()"
        result = tx.run(query)
        return [record for record in result]

if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "walid123"  # Replace with your actual password

    schema_extractor = Neo4jSchemaExtractor(uri, username, password)
    try:
        print("Node Schema:")
        node_schema = schema_extractor.get_node_schema()
        for node in node_schema:
            print(node)
        
        print("\nRelationship Schema:")
        relationship_schema = schema_extractor.get_relationship_schema()
        for relationship in relationship_schema:
            print(relationship)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        schema_extractor.close()
