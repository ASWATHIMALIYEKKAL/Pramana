# -*- coding: utf-8 -*-
"""Chatbot.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1wWrD1x9mCHWoyF6UqCGCfo77USEX6TmO
"""

import gradio as gr
from huggingface_hub import InferenceClient
from typing import List, Tuple
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util
import numpy as np
import faiss

# Initialize the InferenceClient for the Hugging Face model
client = InferenceClient("HuggingFaceH4/zephyr-7b-beta", token="")  # Replace with your actual Hugging Face API token

class AyurvedaAssistant:
    def __init__(self) -> None:
        self.documents = []
        self.embeddings = None
        self.index = None
        self.load_pdf("Charaka Samhita Sutrasthana Made Easy - Dr JV Hebbar.pdf")  # Use a relevant Ayurveda PDF file
        self.build_vector_db()

    def load_pdf(self, file_path: str) -> None:
        """Extracts text from a PDF file and stores it in the app's documents."""
        doc = fitz.open(file_path)
        self.documents = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            self.documents.append({"page": page_num + 1, "content": text})
        print("PDF processed successfully!")

    def build_vector_db(self) -> None:
        """Builds a vector database using the content of the PDF."""
        model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embeddings = model.encode([doc["content"] for doc in self.documents])
        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.index.add(np.array(self.embeddings))
        print("Vector database built successfully!")

    def search_documents(self, query: str, k: int = 3) -> List[str]:
        """Searches for relevant documents using vector similarity."""
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode([query])
        D, I = self.index.search(np.array(query_embedding), k)
        results = [self.documents[i]["content"] for i in I[0]]
        return results if results else ["No relevant documents found."]

# Initialize the application
app = AyurvedaAssistant()

def respond(
    message: str,
    history: List[Tuple[str, str]],
    system_message: str = "You are a knowledgeable Ayurveda digital assistant. Provide helpful information about Ayurvedic herbs, treatments, and patient care.",
    max_tokens: int = 100,
    temperature: float = 0.7,
    top_p: float = 0.9,
):
    messages = [{"role": "system", "content": system_message}]

    # Construct the message history for context
    for user_msg, assistant_msg in history:
        if user_msg:
            messages.append({"role": "user", "content": user_msg})
        if assistant_msg:
            messages.append({"role": "assistant", "content": assistant_msg})

    messages.append({"role": "user", "content": message})

    # Retrieve relevant Ayurvedic documents
    retrieved_docs = app.search_documents(message)
    context = "\n".join(retrieved_docs)
    messages.append({"role": "system", "content": "Relevant documents: " + context})

    response = ""
    # Get the assistant's response from the model
    for msg in client.chat_completion(
        messages,
        max_tokens=max_tokens,
        stream=True,
        temperature=temperature,
        top_p=top_p,
    ):
        token = msg.choices[0].delta.content
        response += token
        yield response

# Gradio interface for the chatbot
demo = gr.Blocks()

with demo:
    gr.Markdown("# 🌿 Ayurveda Assistant 🌱")
    gr.Markdown("Welcome! Ask me about Ayurvedic herbs, treatments, or how to manage specific symptoms.")
    gr.Markdown(
        "‼️ **Disclaimer:** This assistant offers general Ayurvedic information. Please consult a certified Ayurveda practitioner before using any treatments. ‼️"
    )

    with gr.Row():
        with gr.Column():
            chatbot = gr.ChatInterface(
                respond,
                examples=[
                    ["What herbs help with digestion according to Ayurveda?"],
                    ["How can I balance Pitta dosha?"],
                    ["What is the use of Neem in Ayurveda?"],
                    ["Can you suggest an Ayurvedic remedy for anxiety?"],
                    ["What is the role of Ashwagandha in immunity?"],
                ],
                title='Ayurveda Digital Assistant 🌱'
            )

    gr.Markdown("### 🌼 Discover More Ayurvedic Remedies!")
    gr.Markdown("Feel free to ask about any Ayurvedic treatments or herbal remedies you are curious about!")

if __name__ == "__main__":
    demo.launch()