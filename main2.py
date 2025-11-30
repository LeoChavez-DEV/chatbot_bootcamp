import streamlit as st
import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.messages import HumanMessage, AIMessage

from openai import OpenAI

load_dotenv()

st.set_page_config(page_title="TIP_CHATBOT", layout="wide")
st.title("TIP_CHATBOT")

modelo = st.sidebar.selectbox("Modelo a usar:", ["gemini", "deepseek"])

temperatura = st.sidebar.slider(
    "Temperatura",
    min_value=0.0,
    max_value=1.0,
    value=0.3,
    step=0.1
)

# Historial
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for msg in st.session_state.mensajes:
    role = "assistant" if isinstance(msg, AIMessage) else "user"
    with st.chat_message(role):
        st.markdown(msg.content)

pregunta = st.chat_input("Escribe tu mensaje:")

if pregunta:

    # Guardamos lo que dijo el usuario
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

        elif modelo == "deepseek":
            client = OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com"
            )

            msgs = []
            for m in st.session_state.mensajes:
                if isinstance(m, HumanMessage):
                    msgs.append({"role": "user", "content": m.content})
                else:
                    msgs.append({"role": "assistant", "content": m.content})

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=msgs,
                temperature=temperatura
            )

            texto = response.choices[0].message.content

        else:
            texto = "Modelo no soportado."

    except Exception as e:
        texto = f"Error ejecutando modelo: {e}"

    with st.chat_message("assistant"):
        st.markdown(texto)

    # Guardar en historial
    st.session_state.mensajes.append(AIMessage(content=texto))
