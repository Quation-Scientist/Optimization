import streamlit as st
import pandas as pd
import math
import io
import matplotlib.pyplot as plt

# Conversion factors
FEET_TO_INCHES = 12
LBS_TO_KG = 0.453592

# Helper function to calculate volume
def calculate_volume(length, width, height):
    return length * width * height

# Helper function to calculate cylinder volume
def calculate_cylinder_volume(diameter, height):
    radius = diameter / 2
    return math.pi * (radius ** 2) * height

# Function to optimize roll placement using a honeycomb pattern
def optimize_honeycomb_packing(truck_width, truck_length, roll_diameter):
    row_spacing = roll_diameter * math.sqrt(3) / 2  # Hexagonal packing spacing
    max_rows = int(truck_length // row_spacing)
    max_cols = int(truck_width // roll_diameter)
    
    total_rolls = 0
    positions = []
    for row in range(max_rows):
        cols = max_cols if row % 2 == 0 else max_cols - 1  # Alternate row shifting
        for col in range(cols):
            x = col * roll_diameter + (roll_diameter / 2 if row % 2 != 0 else 0)
            y = row * row_spacing
            positions.append((x, y))
        total_rolls += cols
    
    return total_rolls, positions

# Function to optimize loading
def optimize_loading(trucks, rolls):
    results = []
    
    for truck in trucks:
        truck_volume = calculate_volume(truck['length'] * FEET_TO_INCHES, 
                                        truck['width'] * FEET_TO_INCHES, 
                                        truck['height'] * FEET_TO_INCHES)
        remaining_volume = truck_volume
        remaining_weight = truck['max_weight'] * LBS_TO_KG  # Convert to KG
        
        # Initialize counts
        roll_counts = {f"roll_type_{i+1}": 0 for i in range(len(rolls))}
        
        # Sort rolls by volume (descending)
        sorted_rolls = sorted(rolls, key=lambda r: r['volume'], reverse=True)
        
        # Fit rolls using honeycomb pattern and weight constraint
        for i, roll in enumerate(sorted_rolls):
            if roll['quantity'] > 0:
                max_fit, positions = optimize_honeycomb_packing(truck['width'] * FEET_TO_INCHES, truck['length'] * FEET_TO_INCHES, roll['diameter'])
                actual_fit = min(max_fit, roll['quantity'])
                total_weight = actual_fit * roll['weight'] * LBS_TO_KG  # Convert to KG
                
                if total_weight <= remaining_weight:
                    roll_counts[f"roll_type_{i+1}"] = actual_fit
                    remaining_weight -= total_weight
                else:
                    roll_counts[f"roll_type_{i+1}"] = int(remaining_weight // (roll['weight'] * LBS_TO_KG))
                    remaining_weight = 0
        
        results.append({
            'truck': truck,
            'roll_counts': roll_counts,
            'remaining_volume': remaining_volume,
            'remaining_weight': remaining_weight,
            'positions': positions
        })
    
    return results

# Function to visualize the honeycomb pattern
def visualize_honeycomb(positions, roll_diameter, truck_width, truck_length):
    fig, ax = plt.subplots(figsize=(8, 6))
    for x, y in positions:
        circle = plt.Circle((x, y), roll_diameter / 2, color='blue', alpha=0.5)
        ax.add_patch(circle)
    ax.set_xlim(0, truck_width * FEET_TO_INCHES)
    ax.set_ylim(0, truck_length * FEET_TO_INCHES)
    ax.set_aspect('equal')
    ax.set_title("Honeycomb Roll Placement")
    st.pyplot(fig)

# Streamlit App
st.title("Truck Load Optimization")

st.sidebar.header("Input Data")

# Input for trucks (in feet)
num_trucks = st.sidebar.number_input("Number of Truck Types", min_value=1, step=1)
trucks = []
for i in range(num_trucks):
    st.sidebar.subheader(f"Truck Type {i+1}")
    length = st.sidebar.number_input(f"Length (ft) for Truck Type {i+1}", min_value=1.0, step=0.1)
    width = st.sidebar.number_input(f"Width (ft) for Truck Type {i+1}", min_value=1.0, step=0.1)
    height = st.sidebar.number_input(f"Height (ft) for Truck Type {i+1}", min_value=1.0, step=0.1)
    max_weight = st.sidebar.number_input(f"Max Weight (kg) for Truck Type {i+1}", min_value=50.0, step=25.0)
    quantity = st.sidebar.number_input(f"Quantity for Truck Type {i+1}", min_value=1, step=1)
    trucks.append({'length': length, 'width': width, 'height': height, 'max_weight': max_weight, 'quantity': quantity})

# Input for rolls (in inches)
num_rolls = st.sidebar.number_input("Number of Roll Types", min_value=1, step=1)
rolls = []
for i in range(num_rolls):
    st.sidebar.subheader(f"Roll Type {i+1}")
    diameter = st.sidebar.number_input(f"Diameter (in) for Roll Type {i+1}", min_value=0.1, step=0.1)
    length = st.sidebar.number_input(f"Length (in) for Roll Type {i+1}", min_value=0.1, step=0.1)
    weight = st.sidebar.number_input(f"Weight (kg) for Roll Type {i+1}", min_value=0.5, step=0.1)
    quantity = st.sidebar.number_input(f"Quantity for Roll Type {i+1}", min_value=1, step=1)
    volume = calculate_cylinder_volume(diameter, length)
    rolls.append({'diameter': diameter, 'length': length, 'weight': weight, 'quantity': quantity, 'volume': volume})

# Add a run button
if st.button("Run Optimization"):
    results = optimize_loading(trucks, rolls)
    
    for result in results:
        st.subheader(f"Truck Type {results.index(result) + 1}")
        st.write("Roll Counts:")
        st.table(pd.DataFrame(result['roll_counts'].items(), columns=['Roll Type', 'Count']))
        st.write(f"Remaining Volume: {result['remaining_volume']} cubic inches")
        st.write(f"Remaining Weight: {result['remaining_weight']} kg")
        
        # Visualization of Honeycomb Pattern
        visualize_honeycomb(result['positions'], rolls[0]['diameter'], result['truck']['width'], result['truck']['length'])
