import streamlit as st
import requests

st.title("🏥 ORL IA - CLINICAL RISK SYSTEM")

age = st.slider("Age", 0, 100, 50)
larynx = st.selectbox("Larynx", [0, 1])
parotide = st.selectbox("Parotide", [0, 1])
ethmoide = st.selectbox("Ethmoide", [0, 1])

if st.button("Predict"):
    res = requests.post(
        "http://orl-api:8000/predict",
        json={
            "age": age,
            "larynx": larynx,
            "parotide": parotide,
            "ethmoide": ethmoide
        }
    )
    st.write(res.json())