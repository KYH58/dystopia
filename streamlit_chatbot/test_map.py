import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("Folium Map Test")

# Create a simple map centered at some coords
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)  # NYC coords
folium.Marker([40.7128, -74.0060], tooltip="New York City").add_to(m)

# Display the map
st_data = st_folium(m, width=700, height=500)
