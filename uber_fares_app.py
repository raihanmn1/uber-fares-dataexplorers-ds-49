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
                <h1 style="color:#fff;text-align:center">Loan Eligibility Prediction App</h1> 
                <h4 style="color:#fff;text-align:center">Made for: Credit Team</h4> 
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

    # Simpan waktu sekali saja (timezone New York)
    if "current_datetime" not in st.session_state:
        tz_ny = pytz.timezone("America/New_York")
        ny_time = datetime.now(tz_ny)
        st.session_state.current_datetime = ny_time
        st.session_state.year = ny_time.year
        st.session_state.month = ny_time.month
        st.session_state.day = ny_time.day
        st.session_state.hour = ny_time.hour
        st.session_state.minute = ny_time.minute
        
    # Tombol reset di atas, supaya langsung kosong sebelum baca klik baru
    if st.button("Reset"):
        st.session_state.pickup_coords = None
        st.session_state.dropoff_coords = None
        st.session_state.distance = None
        st.session_state.just_reset = True  # flag reset
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
        #If button is clilcked
    pass

def predict(gender, married, dependent, education, self_employed, applicant_income, coApplicant_income
                         ,loan_amount, loan_amount_term, credit_history, property_area):
    
    #Making prediction
    pass

if __name__ == "__main__":

    main()





















