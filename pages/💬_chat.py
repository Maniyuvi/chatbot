from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
import streamlit as st
from streamlit_chat import message
from utils import *
from dotenv import load_dotenv
import predefined_user_input as UserInputs

load_dotenv()


st.title("Chat with AI 💬")

user_role_other = ''

chat_type = st.sidebar.selectbox("Chat Type", UserInputs.chatTypes())
user_role = st.sidebar.selectbox("Select User/Role", UserInputs.userRoles())
if(user_role == "Others"):
    user_role_other = st.sidebar.text_input("user/role", key="input")
responce_type = st.sidebar.selectbox("Responce Type", UserInputs.responceType())
with_example = st.sidebar.checkbox('With Example')

user_input = {
    "chat_type": chat_type,
    "user_role": user_role,
    "user_role_other": user_role_other,
    "responce_type": responce_type,
    "with_example": with_example
}
print('User Inputs :::::', user_input)

st.session_state["user_input"] = user_input
print('User Details Loaded...')



if 'responses' not in st.session_state:
    st.session_state['responses'] = ["How can I assist you?"]

if 'requests' not in st.session_state:
    st.session_state['requests'] = []

llm = ChatOpenAI(temperature=0, model='gpt-3.5-turbo') ## find at platform.openai.com

if 'buffer_memory' not in st.session_state:
            st.session_state.buffer_memory=ConversationBufferWindowMemory(k=3,return_messages=True)

system_msg_template = SystemMessagePromptTemplate.from_template(template="""Answer the question as truthfully as possible using the provided context, 
and if the answer is not contained within the text below, say 'I don't know'""")


human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")

prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

conversation = ConversationChain(memory=st.session_state.buffer_memory, prompt=prompt_template, llm=llm, verbose=True)


# container for chat history
response_container = st.container()

# container for text box
textcontainer = st.container()

#user Input
if 'user_input' in st.session_state:
    print('chat page:::',st.session_state['user_input'])

query = st.text_input("Query: ", key="input")

# if st.button("Enter"):
with textcontainer:
    if query:
        with st.spinner("typing..."):
            context = ''
            conversation_string = get_conversation_string()
            print('chat_type ::::', chat_type)
            if(chat_type == 'Docs'):
                print('Docs :::::')
                refined_query = query_refiner(conversation_string, query)
                print('refined_query :::::', refined_query)
                st.subheader("Refined Query:")
                st.write(refined_query)
                context = find_match(refined_query)
            elif(chat_type == 'General'):
                print('Genral ::::')
                context =chat_complete(conversation_string, query)
            print(context)  
            response = conversation.predict(input=f"Context:\n {context} \n\n Query:\n{query}")
        st.session_state.requests.append(query)
        st.session_state.responses.append(response) 
with response_container:
    if st.session_state['responses']:
        for i in range(len(st.session_state['responses'])):
            message(st.session_state['responses'][i],key=str(i))
            if i < len(st.session_state['requests']):
                message(st.session_state["requests"][i], is_user=True,key=str(i)+ '_user')

