import streamlit as st
import requests

st.title("Medical Chatbot 🩺")

# Initialize session state
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}
if 'history' not in st.session_state:
    st.session_state.history = []

# Sidebar: User Info collection
with st.sidebar:
    st.header("📝 User Information")

    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    id_number = st.text_input("ID (9-digit)")
    gender = st.selectbox("Gender", ["Male", "Female"])
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
    hmo_name = st.selectbox("HMO", ["כללית", "מאוחדת", "מכבי"])
    hmo_card_number = st.text_input("HMO Card Number (9-digit)")
    insurance_tier = st.selectbox("Insurance Tier", ["זהב", "כסף", "ארד"])

    if st.button("Confirm & Save User Info"):
        st.session_state.user_info = {
            "first_name": first_name,
            "last_name": last_name,
            "id": id_number,
            "gender": gender,
            "age": age,
            "hmo_name": hmo_name,
            "hmo_card_number": hmo_card_number,
            "insurance_tier": insurance_tier
        }
        st.success("User information saved!")

# Main chat interface
st.header("💬 Chat")

question = st.text_input("Your question:")

if st.button("Ask"):
    if not st.session_state.user_info:
        st.error("⚠️ Please complete your user information first.")
    else:
        payload = {
            "user_info": st.session_state.user_info,
            "history": st.session_state.history,
            "question": question
        }

        response = requests.post("http://localhost:8000/chat", json=payload)

        if response.ok:
            answer = response.json()["response"]
            st.session_state.history.append({"question": question, "answer": answer})
            st.write(f"**Chatbot:** {answer}")
        else:
            st.error("Error in chatbot response")

# Display chat history clearly
if st.session_state.history:
    st.subheader("Conversation History:")
    for chat in reversed(st.session_state.history):
        st.write(f"**You:** {chat['question']}")
        st.write(f"**Chatbot:** {chat['answer']}")