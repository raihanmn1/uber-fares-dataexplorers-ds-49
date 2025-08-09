import streamlit as st
import streamlit.components.v1 as stc
import pickle
import folium
from streamlit_folium import st_folium
import math
import pytz
from datetime import datetime
import numpy as np
import pandas as pd

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
    if "predicted_fare" not in st.session_state:
        st.session_state.predicted_fare = None
    
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
        st.session_state.just_reset = True
        st.session_state.predicted_fare = None 
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
        
    # Hitung jarak asli (km) dan simpan di session state
    if st.session_state.pickup_coords and st.session_state.dropoff_coords:
        jarak_km = haversine(st.session_state.pickup_coords, st.session_state.dropoff_coords)
        st.session_state.distance = jarak_km
        st.success(f"Jarak: {jarak_km:.2f} km")
        distance_log = np.log1p(jarak_km)  # log transform untuk model input
    else:
        distance_log = 0

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
    if st.session_state.distance is not None and st.session_state.passenger_count is not None:
        if st.button("Predict Fare"):
            pickup_longitude = st.session_state.pickup_coords[1] if st.session_state.pickup_coords else 0.0
            pickup_latitude = st.session_state.pickup_coords[0] if st.session_state.pickup_coords else 0.0
            dropoff_longitude = st.session_state.dropoff_coords[1] if st.session_state.dropoff_coords else 0.0
            dropoff_latitude = st.session_state.dropoff_coords[0] if st.session_state.dropoff_coords else 0.0
            passenger_count = st.session_state.passenger_count
            year = st.session_state.year
            month = st.session_state.month
            day = st.session_state.day
            hour = st.session_state.hour
            distance = st.session_state.distance if st.session_state.distance else 0.0
            pickup_season_Spring = st.session_state.pickup_season_Spring
            pickup_season_Summer = st.session_state.pickup_season_Summer
            pickup_season_Winter = st.session_state.pickup_season_Winter
            pickup_period_Evening = st.session_state.pickup_period_Evening
            pickup_period_Morning = st.session_state.pickup_period_Morning
            pickup_period_Night = st.session_state.pickup_period_Night
            
            features = [
                pickup_longitude,
                pickup_latitude,
                dropoff_longitude,
                dropoff_latitude,
                passenger_count,
                year,
                month,
                day,
                hour,
                distance_log,
                pickup_season_Spring,
                pickup_season_Summer,
                pickup_season_Winter,
                pickup_period_Evening,
                pickup_period_Morning,
                pickup_period_Night,
                
            ]

            st.write("Features used for prediction:", features)  # debug print fitur

            fare_pred = predict(*features)
            st.session_state.predicted_fare = fare_pred

    # Tampilkan hasil prediksi jika ada
    if st.session_state.predicted_fare is not None:
        st.success(f"Predicted Uber Fare: ${st.session_state.predicted_fare:.2f}")

# Fungsi prediksi
def predict(pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude,
            passenger_count, year, month, day, hour, distance_log,
            pickup_season_Spring, pickup_season_Summer, pickup_season_Winter,
            pickup_period_Evening, pickup_period_Morning, pickup_period_Night): # << Tambahin distance_log disini

    features = [[
        pickup_longitude,
        pickup_latitude,
        dropoff_longitude,
        dropoff_latitude,
        passenger_count,
        year,
        month,
        day,
        hour,
        distance_log,
        pickup_season_Spring,
        pickup_season_Summer,
        pickup_season_Winter,
        pickup_period_Evening,
        pickup_period_Morning,
        pickup_period_Night
        # Tambahin distance_log disini
    ]]

    pred_log = LightGBM_Regression_Model.predict(features)
    pred_fare = np.expm1(pred_log)  # balik dari log fare ke asli
    return pred_fare[0]

if __name__ == "__main__":

    main()



































