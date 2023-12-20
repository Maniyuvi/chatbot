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
import user_info as UserInputs
from streamlit_lottie import st_lottie_spinner

load_dotenv()

#load Animation
typing_animation_json = render_animation()

# st.markdown(
#     """
#         <style>
#         button {
#             height: 10px;
#             padding-top: 0px !important;
#             padding-bottom: 0px !important;
#         }
#         </style>
#         """,
#             unsafe_allow_html=True,
# )

st.title("Chat with AI 💬")
st.write("I have information about the content below. You can ask me questions about it.")

product_type = st.sidebar.selectbox("Product", UserInputs.getProductList())

user_input = {
    "product_type": product_type
}

st.session_state["user_input"] = user_input

if 'responses' not in st.session_state:
    st.session_state['responses'] = ["How can I assist you?"]

if 'requests' not in st.session_state:
    st.session_state['requests'] = []

if 'initialPageLoad' not in st.session_state:
    st.session_state['initialPageLoad'] = True

if 'prev_peoduct_select' not in st.session_state:
     st.session_state['prev_peoduct_select'] = 'Agrid'

llm = ChatOpenAI(temperature=0, model='gpt-3.5-turbo') ## find at platform.openai.com

if 'buffer_memory' not in st.session_state:
            st.session_state.buffer_memory=ConversationBufferWindowMemory(k=3,return_messages=True)

# Answer the question as truthfully as possible using the provided context, 
# and if the answer is not contained within the text below, say 'I don't know'

system_msg_template = SystemMessagePromptTemplate.from_template(template="""The following is a friendly conversation between a human and an AI. 
        The AI is talkative and provides lots of specific details from its context. 
        If the AI does not know the answer to a question, it truthfully says it does
        not know.""")

human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")

prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

conversation = ConversationChain(memory=st.session_state.buffer_memory, prompt=prompt_template, llm=llm, verbose=True)


# container for chat history
response_container = st.container()
# container for text box
textcontainer = st.container()
if(st.session_state.initialPageLoad or st.session_state.prev_peoduct_select != product_type ):
    with st_lottie_spinner(typing_animation_json, height=50, width= 50, speed=3):
        refined_query = f"""summarize the document and genrate some meaningfull qustion based on the document in {product_type}"""
        context = find_match(refined_query)
        response = conversation.predict(input=f"Context:\n {context} \n\n Query:\n{refined_query}")
        st.session_state.requests.append("Summary of the "+product_type+ " Product")
        st.session_state.responses.append(response) 
        st.session_state.initialPageLoad = False
        st.session_state.prev_peoduct_select = product_type

with textcontainer:
    st.session_state.initialPageLoad = False
    query = st.chat_input(placeholder="Say something ... ", key="input")
    if query:
        print('query :::', query)
        conversation_string = get_conversation_string()
        with st_lottie_spinner(typing_animation_json, height=50, width= 50, speed=3, reverse=True ):
            refined_query = query_refiner(conversation_string, query)
            print('refined_query :::::', refined_query)
            # st.subheader("Refined Query:")
            # st.write(refined_query)
            context = find_match(refined_query)
            response = conversation.predict(input=f"Context:\n {context} \n\n Query:\n{query}")
            st.session_state.requests.append(query)
            st.session_state.responses.append(response) 
with response_container:
    st.session_state.initialPageLoad = False
    if st.session_state['responses']:
        for i in range(len(st.session_state['responses'])):
            message(st.session_state['responses'][i],key=str(i))
            if i < len(st.session_state['requests']):
                message(st.session_state["requests"][i], is_user=True,key=str(i)+ '_user')

