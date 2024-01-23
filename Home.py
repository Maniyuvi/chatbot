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
from streamlit_pills import pills

st.set_page_config(
    page_title="Softsquare AI",
    page_icon="🤖",
)
import time

load_dotenv()

#load Animation
typing_animation_json = render_animation()

st.title("Chat with AI 💬")
# st.write("I have information about the content below. You can ask me questions about it.")
# st.write("Ask me or select an option below.")


product_type = pills("Select an option below.",
                        [
                            "AGrid",
                            "Media Manager",
                            "User 360",
                            "Snap Data",
                        ],
                        index=None,
                        label_visibility="visible",
                        key="menulist1"
                    )

def buttonClick(productName):
    if st.session_state.selected_product_type_menu.lower() == productName.lower():
        st.session_state.prevent_loading = True
    else:
        st.session_state['selected_product_type_menu'] = productName
        st.session_state.prevent_loading = False


if product_type != "None" and product_type != None:

    if 'responses' not in st.session_state:
        st.session_state['responses'] = ["How can I assist you?"]

    if 'requests' not in st.session_state:
        st.session_state['requests'] = []

    if 'initialPageLoad' not in st.session_state:
        st.session_state['initialPageLoad'] = True

    if 'selected_product_type' not in st.session_state:
        st.session_state['selected_product_type'] = product_type

    if 'prevent_loading' not in st.session_state:
        st.session_state['prevent_loading'] = False

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

    if st.session_state.initialPageLoad:
        if 'selected_product_type_menu' not in st.session_state:
            st.session_state['selected_product_type_menu'] = ''

    if st.session_state.initialPageLoad or (st.session_state.selected_product_type != st.session_state.selected_product_type_menu and st.session_state.selected_product_type_menu != "None" and st.session_state.selected_product_type_menu != None and st.session_state.selected_product_type_menu != '' and st.session_state.prevent_loading != True):
        with st_lottie_spinner(typing_animation_json, height=50, width= 50, speed=3):
            productName = st.session_state.selected_product_type if st.session_state.initialPageLoad else st.session_state.selected_product_type_menu
            refined_query = f"""summarize the document and genrate some meaningfull qustion based on the document in {productName}"""
            context = find_match(refined_query)
            response = conversation.predict(input=f"Context:\n {context} \n\n Query:\n{refined_query}")
            st.session_state.requests.append("Summary of the "+productName+ " Product")
            st.session_state.responses.append(response) 
            st.session_state.initialPageLoad = False
            st.session_state.prev_peoduct_select = productName

    with textcontainer:
        st.session_state.initialPageLoad = False
        query = st.chat_input(placeholder="Say something ... ", key="input")
        if query and query == "Menu":
            try:
                button_col1, button_col2, button_col3, button_col4 = st.columns([2,3,3,4])
                button_col1.button("AGrid", on_click=buttonClick, args=["AGrid"])
                button_col2.button("Media Manager", on_click=buttonClick, args=["Media Manager"])
                button_col3.button("User 360", on_click=buttonClick, args=["User 360"])
                button_col4.button("Snap Data", on_click=buttonClick, args=["Snap Data"])
            except Exception as ex:
                print('Error :::', ex)
        elif query and query != "Menu":
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
        st.session_state.prevent_loading = True

        with response_container:
            st.session_state.initialPageLoad = False
            if st.session_state['responses']:
                for i in range(len(st.session_state['responses'])):
                    message(st.session_state['responses'][i],key=str(i))
                    if i < len(st.session_state['requests']):
                        message(st.session_state["requests"][i], is_user=True,key=str(i)+ '_user')


# st.title("Welcome")
# st.write("This is a custom AI chatbot specific for our AppExchange Products Agrid, Media Manager, User 360 and Snap Data.")