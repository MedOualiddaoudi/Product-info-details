import streamlit as st
from neo4j import GraphDatabase
import vertexai
from vertexai.generative_models import GenerativeModel

# Initialize Vertex AI with your project details if not already initialized
if 'vertex_ai_initialized' not in st.session_state:
    vertexai.init(project="gen-lang-client-0447891830", location="us-east1")
    st.session_state['vertex_ai_initialized'] = True

# Set up Neo4j connection only once
if 'neo4j_driver' not in st.session_state:
    st.session_state['neo4j_driver'] = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "walid123"))

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

def generate_cypher_query(user_query):
    # Context for the LLM, same as what was developed before
    context =   """
    You are an expert in querying knowledge graphs. Our graph has been constructed using data from three main sources: Assurance, Carte, and Pack. Each source is structured similarly, with nodes representing different entities and relationships connecting them.

    ### Instructions:
    - When generating a Cypher query, ensure that the output is a plain text Cypher query with no additional formatting, code block delimiters, or Markdown.
    - The query should start directly with the Cypher command (e.g., `MATCH`, `RETURN`)
    - Do not include any additional text, explanations, or comments in the output.
    - always understand the full context before generting a query looking for the components of each node and all its links before so it adapts to what the input is not what it means 
   ### Nodes:
    1. **Assurance**: Represents insurance products with properties:
       - `productId` (String): Unique identifier for the assurance product.
       - `productType` (String): The type of the assurance.
       - `productName` (String): The name of the assurance product.

    2. **Target**: Represents target descriptions for products with a single property:
       - `description` (String): Description of the target audience or purpose.

    3. **Formula**: Represents a formula related to a product with properties:
       - `composite_key` (String): A unique key combining name and price.
       - `name` (String): Name of the formula.
       - `price` (Float): Price associated with the formula.
       - `currency` (String): The currency in which the price is denominated.

    4. **Feature**: Represents features associated with a formula with a property:
        - `description` (String): Description of the feature.

    ### Relationships:
    - `HAS_TARGET`: Connects an `Assurance` node to one or more `Target` nodes.
    - `HAS_FORMULA`: Connects an `Assurance` node to one or more `Formula` nodes.
    - `HAS_FEATURE`: Connects a `Formula` node to one or more `Feature` nodes.

    EXAMPLES:
    ** MATCH (p:Assurance {productName: "Product Name"})-[:HAS_TARGET]->(t:Target)
    RETURN t.description;
    ** MATCH (a:Assurance)-[r:HAS_FORMULA|HAS_TARGET]->(connectedNode)
    RETURN a.productName, type(r), connectedNode
    ### Nodes:
    1. **Pack**: Represents product packs with properties:
       - `productId` (String): Unique identifier for the pack.
       - `productType` (String): The type of the pack.
       - `productName` (String): The name of the pack.

    2. **Target**: Represents target descriptions for products with a single property:
       - `description` (String): Description of the target audience or purpose.

    3. **Formula**: Represents a formula related to a product with properties:
       - `composite_key` (String): A unique key combining name and price.
       - `name` (String): Name of the formula.
       - `price` (Float): Price associated with the formula.
       - `currency` (String): The currency in which the price is denominated.

    4. **Feature**: Represents features associated with a formula with a property:
        - `description` (String): Description of the feature.

    ### Relationships:
    - `HAS_TARGET`: Connects a `Pack` node to one or more `Target` nodes.
    - `HAS_FORMULA`: Connects a `Pack` node to one or more `Formula` nodes.
    - `HAS_FEATURE`: Connects a `Formula` node to one or more `Feature` nodes.

    EXAMPLES:
    ** MATCH (p:Pack {productName: "Pack Business"})-[:HAS_TARGET]->(t:Target)
    RETURN t.description;
    ** MATCH (p:Pack)-[r:HAS_FORMULA|HAS_TARGET]->(connectedNode)
    RETURN p.productName, type(r), connectedNode
     ### Nodes:
    1. **Product**: Represents products (cards) with properties:
       - `productId` (String): Unique identifier for the product.
       - `productType` (String): The type of the product.
       - `productName` (String): The name of the product.

    2. **Target**: Represents target descriptions for products with a single property:
       - `description` (String): Description of the target audience or purpose.

    3. **Pricing**: Represents the pricing details associated with products, having properties:
       - `price` (Float): The price of the product.
       - `currency` (String): The currency in which the price is denominated.

    4. **ExtraCosts**: Represents additional costs related to a product with properties:
       - `costs` (String): Comma-separated list of extra costs.

    5. **Characteristic**: Represents product characteristics with a property:
       - `title` (String): Title of the characteristic.

    6. **Detail**: Represents detailed information about a characteristic with properties:
       - `composite_key` (String): A unique key combining head and content.
       - `head` (String): A header or title of the detail.
       - `content` (String): The content or body of the detail.

    ### Relationships:
    - `HAS_TARGET`: Connects a `Product` node to one or more `Target` nodes.
    - `HAS_PRICING`: Connects a `Product` node to its `Pricing` node.
    - `HAS_EXTRA_COSTS`: Connects a `Pricing` node to its `ExtraCosts` node.
    - `HAS_CHARACTERISTIC`: Connects a `Product` node to one or more `Characteristic` nodes.
    - `INCLUDES_DETAIL`: Connects a `Characteristic` node to one or more `Detail` nodes.

    EXAMPLES:
    ** MATCH (p:Product {productName: "Product Name"})-[:HAS_TARGET]->(t:Target)
    RETURN t.description;
    ** MATCH (p:Product)-[r:HAS_PRICING|HAS_CHARACTERISTIC]->(connectedNode)
    RETURN p.productName, type(r), connectedNode
    
    
    when retriving data always get the product details!

    """

       # Combine the context with the user query
    full_input = context + "\nUser Query: " + user_query


    # Load the generative model
    model = GenerativeModel("gemini-1.5-flash-001")

    # Generate the Cypher query
    response = model.generate_content(
        [full_input],
        generation_config=generation_config,
        stream=False,
    )

    cypher_query = response.text.strip()

    if cypher_query.startswith("```cypher"):
        cypher_query = cypher_query.replace("```cypher", "").replace("```", "").strip()

    return cypher_query


