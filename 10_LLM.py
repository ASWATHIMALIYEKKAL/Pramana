import os
from dotenv import load_dotenv
import streamlit as st
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models import ChatOpenAI

# Load environment variables from .env file
load_dotenv()

# Set up Streamlit UI
st.set_page_config(page_title="Ayurveda Chatbot")
st.header("Welcome to the Ayurveda Chatbot")

# Initialize ChatOpenAI
api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    st.error("Error: OPENAI_API_KEY not found in environment variables.")
else:
    chatllm = ChatOpenAI(openai_api_key=api_key, temperature=0.7)

    # Define a dictionary with terms and their classifications
    classification_dict = {
        'Ashwagandha': 'Medical Plant',
        'Triphala': 'Ingredient',
        'Neem': 'Medical Plant',
        'Pitta': 'Symptom',
        'Vata': 'Symptom',
        'Kapha': 'Symptom',
        'Diabetes': 'Disease',
        'Jwara': 'Disease',
        'Rakta': 'Ingredient',
        'Svedana': 'Treatment'
    }

    # Initialize the session state for conversation flow
    if 'flowmessages' not in st.session_state:
        st.session_state['flowmessages'] = [
            SystemMessage(content="You are an Ayurveda assistant. Please provide definitions and classifications for Ayurveda terms.")
        ]

    # Function to classify a term using the LLM
    def classify_term_with_llm(term):
        st.session_state['flowmessages'].append(HumanMessage(content=f"What does '{term}' mean in Ayurveda?"))
        answer = chatllm.invoke(st.session_state['flowmessages'])
        return answer.content

    # Function to classify a term using the predefined dictionary
    def classify_term(term):
        return classification_dict.get(term.strip(), "Term not found in the classification.")

    # Streamlit input for the user to ask for a term meaning or classification
    term_input = st.text_input("Enter an Ayurveda term to classify or learn its meaning:", key="term_input")
    submit_classify = st.button("Classify Term")
    

    # If 'Classify Term' button is clicked, display the classification
    if submit_classify and term_input:
        classification = classify_term(term_input)
        st.subheader("Classification Result:")
        st.write(classification)

  
