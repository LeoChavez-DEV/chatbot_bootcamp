import os
import requests

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = "meta-llama/Llama-3.1-8B-Instruct"

def responder_hf(messages, temperature=0.7):

    if not HF_API_KEY:
        return "No hay clave de HuggingFace configurada."

    # Convertir historial al formato del nuevo API
    convertidos = []
    for m in messages:
        if m.type == "human":
            convertidos.append({"role": "user", "content": m.content})
        else:
            convertidos.append({"role": "assistant", "content": m.content})

    url = "https://router.huggingface.co/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": HF_MODEL,
        "messages": convertidos,
        "temperature": temperature,
        "max_tokens": 256
    }

    resp = requests.post(url, headers=headers, json=payload)

    if resp.status_code != 200:
        return f"Error HF API: {resp.status_code} — {resp.text}"

    data = resp.json()

    try:
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error procesando respuesta HF: {e} — {data}"
