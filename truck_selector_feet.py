import streamlit as st
import math

# Conversion factor: 1 meter = 3.28084 feet
METER_TO_FEET = 3.28084

# Function to calculate roll volume
def calculate_roll_volume(diameter, length):
    if diameter <= 0 or length <= 0:
        raise ValueError("Diameter and Length must be greater than zero.")
    return math.pi * (diameter / 2) ** 2 * length

# Function to optimize truck selection and determine how many rolls can fit
def optimize_truck_selection(truck_data, total_volume_required, total_weight_required, roll_volume, roll_weight):
    rolls_accommodated = []
    try:
        # Sort trucks by volume and weight capacity
        truck_data = sorted(truck_data, key=lambda x: (x["Volume (m³)"], x["Weight Capacity (kg)"]))

        for truck in truck_data:
            truck_volume_remaining = truck["Volume (m³)"]
            truck_weight_remaining = truck["Weight Capacity (kg)"]

            # Calculate how many rolls this truck can carry based on volume and weight
            rolls_by_volume = truck_volume_remaining // roll_volume
            rolls_by_weight = truck_weight_remaining // roll_weight
            rolls_in_truck = min(rolls_by_volume, rolls_by_weight)

            rolls_accommodated.append({
                "Name": truck["Name"],
                "Rolls Accommodated": rolls_in_truck,
                "Volume (m³) Remaining": truck_volume_remaining - rolls_in_truck * roll_volume,
                "Weight (kg) Remaining": truck_weight_remaining - rolls_in_truck * roll_weight
            })

            total_volume_required -= rolls_in_truck * roll_volume
            total_weight_required -= rolls_in_truck * roll_weight

            if total_volume_required <= 0 and total_weight_required <= 0:
                break
    except KeyError as e:
        st.error(f"KeyError: Missing key in truck data: {e}")
    except TypeError as e:
        st.error(f"TypeError: Incorrect type used in data processing: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

    if total_volume_required > 0 or total_weight_required > 0:
        return None  # Not all rolls can be accommodated
    return rolls_accommodated

# Streamlit app
st.title('Truck Selection: Number of Rolls Per Truck')

# Input for roll specifications
st.header('Roll Specifications')

# Validate non-zero inputs for diameter, length, and weight
roll_diameter = st.number_input('Roll Diameter (meters)', min_value=0.01, step=0.1)
roll_length = st.number_input('Roll Length (meters)', min_value=0.01, step=0.1)
roll_weight = st.number_input('Roll Weight (kg)', min_value=0.1, step=0.1)
number_of_rolls = st.number_input('Number of Rolls', min_value=1, step=1)

# Calculate roll volume
try:
    roll_volume = calculate_roll_volume(roll_diameter, roll_length)
except ValueError as e:
    st.error(f"Error: {e}")
    roll_volume = 0

if roll_volume > 0:
    total_volume_required = roll_volume * number_of_rolls
    total_weight_required = roll_weight * number_of_rolls

    # Predefined truck dimensions (no Excel upload)
    truck_data = [
        {"Name": "Small Truck", "Length (ft)": 19.7, "Width (ft)": 8.2, "Height (ft)": 8.2, "Weight Capacity (kg)": 5000},
        {"Name": "Medium Truck", "Length (ft)": 26.2, "Width (ft)": 8.2, "Height (ft)": 9.8, "Weight Capacity (kg)": 10000},
        {"Name": "Large Truck", "Length (ft)": 39.4, "Width (ft)": 8.2, "Height (ft)": 11.5, "Weight Capacity (kg)": 15000},
    ]

    # Convert truck dimensions from feet to cubic meters
    for truck in truck_data:
        try:
            truck["Volume (m³)"] = (truck["Length (ft)"] / METER_TO_FEET) * \
                                   (truck["Width (ft)"] / METER_TO_FEET) * \
                                   (truck["Height (ft)"] / METER_TO_FEET)
        except KeyError as e:
            st.error(f"KeyError: Missing dimension key in truck data: {e}")
        except TypeError as e:
            st.error(f"TypeError: Incorrect type used in truck dimension conversion: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

    # Display the truck's individual capacity for rolls based on their volume and weight
    st.subheader('Truck Capacity Overview (in terms of Rolls)')
    for truck in truck_data:
        rolls_by_volume = truck["Volume (m³)"] // roll_volume
        rolls_by_weight = truck["Weight Capacity (kg)"] // roll_weight
        rolls_possible = min(rolls_by_volume, rolls_by_weight)
        st.write(f"{truck['Name']} can hold up to {rolls_possible} rolls based on its capacity.")

    # Optimize truck selection and calculate number of rolls per truck
    rolls_accommodated = optimize_truck_selection(truck_data, total_volume_required, total_weight_required, roll_volume, roll_weight)

    # Display the result
    if rolls_accommodated:
        st.write(f'Total Rolls: {number_of_rolls}')
        for truck in rolls_accommodated:
            st.write(f'{truck["Name"]} can accommodate {truck["Rolls Accommodated"]} rolls')
            st.write(f'Volume Remaining: {truck["Volume (m³) Remaining"]:.2f} m³')
            st.write(f'Weight Remaining: {truck["Weight (kg) Remaining"]:.2f} kg')
    else:
        st.write('Not all rolls can be accommodated. Consider using more trucks or adjusting roll specifications.')
else:
    st.write("Please ensure the diameter and length of the roll are greater than zero.")
