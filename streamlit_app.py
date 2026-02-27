import streamlit as st
import requests
import base64

BACKEND_URL = "https://titanic-chatbot-n2id.onrender.com/ask"

st.set_page_config(page_title="Titanic Chatbot", layout="wide")

st.title("🚢 Titanic Dataset Chat Agent")

st.write("Ask questions about the Titanic passengers!")

question = st.text_input(
    "Enter your question:",
    placeholder="e.g. What percentage of passengers were male?"
)

if st.button("Ask"):
    if question:
        with st.spinner("Thinking..."):
            response = requests.post(
                BACKEND_URL,
                json={"question": question}
            )

            data = response.json()

            st.subheader("📊 Answer")
            st.write(data["answer"])

            if data["plot"]:
                st.subheader("📈 Visualization")
                image_bytes = base64.b64decode(data["plot"])
                st.image(image_bytes)
    else:
        st.warning("Please enter a question.")