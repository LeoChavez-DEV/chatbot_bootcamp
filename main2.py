import streamlit as st
import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

st.set_page_config(page_title="TIP_CHATBOT", layout="wide")
st.title("TIP_CHATBOT")

modelo = st.sidebar.selectbox("Modelo a usar:", ["gemini", "Llama-3.1"])

temperatura = st.sidebar.slider(
    "Temperatura",
    min_value=0.0,
    max_value=1.0,
    value=0.0,
    step=0.1
)

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for msg in st.session_state.mensajes:
    role = "assistant" if isinstance(msg, AIMessage) else "user"
    with st.chat_message(role):
        st.markdown(msg.content)

pregunta = st.chat_input("Escribe tu mensaje:")

if pregunta:

    st.session_state.mensajes.append(HumanMessage(content=pregunta))

    with st.chat_message("user"):
        st.markdown(pregunta)

    try:

        if modelo == "gemini":
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=temperatura
            )
            respuesta = llm.invoke(st.session_state.mensajes)
            texto = respuesta.content

        elif modelo == "Llama-3.1":
            from hf_model import responder_hf
            texto = responder_hf(st.session_state.mensajes, temperatura)

        else:
            texto = "Modelo no soportado."

    except Exception as e:
        texto = f"Error ejecutando modelo: {e}"

    with st.chat_message("assistant"):
        st.markdown(texto)

    st.session_state.mensajes.append(AIMessage(content=texto))
