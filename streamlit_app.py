# Loading documents from a directory with LangChain
import streamlit as st
import pinecone
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import os
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

def main():
    st.header("Chat with PDF 💬")
    # embeddings
    embeddings = OpenAIEmbeddings()

    #pinecone init
    pinecone.init(
    api_key="2d229696-dd58-4f6d-827c-b8a7523f55de",
    environment="gcp-starter"
    )
    index_name = "source-data"

    # connect to index
    index = pinecone.Index(index_name)
    # view index stats
    index.describe_index_stats()

    # Accept user questions/query
    query = st.text_input("Ask questions about your file")

    vector_store = Pinecone(index, embeddings.embed_query, "text")

    qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0), chain_type="stuff", retriever=vector_store.as_retriever())

    answer = qa.run(query)

    print('ans :::::',answer )

    st.write(answer)

if __name__ == "__main__":
    main()