def execute_cypher_query(cypher_query):
    # Use the driver object from the session state to create a session
    driver = st.session_state['neo4j_driver']
    
    with driver.session() as session:
        # Execute the Cypher query and return the results
        result = session.run(cypher_query)
        return [record.data() for record in result]


def format_response(results):
    # Initialize Vertex AI for generating a human-readable response
    model = GenerativeModel("gemini-1.5-flash-001")

    # Format the results into a text description for the user
    prompt = f"Given the following data from a Neo4j database query: {results}, create a human-readable explanation in paragraph format if there is multiple deails or a comparison sort it in point format "

    response = model.generate_content(
        [prompt],
        generation_config=generation_config,
        stream=False,
    )

    return response.text.strip()



from datetime import datetime
import base64
def get_image_as_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')
    
def display_chat_history():
    user_image_path = r'd:\2ia projects\Stage 2a\Langchainn connector\user-128.png'
    bot_image_path = r'd:\2ia projects\Stage 2a\Langchainn connector\4712139.png'
    
    # Convert images to base64 strings
    user_image_base64 = get_image_as_base64(user_image_path)
    bot_image_base64 = get_image_as_base64(bot_image_path)

    for entry in st.session_state['chat_history']:
        timestamp = datetime.now().strftime("%H:%M")

        st.markdown(f"""
        <div style='display: flex; align-items: flex-start; margin-bottom: 10px;'>
            <img src='data:image/png;base64,{user_image_base64}' style='width: 40px; height: 40px; border-radius: 50%; margin-right: 10px;' />
            <div style='background-color:#f1f1f1; padding:10px; border-radius:10px; flex-grow: 1;'>
                <strong>You</strong> <span style='color: #888; font-size: 0.8em;'>[{timestamp}]</span><br>{entry['user_query']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='display: flex; align-items: flex-start; margin-bottom: 10px;'>
            <img src='data:image/png;base64,{bot_image_base64}' style='width: 40px; height: 40px; border-radius: 50%; margin-right: 10px;' />
            <div style='background-color:#e0ffe0; padding:10px; border-radius:10px; flex-grow: 1;'>
                <strong>Bot</strong> <span style='color: #888; font-size: 0.8em;'>[{timestamp}]</span><br>{entry['bot_response']}
            </div>
        </div>
        """, unsafe_allow_html=True)


def main():
    # Create a two-column layout: one for the logo, one for the title
    col1, col2 = st.columns([1, 5])  # Adjust the ratio as needed

    with col1:
        st.image(r"c:\Users\walid\Downloads\pngegg.png", width=120)  # Replace with the path to your logo file

    with col2:
        st.markdown("""
        <div style='display: flex; align-items: center;'>
            <div>
                <h1 style='font-size: 2.5em; color: #ff5e00; margin: 0;'>Attijariwafa Bank</h1>
                <h2 style='font-size: 1.5em; color: #333; margin: 0;'>Product Information Chatbot</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #ff5e00;'>", unsafe_allow_html=True)

    display_chat_history()

    user_input = st.text_area("Your message:", height=50, max_chars=200, placeholder="Type your message here...")

    if st.button("Send", key="send_button", use_container_width=True):
        if user_input:
            with st.spinner("Generating response..."):
                cypher_query = generate_cypher_query(user_input)
                results = execute_cypher_query(cypher_query)
                human_readable_output = format_response(results)

                st.session_state['chat_history'].append({"user_query": user_input, "bot_response": human_readable_output})

                st.experimental_rerun()
        else:
            st.warning("Please enter a message.")

def load_custom_css():
    st.markdown("""
    <style>
    ::-webkit-scrollbar {
        width: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    ::-webkit-scrollbar-thumb {
        background: #ff5e00;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #d94e00;
    }
    html {
        scroll-behavior: smooth;
    }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

generation_config = {
    "max_output_tokens": 1024,
    "temperature": 0,
    "top_p": 0.95,
}

if __name__ == "__main__":
    main()


