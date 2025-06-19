import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="centered", page_title="Freight Rate Calculator")
st.title("📦 Freight Rate Netback Calculator")
st.write("Upload a freight rate CSV file to begin and select the specifications below to calculate the netback.")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your Freight Rate CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        required_freight_column = 'Rate 1st Half of Month'

        if required_freight_column not in df.columns:
            raise ValueError(
                f"Required freight rate column '{required_freight_column}' not found in the uploaded CSV file. "
                f"Ensure the column name is correct (case-sensitive) and free of extra spaces. "
                f"Available columns: {', '.join(df.columns)}"
            )

        df[required_freight_column] = pd.to_numeric(df[required_freight_column], errors='coerce')

    except ValueError as ve:
        st.error(f"Data Processing Error: {ve}")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred while reading or processing the CSV file: {e}")
        st.stop()
else:
    st.info("📂 Please upload a CSV file to proceed.")
    st.stop()

# --- Select Specifications ---
st.header("Select Specifications")

required_unit_column = 'Unit'
required_destination_port_column = 'Destination Port'
required_country_column = 'Country'

try:
    if required_unit_column not in df.columns:
        raise ValueError(f"Required column '{required_unit_column}' not found. Columns: {', '.join(df.columns)}")
    units = df[required_unit_column].unique().tolist()

    if required_destination_port_column not in df.columns:
        raise ValueError(f"Required column '{required_destination_port_column}' not found.")
    
    if required_country_column not in df.columns:
        raise ValueError(f"Required column '{required_country_column}' not found.")
    countries = df[required_country_column].unique().tolist()

except ValueError as ve:
    st.error(f"Dropdown Data Error: {ve}")
    st.stop()
except Exception as e:
    st.error(f"An error occurred while preparing dropdown data: {e}")
    st.stop()

# --- Dropdowns ---
selected_country = st.selectbox(f"Select {required_country_column}", countries)

filtered_ports_df = df[df[required_country_column] == selected_country]
destination_ports_for_country = sorted(filtered_ports_df[required_destination_port_column].unique().tolist())
selected_destination_port = st.selectbox(f"Select {required_destination_port_column}", destination_ports_for_country)

selected_unit = st.selectbox(f"Select {required_unit_column}", sorted(units))

# --- Freight Rate ---
st.header("Freight Rate Information")

filtered_df = df[
    (df[required_unit_column] == selected_unit) &
    (df[required_destination_port_column] == selected_destination_port) &
    (df[required_country_column] == selected_country)
]

freight_rate = None
if not filtered_df.empty:
    potential_freight_rate = filtered_df[required_freight_column].iloc[0]

    if not pd.isna(potential_freight_rate):
        freight_rate = potential_freight_rate
        st.success(f"**Freight Rate ({required_freight_column}):** ${freight_rate:,.2f}")
    else:
        st.warning(f"No valid freight rate found (or rate is non-numeric) for the selected combination.")
else:
    st.warning("No freight rate data found for the selected combination.")

# --- Netback Calculation ---
st.header("Netback Calculation")

if freight_rate is not None:
    cif = st.number_input("Enter CIF (Cost, Insurance, Freight) in Dollars ($)", min_value=0.0, format="%.2f")

    local_rate_default = 0.02
    local_rate = st.number_input("Enter Local Rate", min_value=0.0, value=local_rate_default, format="%.4f")

    divisor = 23000.0

    if cif > 0:
        netback = cif - (freight_rate / divisor) - local_rate
        st.success(f"**Calculated Netback:** ${netback:,.2f}")
    else:
        st.info("Enter a CIF value greater than 0 to calculate netback.")
else:
    st.info("Select a valid combination of Unit, Destination Port, and Country to proceed.")

# --- UI Styling ---
st.markdown("""
<style>
    .st-emotion-cache-h4xj66 {
        padding-left: 2rem;
        padding-right: 2rem;
    }
    .st-emotion-cache-lckq4l {
        font-family: "Inter", sans-serif;
    }
    .stButton > button {
        border-radius: 0.5rem;
        border: 1px solid #4CAF50;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #4CAF50;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    .stTextInput>div>div>input {
        border-radius: 0.5rem;
        padding: 0.5rem;
    }
    .stSelectbox>div>div>div {
        border-radius: 0.5rem;
    }
    .css-1ht1j85 {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)
