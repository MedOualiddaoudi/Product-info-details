from langchain_community.graphs import Neo4jGraph
from langchain_openai import OpenAI
from langchain.chains import GraphQAChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.graphs.networkx_graph import NetworkxEntityGraph
import os

# Initialize the Neo4j graph
neo4j_graph = Neo4jGraph(
    url="bolt://localhost:7687",
    username="neo4j",
    password="walid123"  # Replace with your actual password
)

# Initialize the LLM
llm = OpenAI(api_key="sk-None-EzIYxmcglJhtWmbCt82FT3BlbkFJoV9J5QicPJCjcx53Otsx")  # Replace with your actual API key

# Create an empty NetworkxEntityGraph
entity_graph = NetworkxEntityGraph()

# Fetch nodes and add them to the entity graph
nodes = neo4j_graph.query("MATCH (n) RETURN elementId(n) as id, labels(n) as labels, properties(n) as properties")
for node in nodes:
    # Combine labels and properties into a single dictionary
    attributes = {"labels": node['labels'], "properties": node['properties']}
    entity_graph._graph.add_node(node['id'], **attributes)  # Use the internal graph's add_node method

# Fetch relationships and add them to the entity graph
relationships = neo4j_graph.query("""
MATCH (a)-[r]->(b)
RETURN elementId(a) as start, elementId(b) as end, type(r) as type, properties(r) as properties
""")
for rel in relationships:
    # Add the edge with its relationship type and properties
    entity_graph._graph.add_edge(
        rel['start'],
        rel['end'],
        relation=rel['type'],
        **rel['properties']
    )

# Create prompt templates and chains
entity_prompt = PromptTemplate(template="Extract entities: {query}")
qa_prompt = PromptTemplate(template="Answer the question: {query}")

entity_chain = LLMChain(llm=llm, prompt=entity_prompt)
qa_chain = LLMChain(llm=llm, prompt=qa_prompt)

# Create the GraphQAChain using the NetworkxEntityGraph
graph_qa_chain = GraphQAChain(
    llm=llm,
    graph=entity_graph,
    entity_extraction_chain=entity_chain,
    qa_chain=qa_chain
)

# Example query
response = graph_qa_chain.run("What is the cheapest assurance?")
print(response)