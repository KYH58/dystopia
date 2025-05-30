import streamlit as st
import requests
import overpy
from streamlit_folium import st_folium
import folium

# API KEYS from Streamlit Secrets
OPENCAGE_KEY = st.secrets["OPENCAGE_KEY"]
ORS_KEY = st.secrets["ORS_API_KEY"]

@st.cache_data(ttl=3600)
def geocode_location(place):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={place}&key={OPENCAGE_KEY}"
    res = requests.get(url).json()
    if res.get('results'):
        coords = res['results'][0]['geometry']
        return coords['lat'], coords['lng']
    return None, None

@st.cache_data(ttl=3600)
def get_routes(lat1, lon1, lat2, lon2):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {"Authorization": ORS_KEY}
    params = {"start": f"{lon1},{lat1}", "end": f"{lon2},{lat2}"}
    res = requests.get(url, headers=headers, params=params)
    data = res.json()
    if "features" in data and data["features"]:
        coords = data['features'][0]['geometry']['coordinates']
        summary = data['features'][0]['properties']['summary']
        return coords, summary['distance'], summary['duration']
    return None, None, None

@st.cache_data(ttl=3600)
def find_nearby_restaurants(lat, lon, radius=2000):
    api = overpy.Overpass()
    query = f"""
    [out:json];
    node["amenity"~"restaurant|cafe"](around:{radius},{lat},{lon});
    out;
    """
    result = api.query(query)
    return result.nodes

def build_route_map(coords, start, end):
    m = folium.Map(location=start, zoom_start=13)
    folium.Marker(start, tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(end, tooltip="End", icon=folium.Icon(color="red")).add_to(m)
    route_latlon = [(lat, lon) for lon, lat in coords]
    folium.PolyLine(route_latlon, color="blue", weight=5, opacity=0.7).add_to(m)
    return m

def build_food_map(nodes, center):
    m = folium.Map(location=center, zoom_start=15)
    for node in nodes:
        name = node.tags.get("name", "Unnamed")
        amenity = node.tags.get("amenity", "Unknown")
        folium.Marker(
            [node.lat, node.lon],
            tooltip=f"{name} ({amenity})",
            icon=folium.Icon(color="red", icon="cutlery", prefix="fa")
        ).add_to(m)
    return m

# --- UI ---

st.set_page_config(page_title="Navigation & Food Finder", layout="wide")
st.title("🚗 Navigation & 🍽️ Food Finder")

tab1, tab2 = st.tabs(["🧭 Navigation", "🍽️ Food"])

# Initialize session_state keys
for key in ["route_result", "food_result"]:
    if key not in st.session_state:
        st.session_state[key] = None

with tab1:
    st.subheader("Find a Route")
    with st.form("route_form"):
        origin = st.text_input("Enter starting point", key="origin")
        destination = st.text_input("Enter destination", key="destination")
        submitted = st.form_submit_button("Show Route")

    if submitted:
        lat1, lon1 = geocode_location(origin)
        lat2, lon2 = geocode_location(destination)
        if not lat1 or not lat2:
            st.error("Could not geocode one or both locations.")
            st.session_state.route_result = None
        else:
            coords, dist, dur = get_routes(lat1, lon1, lat2, lon2)
            if not coords:
                st.error("Could not fetch route data.")
                st.session_state.route_result = None
            else:
                st.session_state.route_result = {
                    "coords": coords,
                    "start": (lat1, lon1),
                    "end": (lat2, lon2),
                    "distance": dist,
                    "duration": dur,
                }

    if st.session_state.route_result:
        data = st.session_state.route_result
        route_map = build_route_map(data["coords"], data["start"], data["end"])
        st_folium(route_map, width=700, height=500)
        st.success(f"Distance: {data['distance']/1000:.2f} km | Duration: {data['duration']/60:.1f} min")

with tab2:
    st.subheader("Discover Food Nearby")
    with st.form("food_form"):
        location = st.text_input("Enter location", key="food_location")
        food_type = st.text_input("Food type (optional)", key="food_type")
        radius = st.slider("Search radius (meters)", 500, 5000, 2000, step=500, key="food_radius")
        submitted = st.form_submit_button("Find Food")

    if submitted:
        lat, lon = geocode_location(location)
        if not lat:
            st.error("Could not geocode location.")
            st.session_state.food_result = None
        else:
            nodes = find_nearby_restaurants(lat, lon, radius)
            if food_type:
                ft = food_type.lower()
                nodes = [
                    node for node in nodes if
                    ft in node.tags.get("name", "").lower() or ft in node.tags.get("cuisine", "").lower()
                ]
            if not nodes:
                st.info("No food places found.")
                st.session_state.food_result = None
            else:
                st.session_state.food_result = {
                    "nodes": nodes,
                    "center": (lat, lon)
                }

    if st.session_state.food_result:
        data = st.session_state.food_result
        food_map = build_food_map(data["nodes"], data["center"])
        st_folium(food_map, width=700, height=500)
        st.info(f"Found {len(data['nodes'])} places.")

