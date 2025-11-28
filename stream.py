from dotenv import load_dotenv
load_dotenv()
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama.llms import OllamaLLM

# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature = 0.7)
llm = OllamaLLM(model="tinyllama")

# pregunta = input("Pregunta? :")
pregunta = input("que puedo hacer por ti? :")
# respuesta = llm.invoke(pregunta)
respuesta = llm.invoke(pregunta)
# print("Respuesta: ", respuesta.content)
print("Respuesta: ", respuesta)