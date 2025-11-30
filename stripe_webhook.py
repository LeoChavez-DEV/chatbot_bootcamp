from flask import Flask, request, jsonify
import stripe
import os
from dotenv import load_dotenv

from db_mysql import set_credits, update_transaction_status, get_connection

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook_received():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        return jsonify({"error": "Invalid signature"}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        metadata = session.get("metadata", {})
        username = metadata.get("username")

        if not username:
            print("⚠️  No se encontró username en metadata, ignorando evento...")
            return "ok", 200

        credits = int(session["metadata"]["credits"])
        session_id = session["id"]

        update_transaction_status(session_id, "completed")

        # sumar créditos
        con = get_connection()
        cur = con.cursor()
        cur.execute("UPDATE users SET credits = credits + %s WHERE username=%s", (credits, username))
        con.commit()
        con.close()

    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(port=4242)