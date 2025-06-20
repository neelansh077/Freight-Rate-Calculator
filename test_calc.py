import streamlit as st
import pandas as pd
import io
import numpy as np
 
try:
    df = pd.read_csv("Sample File - Export(Sample File).csv")
 
    required_freight_column = 'Rate 1st Half of Month'
 
    if required_freight_column not in df.columns:
        raise ValueError(
            f"Required freight rate column '{required_freight_column}' not found in the CSV file. "
            f"Please ensure the column name is exact (case-sensitive) and check for any leading/trailing spaces. "
            f"Available columns are: {', '.join(df.columns)}"
        )
 
    df[required_freight_column] = pd.to_numeric(
        df[required_freight_column], errors='coerce'
    )
 
except FileNotFoundError:
    st.error("Error: 'Sample File - Export(Sample File).csv' not found. Please ensure the file is in the correct directory.")
    st.stop()
except ValueError as ve:
    st.error(f"Data Processing Error: {ve}")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred while reading or processing the CSV file: {e}")
    st.stop()
 
st.set_page_config(layout="centered", page_title="Freight Rate Calculator")
st.title("Freight Rate Netback Calculator")
st.write("Select the specifications below to find the freight rate and calculate netback.")
 
st.header("Select Specifications")
 
required_unit_column = 'Unit'
required_destination_port_column = 'Destination Port'
required_country_column = 'Country'
 
try:
    if required_unit_column not in df.columns:
        raise ValueError(f"Required dropdown column '{required_unit_column}' not found. Available columns: {', '.join(df.columns)}")
    units = df[required_unit_column].unique().tolist()
 
    if required_destination_port_column not in df.columns:
        raise ValueError(f"Required dropdown column '{required_destination_port_column}' not found. Available columns: {', '.join(df.columns)}")
    # destination_ports will be filtered dynamically later
 
    if required_country_column not in df.columns:
        raise ValueError(f"Required dropdown column '{required_country_column}' not found. Available columns: {', '.join(df.columns)}")
    countries = df[required_country_column].unique().tolist()
 
except ValueError as ve:
    st.error(f"Data Processing Error for Dropdowns: {ve}")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred while preparing dropdown data: {e}")
    st.stop()
 
# Reordered dropdowns: Country first, then Destination Port, then Unit
selected_country = st.selectbox(f"Select {required_country_column}", (countries))
 
# Filter destination ports based on selected country
# Only show ports that exist for the selected country
filtered_ports_df = df[df[required_country_column] == selected_country]
destination_ports_for_country = sorted(filtered_ports_df[required_destination_port_column].unique().tolist())
 
selected_destination_port = st.selectbox(f"Select {required_destination_port_column}", destination_ports_for_country)
 
selected_unit = st.selectbox(f"Select {required_unit_column}", sorted(units))
 
 
st.header("Freight Rate Information")
 
# Filter DataFrame based on all three selections
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
        st.warning(f"No valid freight rate found (or rate is empty/non-numeric) for the selected combination. Please adjust your selections or check your data in column '{required_freight_column}'.")
else:
    st.warning("No freight rate data found for the selected combination. Please adjust your selections.")
 
st.header("Netback Calculation")
 
if freight_rate is not None:
    cif = st.number_input("Enter CIF (Cost, Insurance, Freight) in Dollars ($)", min_value=0.0, format="%.2f")
 
    local_rate_default = 0.02
    local_rate = st.number_input(f"Enter Local Rate (default: {local_rate_default})", min_value=0.0, value=local_rate_default, format="%.4f")
 
    divisor = 23000.0
 
    if cif > 0:
        netback = cif - (freight_rate / divisor) - local_rate
        st.success(f"**Calculated Netback:** ${netback:,.2f}")
    else:
        st.info("Enter a CIF value greater than 0 to calculate netback.")
else:
    st.info("Select a valid combination of Unit, Destination Port, and Country with an existing and valid freight rate to proceed with Netback calculation.")
 
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
 
 