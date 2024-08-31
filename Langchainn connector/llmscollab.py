import streamlit as st
from neo4j import GraphDatabase
from datetime import datetime
import base64
from langchain_google_vertexai import VertexAI
from langchain.prompts import PromptTemplate
from google.cloud import aiplatform
from google.oauth2 import service_account
import vertexai
from vertexai.language_models import ChatModel
from google.auth.exceptions import DefaultCredentialsError
from google.api_core.exceptions import RetryError
from langchain_core.runnables.base import RunnableSequence


# Initialize PaLM 2 Model
def init_palm2_model():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            r'C:\Users\walid\Downloads\gen-lang-client-0447891830-6d52d921f249.json'
        )
        
        aiplatform.init(project='gen-lang-client-0447891830', location='us-east4', credentials=credentials)
        vertexai.init(project='gen-lang-client-0447891830', location='us-east4', credentials=credentials)
        
        chat_model = ChatModel.from_pretrained("chat-bison@002")
        chat = chat_model.start_chat(context="You are a language model assisting in processing queries for Attijariwafa Bank.")
        
        return chat
    except DefaultCredentialsError:
        st.error("Error: Could not find default credentials. Make sure you have authenticated properly.")
    except RetryError as e:
        st.error(f"RetryError: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    return None

# Initialize Gemini (Vertex AI)
def init_gemini():
    return VertexAI(
        model_name="gemini-1.5-flash-001",
        project="gen-lang-client-0447891830",
        location="us-east4",
        max_output_tokens=1024,
        temperature=0,
        top_p=0.95
    )

# Function to generate Cypher query using Gemini
def generate_cypher_query_with_gemini(gemini_model, user_query):
    prompt_template = """
   Graph Schema Overview:

The knowledge graph is constructed from three primary data sources: Assurance, Carte, and Pack. Each source has a structured format, with specific nodes representing different entities and relationships that connect these entities. The schema is designed to support complex queries about products and their attributes, and relationships across these three data sources.

Entities and Their Attributes:
Assurance:

Purpose: Represents insurance products.
Attributes:
productId (String): A unique identifier for each insurance product.
productType (String): The category or type of insurance (e.g., life, health).
productName (String): The name of the insurance product (e.g., "Life Protect").
Pack:

Purpose: Represents various product bundles or packages offered.
Attributes:
productId (String): A unique identifier for each pack.
productType (String): The type of pack (e.g., "Business Pack").
productName (String): The name of the pack (e.g., "Premium Pack").
Product:

Purpose: Represents individual products such as cards.
Attributes:
productId (String): A unique identifier for each product.
productType (String): The type of product (e.g., credit card).
productName (String): The name of the product (e.g., "Gold Card").
Target:

Purpose: Describes the intended audience or purpose of the products.
Attributes:
description (String): A textual description of the target audience or product’s purpose (e.g., "Young Professionals").
Formula:

Purpose: Represents pricing formulas or structures related to products.
Attributes:
composite_key (String): A unique key that combines the formula's name and price for identification.
name (String): The name of the formula (e.g., "Standard Pricing").
price (Float): The price associated with the formula.
currency (String): The currency in which the price is denominated (e.g., USD).
Feature:

Purpose: Represents specific features associated with a product’s formula.
Attributes:
description (String): A description of the feature (e.g., "24/7 Customer Support").
Pricing:

Purpose: Captures detailed pricing information for products.
Attributes:
price (Float): The actual price of the product.
currency (String): The currency in which the product is priced.
ExtraCosts:

Purpose: Represents any additional costs that may be associated with a product.
Attributes:
costs (String): A comma-separated list of extra costs (e.g., "Maintenance Fee, Annual Charge").
Characteristic:

Purpose: Describes specific characteristics of a product.
Attributes:
title (String): The title of the characteristic (e.g., "Card Benefits").
Detail:

Purpose: Provides detailed information linked to a product's characteristic.
Attributes:
composite_key (String): A unique key that combines a header and content to identify the detail.
head (String): The header or title of the detail (e.g., "Annual Fee").
content (String): The body content or explanation (e.g., "No fee for the first year").
Relationships Between Entities:
HAS_TARGET:

HAS_CHARACTERISTIC:

Description: Links a Product node to one or more Characteristic nodes, describing various features or benefits.
Example: MATCH (p:Product {productName: "Gold Card"})-[:HAS_CHARACTERISTIC]->(c:Characteristic) RETURN c.title
INCLUDES_DETAIL:

Description: Connects a Characteristic node to one or more Detail nodes, providing in-depth information on each characteristic.
Example: MATCH (c:Characteristic {title: "Card Benefits"})-[:INCLUDES_DETAIL]->(d:Detail) RETURN d.head, d.content
Instructions for Querying:
When generating Cypher queries, always produce plain text without any additional formatting, comments, or explanations.
The query should start with the Cypher command, such as MATCH or RETURN.
Understand the full context before generating queries to ensure that all related components and their connections are accurately represented.
    User Query: {user_query}
    """

    prompt = PromptTemplate(template=prompt_template, input_variables=["user_query"])
    llm_chain = prompt | gemini_model
    return llm_chain.invoke({"user_query": user_query}).strip()
# Function to transform Cypher query result to readable output using PaLM 2
def postprocess_response_with_palm2(chat, results):
    results_text = str(results)
    prompt = f"Given the following data from a Neo4j database query: {results_text}, create a human-readable explanation."
    response = chat.send_message(prompt)
    
    # Extract and return the text from the first candidate
    if hasattr(response, 'candidates') and len(response.candidates) > 0:
        return response.candidates[0].text.strip()
    else:
        st.error("No text candidates found in the PaLM 2 response.")
        return None

# Function to execute the generated Cypher query
def execute_cypher_query(cypher_query):
    driver = st.session_state['neo4j_driver']
    with driver.session() as session:
        result = session.run(cypher_query)
        return [record.data() for record in result]

# Function to convert image to base64
def get_image_as_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# Function to display chat history
def display_chat_history():
    user_image_path = r'd:\2ia projects\Stage 2a\Langchainn connector\user-128.png'
    bot_image_path = r'd:\2ia projects\Stage 2a\Langchainn connector\4712139.png'
    
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

# Main function to handle the chatbot workflow
def main():
    # Initialize session state for the first run
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    
    if 'neo4j_driver' not in st.session_state:
        st.session_state['neo4j_driver'] = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "walid123"))

    palm_chat = init_palm2_model()  # Initialize PaLM 2
    gemini_model = init_gemini()  # Initialize Gemini (Vertex AI)

    if not palm_chat or not gemini_model:
        st.error("Initialization failed for one of the models.")
        return

    col1, col2 = st.columns([1, 5])

    with col1:
        st.image(r"c:\Users\walid\Downloads\pngegg.png", width=120)

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
            with st.spinner("Processing your query..."):
                # Generate Cypher query using Gemini
                cypher_query = generate_cypher_query_with_gemini(gemini_model, user_input)
                st.write("Generated Cypher Query:", cypher_query)

                # Execute Cypher query and get results
                results = execute_cypher_query(cypher_query)
                st.write("Cypher Query Results:", results)

                # Postprocess the results using PaLM 2
                human_readable_output = postprocess_response_with_palm2(palm_chat, results)
                st.write("Human-readable Response:", human_readable_output)

                # Save chat history
                st.session_state['chat_history'].append({"user_query": user_input, "bot_response": human_readable_output})

                st.experimental_rerun()
        else:
            st.warning("Please enter a message.")

# Custom CSS for the chat history display
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

if __name__ == "__main__":
    load_custom_css()
    main()
