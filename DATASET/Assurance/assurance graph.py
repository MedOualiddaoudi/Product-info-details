import json
import re
from py2neo import Graph, Node, Relationship

def load_json_file(filepath):
    """Load JSON data from a file."""
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def extract_numeric_value(text):
    """Extract the numeric value from a string."""
    numbers = re.findall(r'\d+', text.replace(' ', ''))
    if numbers:
        return float("".join(numbers))
    return 0

def create_assurance_from_json(json_data, graph):
    """Create nodes and relationships in the Neo4j graph based on the ASSURANCE JSON data."""
    for assurance in json_data:
        # Assurance node setup
        assurance_node = Node("Assurance", productId=assurance["productId"], productType=assurance["productType"], productName=assurance["productName"])
        graph.merge(assurance_node, "Assurance", "productId")

        # Target nodes setup
        for target_desc in assurance["productTarget"]:
            target = Node("Target", description=target_desc)
            graph.merge(target, "Target", "description")
            rel = Relationship(assurance_node, "HAS_TARGET", target)
            graph.merge(rel)

        # Formula nodes setup
        for formula in assurance["productDetails"]["formulas"]:
            price = extract_numeric_value(formula["price"])
            composite_key = f"{formula['name']}_{price}"  # Create a unique key
            formula_node = Node("Formula", composite_key=composite_key, name=formula["name"], price=price, currency="DH")
            graph.merge(formula_node, "Formula", "composite_key")
            rel = Relationship(assurance_node, "HAS_FORMULA", formula_node)
            graph.merge(rel)

            # Feature nodes setup
            for feature in formula["features"]:
                if isinstance(feature, dict):
                    # Handling key-value pair features
                    for key, value in feature.items():
                        feature_description = f"{key}: {', '.join(value) if isinstance(value, list) else value}"
                        feature_node = Node("Feature", description=feature_description)
                        graph.merge(feature_node, "Feature", "description")
                        rel_feature = Relationship(formula_node, "HAS_FEATURE", feature_node)
                        graph.merge(rel_feature)
                else:
                    # Handling simple string features
                    feature_node = Node("Feature", description=feature)
                    graph.merge(feature_node, "Feature", "description")
                    rel_feature = Relationship(formula_node, "HAS_FEATURE", feature_node)
                    graph.merge(rel_feature)

# Connection to Neo4j Database
graph = Graph("bolt://localhost:7687", auth=("neo4j", "walid123"))

# Load data and create graph
json_data = load_json_file(r"D:\2ia projects\Stage 2a\DATASET\Assurance\sample_assurance_products.json")
create_assurance_from_json(json_data, graph)
