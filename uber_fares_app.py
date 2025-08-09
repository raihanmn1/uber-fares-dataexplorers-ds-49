import streamlit as st
import streamlit.components.v1 as stc
import pickle
import folium
from streamlit_folium import st_folium
import math
import pytz
from datetime import datetime

with open('LightGBM_Regression_Model.pkl', 'rb') as file:
    LightGBM_Regression_Model = pickle.load(file)

html_temp = """<div style="background-color:#000;padding:10px;border-radius:10px">
                <h1 style="color:#fff;text-align:center">Uber Fares Prediction App</h1> 
                <h4 style="color:#fff;text-align:center">Made by: Data Explorers Team</h4> 
                """

desc_temp = """ ### Uber Fares Prediction App 
                This app is used to predict Uber fares.
                
                #### Data Source
                Kaggle: Link <Masukkan Link>
                """

def main():
    stc.html(html_temp)
    menu = ["Home", "Uber Fares Prediction"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")
        st.markdown(desc_temp, unsafe_allow_html=True)
    elif choice == "Uber Fares Prediction":
        run_ml_app()

def run_ml_app():
    design = """<div style="padding:15px;">
                    <h1 style="color:#fff">Uber Fares Prediction</h1>
                </div
             """
    st.markdown(design, unsafe_allow_html=True)

    # --- Fungsi Haversine ---
    def haversine(coord1, coord2):
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        R = 6371.0  # km
    
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
    
        a = math.sin(delta_phi / 2) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    # --- Inisialisasi session state ---
    if "pickup_coords" not in st.session_state:
        st.session_state.pickup_coords = None
    if "dropoff_coords" not in st.session_state:
        st.session_state.dropoff_coords = None
    if "distance" not in st.session_state:
        st.session_state.distance = None
    if "passenger_count" not in st.session_state:  # inisialisasi awal
        st.session_state.passenger_count = 1
    
    # --- PETA ---
    st.markdown("### Pilih Titik Pickup & Dropoff di Peta")

    # --- Fungsi untuk set datetime New York ---
    def set_ny_datetime():
        tz_ny = pytz.timezone("America/New_York")
        ny_time = datetime.now(tz_ny)
        st.session_state.current_datetime = ny_time
        st.session_state.year = ny_time.year
        st.session_state.month = ny_time.month
        st.session_state.day = ny_time.day
        st.session_state.hour = ny_time.hour
        st.session_state.minute = ny_time.minute

    # Set datetime pertama kali load
    if "current_datetime" not in st.session_state:
        set_ny_datetime()

    # --- Tentukan Season & Period dari datetime ---
    def get_season(month):
        if month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        elif month in [9, 10, 11]:
            return "Fall"
        else:
            return "Winter"
    
    def get_period(hour):
        if 5 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 17:
            return "Afternoon"
        elif 17 <= hour < 21:
            return "Evening"
        else:
            return "Night"
    
    season = get_season(st.session_state.month)
    period = get_period(st.session_state.hour)
    
    st.session_state.pickup_season_Spring = 1 if season == "Spring" else 0
    st.session_state.pickup_season_Summer = 1 if season == "Summer" else 0
    st.session_state.pickup_season_Winter = 1 if season == "Winter" else 0
    st.session_state.pickup_period_Evening = 1 if period == "Evening" else 0
    st.session_state.pickup_period_Morning = 1 if period == "Morning" else 0
    st.session_state.pickup_period_Night = 1 if period == "Night" else 0
    
    # Tombol reset di atas, supaya langsung kosong sebelum baca klik baru
    if st.button("Reset"):
        st.session_state.pickup_coords = None
        st.session_state.dropoff_coords = None
        st.session_state.distance = None
        st.session_state.just_reset = True  # flag reset
        set_ny_datetime()
    else:
        st.session_state.just_reset = False
    
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)
    m.add_child(folium.LatLngPopup())
    
    map_data = st_folium(m, width=700, height=500)
    
    # Hanya proses klik jika tidak baru reset
    if not st.session_state.just_reset and map_data and map_data["last_clicked"]:
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
    
        if st.session_state.pickup_coords is None:
            st.session_state.pickup_coords = (lat, lon)
            st.success(f"Pickup point: {lat:.6f}, {lon:.6f}")
        elif st.session_state.dropoff_coords is None:
            st.session_state.dropoff_coords = (lat, lon)
            st.success(f"Dropoff point: {lat:.6f}, {lon:.6f}")

    # --- Hitung jarak dan simpan ke session state ---
    if st.session_state.pickup_coords and st.session_state.dropoff_coords:
        jarak_km = haversine(st.session_state.pickup_coords,
                             st.session_state.dropoff_coords)
        st.session_state.distance = jarak_km
        st.success(f"Jarak: {jarak_km:.2f} km")

    # --- Input Passenger Count (selalu muncul dari awal) ---
    st.session_state.passenger_count = st.number_input(
        "Passenger Count",
        min_value=1,
        max_value=6,
        value=st.session_state.passenger_count,
        step=1
    )
    
    # --- Tampilkan data ---
    st.write("Datetime (New York):", st.session_state.current_datetime)
    st.write("Pickup:", st.session_state.pickup_coords)
    st.write("Dropoff:", st.session_state.dropoff_coords)
    st.write("Distance (km):", st.session_state.distance)
    st.write("Passenger Count:", st.session_state.passenger_count)
    st.write("Season:", season)
    st.write("Period:", period)
    
    #If button is clilcked
    pass

def predict(gender, married, dependent, education, self_employed, applicant_income, coApplicant_income
                         ,loan_amount, loan_amount_term, credit_history, property_area):
    
    #Making prediction
    pass

if __name__ == "__main__":

    main()


























