import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

# Modelos
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import OllamaLLM

load_dotenv()

st.set_page_config(page_title="TIP_CHATBOT 2", layout="wide")
st.title("TIP_CHATBOT ☠️")
with st.sidebar:
    st.header("⚙️ Configuración del modelo")

    modelo = st.selectbox(
        "Modelo a usar:",
        ["gemini-2.5-flash", "tinyllama"]
    )

    temperatura = st.slider(
        "Temperatura:",
        0.0, 1.0, 0.2, step=0.05
    )

def load_model():
    if modelo == "gemini-2.5-flash":
        return ChatGoogleGenerativeAI(
            model=modelo,
            temperature=temperatura
        )
    else:
        return OllamaLLM(
            model="tinyllama"
        )

llm = load_model()

if "mensajes2" not in st.session_state:
    st.session_state.mensajes2 = []

st.subheader("💬 Chat")

# Render historial
for msg in st.session_state.mensajes2:
    role = "assistant" if isinstance(msg, AIMessage) else "user"
    with st.chat_message(role):
        st.markdown(msg.content)

pregunta = st.chat_input("Escribe tu mensaje:")

if pregunta:
    st.session_state.mensajes2.append(HumanMessage(content=pregunta))
    with st.chat_message("user"):
        st.markdown(pregunta)

    try:
        respuesta = llm.invoke(st.session_state.mensajes2)
        texto = (
            respuesta.content 
            if hasattr(respuesta, "content")
            else str(respuesta)
        )
    except Exception as e:
        texto = f"Error: {e}"

    # Mostrar respuesta
    with st.chat_message("assistant"):
        st.markdown(texto)

    st.session_state.mensajes2.append(AIMessage(content=texto))
