import streamlit as st
from ollama import Client
import sqlite3
import os
from qdrant_client import QdrantClient
st.set_page_config(page_title="Winy", page_icon="🍷", layout="centered")

QDRANT_CLIENT_URL = os.environ["QDRANT_CLIENT"] 
OLLAMA_URL = os.environ["OLLAMA"]


client_qdrant = QdrantClient(QDRANT_CLIENT_URL)
client_ollama = Client(host=OLLAMA_URL)

@st.cache_resource
def get_wines_names():
    conn = sqlite3.connect('wine_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT wine FROM wine_links')
    result = cursor.fetchall()
    wine_names = [wine[0] for wine in result]
    conn.close()
    return wine_names

# Mock function to simulate fetching wine URLs from an e-commerce API
def fetch_wine_url(wine_name):
    conn = sqlite3.connect('wine_database.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT link FROM wine_links WHERE wine="{wine_name}"')
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    else:
        return f"https://www.wine.com/product/search?query={wine_name.replace(' ', '+')}"

# Updated add_wine_links function
def add_wine_links(response_text):
    wine_names = get_wines_names()  # List of wine names in response 
    for wine_name in wine_names:
        if wine_name in response_text:
            wine_url = fetch_wine_url(wine_name)
            response_text = response_text.replace(wine_name, f"[{wine_name}]({wine_url})")
    return response_text

def show():
    st.title("🍷 Winy")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", 
                                         "content": "Enter the dish or cuisine (e.g., 'Bolognese lasagna'):"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    PROMPT_TEMPLATE_1 = '''
    FROM mistral
    SYSTEM You are a sommelier with extensive knowledge of wines from around the world.
    Your goal is to provide the best possible information about wine taste paired with the food.
    Just in a single sentence, no other informations
    USER INPUT: {query}
    '''

    PROMPT_TEMPLATE_2 = '''
    FROM mistral
    SYSTEM You are a sommelier with extensive knowledge of wines from around the world.
    Your goal is to use the provided bullet point list of wines to suggest how to pair them with the food. 
    Add additional, educative informantion about the wines. Just five sentences at max.
    USER INPUT: Pair {food} with {search_result}
    '''

    def get_recommendation(query):
        prompt = PROMPT_TEMPLATE_1.format(query=query)
        response = client_ollama.generate(model="mistral", prompt=prompt)
        return response["response"]
    
    def get_wines(query,llm_response):
        print(llm_response)
        search_result = client_qdrant.query(
        collection_name="wines5",
        query_text=llm_response
        )
        prompt = PROMPT_TEMPLATE_2.format(food=query,
                                          search_result=search_result)
        response = client_ollama.generate(model="mistral", prompt=prompt)
        return response["response"]

    if prompt := st.chat_input():

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        pairing = get_recommendation(st.session_state.messages)
        resp_wines = get_wines(st.session_state.messages,pairing)
        msg = add_wine_links(resp_wines)
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

if __name__ == '__main__':
    show()