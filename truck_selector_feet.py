import streamlit as st
import pandas as pd
import math

# Conversion factor: 1 meter = 3.28084 feet
METER_TO_FEET = 3.28084

# Function to calculate roll volume
def calculate_roll_volume(diameter, length):
    return math.pi * (diameter / 2) ** 2 * length

# Function to optimize truck selection using a greedy algorithm
def optimize_truck_selection(truck_data, total_volume_required, total_weight_required):
    # Sort trucks by volume and weight capacity
    truck_data["Volume (m³)"] = (truck_data["Length (ft)"] / METER_TO_FEET) * \
                                (truck_data["Width (ft)"] / METER_TO_FEET) * \
                                (truck_data["Height (ft)"] / METER_TO_FEET)
    truck_data = truck_data.sort_values(by=["Volume (m³)", "Weight Capacity (kg)"])
    
    trucks_used = []
    for _, truck in truck_data.iterrows():
        if total_volume_required <= 0 and total_weight_required <= 0:
            break
        if truck["Volume (m³)"] > 0 and truck["Weight Capacity (kg)"] > 0:
            trucks_used.append(truck)
            total_volume_required -= truck["Volume (m³)"]
            total_weight_required -= truck["Weight Capacity (kg)"]

    if total_volume_required > 0 or total_weight_required > 0:
        return None  # Not all rolls can be accommodated
    return trucks_used

# Streamlit app
st.title('Optimized Truck Selection for Multiple Roll Types with Excel Upload')

# Input for multiple roll types
st.header('Roll Specifications')
roll_types = st.number_input('Number of Different Roll Types', min_value=1, step=1)

total_volume_required = 0
total_weight_required = 0

for i in range(roll_types):
    st.subheader(f'Roll Type {i+1}')
    roll_diameter = st.number_input(f'Roll {i+1} Diameter (meters)', min_value=0.0, step=0.1, key=f'diameter_{i}')
    roll_length = st.number_input(f'Roll {i+1} Length (meters)', min_value=0.0, step=0.1, key=f'length_{i}')
    roll_weight = st.number_input(f'Roll {i+1} Weight (kg)', min_value=0.0, step=0.1, key=f'weight_{i}')
    number_of_rolls = st.number_input(f'Number of Rolls for Type {i+1}', min_value=1, step=1, key=f'count_{i}')
    
    # Calculate total volume and weight for this roll type
    roll_volume = calculate_roll_volume(roll_diameter, roll_length)
    total_volume_required += roll_volume * number_of_rolls
    total_weight_required += roll_weight * number_of_rolls

# Upload truck dimensions from an Excel file
st.header('Upload Truck Dimensions Excel File')
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file:
    # Read the Excel file
    truck_data = pd.read_excel(uploaded_file)
    
    # Optimize truck selection
    trucks_used = optimize_truck_selection(truck_data, total_volume_required, total_weight_required)

    # Display the result
    if trucks_used:
        st.write(f'Total Trucks Used: {len(trucks_used)}')
        for truck in trucks_used:
            st.write(f'{truck["Name"]}: {truck["Length (ft)"]} ft (L) x {truck["Width (ft)"]} ft (W) x {truck["Height (ft)"]} ft (H)')
            st.write(f'Weight Capacity: {truck["Weight Capacity (kg)"]} kg')
    else:
        st.write('No suitable combination of trucks found. Consider using more or different trucks.')
else:
    st.write('Please upload a truck dimensions Excel file.')