import whereami
import streamlit as st
import os
import stripe
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage

# Funciones MySQL
from db_mysql import (
    create_user,
    authenticate_user,
    get_credits,
    set_credits,
    create_transaction
)

load_dotenv()

# Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
APP_URL = os.getenv("APP_URL", "http://localhost:8501")

# ============================================
# SESIÓN
# ============================================

def start_session(username):
    st.session_state["username"] = username

def end_session():
    if "username" in st.session_state:
        del st.session_state["username"]

def is_logged():
    return "username" in st.session_state


# ============================================
# STREAMLIT CONFIG
# ============================================

st.set_page_config(page_title="TIP_CHATBOT", layout="wide")
st.title("TIP_CHATBOT ☠️")
st.markdown("Chatbot con login + créditos + Stripe Checkout.")


# ============================================
# TIENDA / CHECKOUT
# ============================================

def create_checkout_session(username, credits_to_add, price_cents):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"Pack {credits_to_add} créditos TIP_CHATBOT"},
                "unit_amount": price_cents,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=f"{APP_URL}/?checkout_success=1&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{APP_URL}/?checkout_canceled=1",
        metadata={
            "username": username,
            "credits": str(credits_to_add)
        }
    )

    # Guardar transacción en DB como pending
    create_transaction(
        username=username,
        stripe_session_id=session.id,
        credits=credits_to_add,
        amount_cents=price_cents,
        currency="usd",
        status="pending"
    )

    return session


# ============================================
# SIDEBAR: LOGIN / REGISTRO / TIENDA
# ============================================

with st.sidebar:
    st.header("🧾 Cuenta")

    if not is_logged():
        modo = st.radio("Acción", ["Iniciar sesión", "Registrarse"])

        if modo == "Registrarse":
            new_user = st.text_input("Nuevo usuario")
            new_pw = st.text_input("Contraseña nueva", type="password")

            if st.button("Crear cuenta"):
                if create_user(new_user, new_pw):
                    st.success("Cuenta creada. Ahora inicia sesión.")
                else:
                    st.error("Ese usuario ya existe.")

        else:
            user = st.text_input("Usuario")
            pw = st.text_input("Contraseña", type="password")

            if st.button("Entrar"):
                if authenticate_user(user, pw):
                    start_session(user)
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

    else:
        st.success(f"Sesión iniciada como **{st.session_state.username}**")
        creditos = get_credits(st.session_state.username)
        st.markdown(f"**Créditos disponibles:** {creditos}")

        # TIENDA
        st.subheader("Comprar créditos")

        opcion = st.selectbox("Pack:", ["5 créditos - $3", "10 créditos - $5", "25 créditos - $12"])

        if opcion == "5 créditos - $3":
            credits_pack = 5
            price_cents = 300
        elif opcion == "10 créditos - $5":
            credits_pack = 10
            price_cents = 500
        else:
            credits_pack = 25
            price_cents = 1200

        if st.button("Comprar ahora 💳"):
            session = create_checkout_session(st.session_state.username, credits_pack, price_cents)
            st.markdown(f"[Haz clic aquí para pagar con Stripe]({session.url})", unsafe_allow_html=True)

        if st.button("Cerrar sesión"):
            end_session()
            st.rerun()


# ============================================
# CHATBOT
# ============================================

if is_logged():

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    st.subheader("💬 Chat")

    for msg in st.session_state.mensajes:
        role = "assistant" if isinstance(msg, AIMessage) else "user"
        with st.chat_message(role):
            st.markdown(msg.content)

    pregunta = st.chat_input("Escribe tu mensaje:")

    if pregunta:

        creditos_actuales = get_credits(st.session_state.username)

        if creditos_actuales <= 0:
            st.error("No tienes créditos disponibles. Compra más en la tienda.")
        else:
            st.session_state.mensajes.append(HumanMessage(content=pregunta))
            with st.chat_message("user"):
                st.markdown(pregunta)

            try:
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    temperature=0.3
                )
                respuesta = llm.invoke(st.session_state.mensajes)
                texto = respuesta.content if hasattr(respuesta, "content") else str(respuesta)
            except Exception as e:
                texto = f"Error llamando al modelo: {e}"

            with st.chat_message("assistant"):
                st.markdown(texto)

            st.session_state.mensajes.append(AIMessage(content=texto))

            # Descontar 1 crédito
            set_credits(st.session_state.username, creditos_actuales - 1)

            st.rerun()

else:
    st.info("Inicia sesión para usar el chatbot.")
