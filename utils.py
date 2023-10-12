from sentence_transformers import SentenceTransformer
import pinecone
import openai
import streamlit as st
import json

#Streamlit Run
openai.api_key = st.secrets["OPENAI_API_KEY"]

embed_model = "text-embedding-ada-002"
pinecone_api_key = st.secrets["PINECONE_API_KEY"]
pinecone_environment = st.secrets["PINECONE_ENVIRONMENT"]
pinecone_index = st.secrets["PINECONE_INDEX"]


pinecone.init(api_key=pinecone_api_key,
              environment=pinecone_environment
             )
index_name = pinecone_index
index = pinecone.Index(index_name) # index name from pinecone)


def find_match(input):
    res = openai.Embedding.create(
        input=[input],
        engine=embed_model
    )
    xq = res['data'][0]['embedding']

    result = index.query(xq, top_k=2, include_metadata=True)

    return result['matches'][0]['metadata']['text']+"\n"+result['matches'][1]['metadata']['text']

def query_refiner(conversation, query):

    response = openai.Completion.create(
    model="text-davinci-003",
    prompt = f"Given the following user query and conversation log, formulate a question that would be the most relevant to provide the user with an answer from a knowledge base.\n\nCONVERSATION LOG: \n{conversation}\n\nQuery: {query}\n\nRefined Query:",
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    # print('response ::::', response)
    refinedQueryString = response['choices'][0]['text']
    print('refinedQueryString ::::', refinedQueryString)

    finalPrompt = refinedQueryString

    if 'user_input' in st.session_state:
        user_info = st.session_state['user_input']
        role = user_info['user_role']
        user_role_other = user_info['user_role_other']
        response_type = user_info['responce_type']
        with_example = user_info['with_example']

        if(role != 'None' and role != 'Others'):
            roleString = f"You are a {role}."
            finalPrompt = roleString + finalPrompt
        elif(role == 'Others' and len(user_role_other) > 1 ):
            roleString = f"You are a {user_role_other}."
            finalPrompt = roleString + finalPrompt
        
        if(response_type != "None"):
            setResponceType = f"Create a  {response_type}."
            finalPrompt = setResponceType + finalPrompt
        
        if(with_example == True or with_example == 'True'):
            addExampe = "If possible give me with some example"
            finalPrompt = finalPrompt + addExampe

    print('finalPrompt ::::', finalPrompt)

    return finalPrompt

def get_conversation_string():
    conversation_string = ""
    for i in range(len(st.session_state['responses'])-1):
        
        conversation_string += "Human: "+st.session_state['requests'][i] + "\n"
        conversation_string += "Bot: "+ st.session_state['responses'][i+1] + "\n"
    return conversation_string

def chat_complete(conversation, query):
    finalPrompt = "Drawing upon the annals of our conversion history and juxtaposing it with the present query, we aim to unlock deep insights and drive actionable outcomes. Present your inquiries, and witness a synthesis of past wisdom with current exploration."

    if 'user_input' in st.session_state:
        user_info = st.session_state['user_input']
        role = user_info['user_role']
        user_role_other = user_info['user_role_other']
        response_type = user_info['responce_type']
        with_example = user_info['with_example']

        if(role != 'None' and role != 'Others'):
            roleString = f"You are a {role}."
            finalPrompt = roleString + finalPrompt
        elif(role == 'Others' and len(user_role_other) > 1 ):
            roleString = f"You are a {user_role_other}."
            finalPrompt = roleString + finalPrompt
        
        if(response_type != "None"):
            # setResponceType = f"Please provide me with a {response_type}."
            setResponceType = f"Create a {response_type}."
            finalPrompt =  setResponceType + finalPrompt

        
        if(with_example == True or with_example == 'True'):
            addExampe = "If possible give me with some example"
            finalPrompt = finalPrompt + addExampe
        
    finalPrompt = finalPrompt + f"**CONVERSION HISTORY ARCHIVE**:{conversation}**CURRENT QUERY CONTEXT**:{query}"
    print('finalPrompt :::: String', finalPrompt)

    response = openai.Completion.create(
    model="text-davinci-003",
    prompt = finalPrompt,
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    print('response ::::', response)
    print('ans :::::', response['choices'][0]['text'])
    return response['choices'][0]['text']
    