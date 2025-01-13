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

# Password for access control
password = st.text_input("Enter password to access the app", type="password")

# Check if the password is correct (replace 'yourpassword' with your desired password)
if password != "yourpassword":
    st.error("Invalid password. Please try again.")
else:
    # Input for multiple roll types
    st.header('Roll Specifications')

    # List to hold different roll types and their quantities
    roll_types = []

    # Allow user to input multiple roll types
    num_roll_types = st.number_input('Number of Different Roll Types', min_value=1, step=1)

    for i in range(num_roll_types):
        st.subheader(f'Roll Type {i+1}')
        roll_diameter = st.number_input(f'  Roll Diameter (meters) for Type {i+1}', min_value=0.01, step=0.1)
        roll_length = st.number_input(f'  Roll Length (meters) for Type {i+1}', min_value=0.01, step=0.1)
        roll_weight = st.number_input(f'  Roll Weight (kg) for Type {i+1}', min_value=0.1, step=0.1)
        roll_quantity = st.number_input(f'  Number of Rolls for Type {i+1}', min_value=1, step=1)

        roll_types.append({
            'Diameter': roll_diameter,
            'Length': roll_length,
            'Weight': roll_weight,
            'Quantity': roll_quantity
        })

    # Calculate total volume and weight required for all roll types
    total_volume_required = 0
    total_weight_required = 0
    roll_volumes = []

    for roll in roll_types:
        try:
            roll_volume = calculate_roll_volume(roll['Diameter'], roll['Length'])
            roll_weight = roll['Weight']
            roll_quantity = roll['Quantity']
            total_volume_required += roll_volume * roll_quantity
            total_weight_required += roll_weight * roll_quantity
            roll_volumes.append(roll_volume)
        except ValueError as e:
            st.error(f"Error: {e}")

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

    # Optimize truck selection and calculate number of rolls per truck
    rolls_accommodated = optimize_truck_selection(truck_data, total_volume_required, total_weight_required, sum(roll_volumes), sum([roll['Weight'] for roll in roll_types]))

    # Display the result
    if rolls_accommodated:
        st.write(f'Total Rolls: {sum([roll["Quantity"] for roll in roll_types])}')
        for truck in rolls_accommodated:
            st.write(f'{truck["Name"]} can accommodate {truck["Rolls Accommodated"]} rolls')
            st.write(f'Volume Remaining: {truck["Volume (m³) Remaining"]:.2f} m³')
            st.write(f'Weight Remaining: {truck["Weight (kg) Remaining"]:.2f} kg')
    else:
        st.write('Not all rolls can be accommodated. Consider using more trucks or adjusting roll specifications.')
