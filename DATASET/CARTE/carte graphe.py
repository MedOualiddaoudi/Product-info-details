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

def create_graph_from_json(json_data, graph):
    """Create nodes and relationships in the Neo4j graph based on the JSON data."""
    for card in json_data:
        # Product node setup
        product = Node("Product", productId=card["productId"], productType=card["productType"], productName=card["productName"])
        graph.merge(product, "Product", "productId")

        # Target nodes setup
        for target_desc in card["productTarget"]:
            target = Node("Target", description=target_desc)
            graph.merge(target, "Target", "description")
            rel = Relationship(product, "HAS_TARGET", target)
            graph.merge(rel)

        # Pricing node setup
        price = extract_numeric_value(card["productDetails"]["pricing"]["contribution"])
        pricing = Node("Pricing", price=price, currency="DH")
        graph.merge(pricing, "Pricing", "price")
        rel = Relationship(product, "HAS_PRICING", pricing)
        graph.merge(rel)

        # Extra costs setup
        extra_costs = card["productDetails"]["pricing"]["extraCosts"]
        extra_cost_node = Node("ExtraCosts", costs=", ".join(extra_costs))
        graph.merge(extra_cost_node, "ExtraCosts", "costs")
        rel = Relationship(pricing, "HAS_EXTRA_COSTS", extra_cost_node)
        graph.merge(rel)

        # Characteristics and details setup
        for characteristic in card["productDetails"]["characteristics"]:
            char_node = Node("Characteristic", title=characteristic["title"])
            graph.merge(char_node, "Characteristic", "title")
            rel = Relationship(product, "HAS_CHARACTERISTIC", char_node)
            graph.merge(rel)

            if isinstance(characteristic["detail"], dict):
                head = characteristic["detail"].get("head", [])
                content = characteristic["detail"].get("content", [])

                if isinstance(head, str):
                    head = [head]
                if isinstance(content, str):
                    content = [content]

                for head_item, content_item in zip(head, content):
                    composite_key = f"{head_item}_{content_item}"  # Create a unique key
                    detail_node = Node("Detail", composite_key=composite_key, head=head_item, content=content_item)
                    graph.merge(detail_node, "Detail", "composite_key")
                    rel_detail = Relationship(char_node, "INCLUDES_DETAIL", detail_node)
                    graph.merge(rel_detail)


# Connection to Neo4j Database
graph = Graph("bolt://localhost:7687", auth=("neo4j", "walid123"))

# Load data and create graph
json_data = load_json_file(r"D:\2ia projects\Stage 2a\DATASET\CARTE\sample_carte.json")
create_graph_from_json(json_data, graph)
