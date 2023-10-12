import openai
import streamlit as st
from utils import *

# Set up your OpenAI API key
api_key = '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'

# Initialize the OpenAI client
openai.api_key = api_key

# Define a function for your chatbot
def chat_with_bot(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text

# Streamlit UI
st.title("OpenAI Chatbot")
user_role = st.selectbox("Select User/Role", ["User", "Admin", "Support","Developer"])

# Output format dropdown
output_format = st.selectbox("Select Output Format", ["Text", "JSON", "Code Snippet"])
user_input = st.text_input(f"Enter {user_role} input:")

if st.button("Chat"):
    output_prompt = f"{user_role}: {user_input} (Format: {output_format})"  # Include output format in the prompt
    response = prompt_genration(output_prompt)
    if output_format == "Text":
        st.write("Chatbot: " + response)
    elif output_format == "JSON":
        st.write("Chatbot Response (JSON):")
        st.json(response)
    elif output_format == "Code Snippet":
        st.write("Chatbot Code Snippet:")
        st.code(response, language="python")  # You can specify the appropriate programming language here