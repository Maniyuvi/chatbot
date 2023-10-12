# Loading documents from a directory with LangChain
from langchain.document_loaders import DirectoryLoader
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pinecone
from langchain.vectorstores import Pinecone
import docx2txt
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from dotenv import load_dotenv

#load openai key
load_dotenv()

pinecone_api_key = st.secrets["PINECONE_API_KEY"]
pinecone_environment = st.secrets["PINECONE_ENVIRONMENT"]
pinecone_index = st.secrets["PINECONE_INDEX"]

def read_pdf(file):
  pdf_reader = PdfReader(file)
  text = ''
  for page in pdf_reader.pages:
    text += page.extract_text()
  return text


def split_docs(documents,chunk_size=1000,chunk_overlap=200):
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
  docs = text_splitter.split_text(documents)
  return docs


def text_split(raw_text):
  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, 
    chunk_overlap=200,
    length_function=len
  )
  docs = text_splitter.split_text(raw_text)

  return docs

st.header("Upload Your File 🗃️")
docx_file = st.file_uploader("Upload File",type=['txt','docx','pdf'])
submit = st.button("Upload")

if docx_file is not None and submit:
  file_details = {"Filename":docx_file.name,"FileType":docx_file.type,"FileSize":docx_file.size}
  print('file_details :::::::', file_details)

  # Check File Type
  if docx_file.type == "text/plain":
    raw_text = str(docx_file.read(),"utf-8")

  elif docx_file.type == "application/pdf":
    raw_text = read_pdf(docx_file)
        
  elif docx_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
  # Use the right file processor ( Docx,Docx2Text,etc)
    raw_text = docx2txt.process(docx_file)

  splitedText = text_split(raw_text)
  print('len of splitedText ::::', len(splitedText))

  st.write(splitedText)

  # embeddings
  embeddings = OpenAIEmbeddings()

  #pinecone init
  pinecone.init(
    api_key=pinecone_api_key,
    environment=pinecone_environment
  )
  index_name = pinecone_index

  #upload data on pinecone
  Pinecone.from_texts(splitedText, embeddings, index_name=index_name)

  st.toast('File uploaded !', icon='🎉')
  st.success('File uploaded Done!')