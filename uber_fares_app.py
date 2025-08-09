import streamlit as st
import streamlit.components.v1 as stc
import pickle
import folium
from streamlit_folium import st_folium

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

        # --- PETA ---
    st.markdown("### Pilih Titik Pickup & Dropoff di Peta")
    
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)
    m.add_child(folium.LatLngPopup())  # tampilkan koordinat saat diklik
    
    map_data = st_folium(m, width=700, height=500)

    # State untuk koordinat
    if "pickup_coords" not in st.session_state:
        st.session_state.pickup_coords = None
    if "dropoff_coords" not in st.session_state:
        st.session_state.dropoff_coords = None

    if map_data and map_data["last_clicked"]:
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]

        # Klik pertama untuk pickup, kedua untuk dropoff
        if st.session_state.pickup_coords is None:
            st.session_state.pickup_coords = (lat, lon)
            st.success(f"Pickup point: {lat:.6f}, {lon:.6f}")
        elif st.session_state.dropoff_coords is None:
            st.session_state.dropoff_coords = (lat, lon)
            st.success(f"Dropoff point: {lat:.6f}, {lon:.6f}")

    st.write("Pickup:", st.session_state.pickup_coords)
    st.write("Dropoff:", st.session_state.dropoff_coords)

    if st.button("Reset Titik"):
        st.session_state.pickup_coords = None
        st.session_state.dropoff_coords = None
    
    # Structure
    left, right = st.columns((2,2))
    
    

    #If button is clilcked
    pass

def predict(gender, married, dependent, education, self_employed, applicant_income, coApplicant_income
                         ,loan_amount, loan_amount_term, credit_history, property_area):
    
    #Making prediction
    pass

if __name__ == "__main__":

    main()


