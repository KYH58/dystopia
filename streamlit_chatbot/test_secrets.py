import streamlit as st

# Read secrets
opencage_key = st.secrets["OPENCAGE_KEY"]
ors_key = st.secrets["ORS_API_KEY"]
google_api_key = st.secrets["GOOGLE_API_KEY"]

st.title("🔐 Streamlit Secrets Test")

st.write("Your OpenCage API Key:")
st.code(opencage_key)

st.write("Your OpenRouteService API Key:")
st.code(ors_key)

st.write("Your Google API Key:")
st.code(google_api_key)