import streamlit as st
import math

# Conversion factor: 1 meter = 3.28084 feet
METER_TO_FEET = 3.28084

# Streamlit app
st.title('Truck Selection for Rolls Transportation')

# Input fields for roll dimensions and weight
st.header('Roll Specifications')
roll_diameter = st.number_input('Roll Diameter (meters)', min_value=0.0, step=0.1)
roll_length = st.number_input('Roll Length (meters)', min_value=0.0, step=0.1)
roll_weight = st.number_input('Roll Weight (kg)', min_value=0.0, step=0.1)

# Input field for the number of rolls
st.header('Transportation Requirements')
number_of_rolls = st.number_input('Number of Rolls', min_value=1, step=1)

# Calculate total volume and weight required for the rolls
roll_volume = math.pi * (roll_diameter / 2) ** 2 * roll_length
total_volume_required = roll_volume * number_of_rolls
total_weight_required = roll_weight * number_of_rolls

# Suggest truck dimensions
st.header('Suggested Truck Specifications')

# Assume some standard truck sizes (converted to feet)
trucks = [
    {"name": "Small Truck", "length": 19.7, "width": 8.2, "height": 8.2, "weight_capacity": 5000},
    {"name": "Medium Truck", "length": 26.2, "width": 8.2, "height": 9.8, "weight_capacity": 10000},
    {"name": "Large Truck", "length": 39.4, "width": 8.2, "height": 11.5, "weight_capacity": 15000},
]

# Find the smallest truck that can accommodate the rolls
suitable_truck = None
for truck in trucks:
    truck_volume = (truck["length"] / METER_TO_FEET) * (truck["width"] / METER_TO_FEET) * (truck["height"] / METER_TO_FEET)
    if truck_volume >= total_volume_required and truck["weight_capacity"] >= total_weight_required:
        suitable_truck = truck
        break

# Display the result
if suitable_truck:
    st.write(f'Suggested Truck: {suitable_truck["name"]}')
    st.write(f'Truck Dimensions: {suitable_truck["length"]} ft (L) x {suitable_truck["width"]} ft (W) x {suitable_truck["height"]} ft (H)')
    st.write(f'Truck Weight Capacity: {suitable_truck["weight_capacity"]} kg')
else:
    st.write('No suitable truck found. Consider splitting the load or using a custom truck.')
