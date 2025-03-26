import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ortools.linear_solver import pywraplp

# Streamlit App Title
st.title("Truck Forecasting & Space Optimization")

# User Input: Truck Dimensions
st.sidebar.header("Truck Dimensions (in feet)")
truck_types = {
    "Small (20ft)": (20, 8, 8),
    "Medium (40ft)": (40, 8, 8),
    "Large (53ft)": (53, 8.5, 9.5)
}
num_trucks = {}

# User Input: Carton Details
st.sidebar.header("Carton Details (in inches)")
num_carton_types = st.sidebar.number_input("Number of Carton Types", min_value=1, value=3)
carton_data = []

total_carton_volume = 0
total_carton_count = 0
for i in range(num_carton_types):
    st.sidebar.subheader(f"Carton Type {i+1}")
    carton_length = st.sidebar.number_input(f"Carton {i+1} Length", min_value=1, value=12, key=f"cl{i}")
    carton_width = st.sidebar.number_input(f"Carton {i+1} Width", min_value=1, value=12, key=f"cw{i}")
    carton_height = st.sidebar.number_input(f"Carton {i+1} Height", min_value=1, value=12, key=f"ch{i}")
    carton_demand = st.sidebar.number_input(f"Demand for Carton {i+1}", min_value=1, value=10, key=f"cd{i}")
    carton_volume = (carton_length * carton_width * carton_height) / 1728  # Convert to cubic feet
    total_carton_volume += carton_demand * carton_volume
    total_carton_count += carton_demand
    carton_data.append({"Length": carton_length, "Width": carton_width, "Height": carton_height, "Demand": carton_demand, "Volume": carton_volume})

if st.button("Run Forecasting"):
    remaining_volume = total_carton_volume
    truck_requirements = {}
    truck_box_distribution = {}
    total_truck_capacity = 0
    
    for truck_type, (length, width, height) in sorted(truck_types.items(), key=lambda x: -x[1][0]):
        truck_volume = length * width * height
        num_trucks = int(remaining_volume // truck_volume)
        remaining_volume %= truck_volume
        truck_requirements[truck_type] = num_trucks
        total_truck_capacity += num_trucks * truck_volume
        truck_box_distribution[truck_type] = num_trucks * (truck_volume // (total_carton_volume / total_carton_count))
    
    # Calculate utilization
    utilization = (total_carton_volume / total_truck_capacity) * 100 if total_truck_capacity > 0 else 0
    
    st.write("### Truck Requirements to Fulfill Demand:")
    for truck_type, count in truck_requirements.items():
        st.write(f"- {truck_type}: {count} trucks")
    
    st.write(f"### Capacity Utilization: {utilization:.2f}%")
    
    st.write("### Number of Boxes in Each Truck:")
    for truck_type, box_count in truck_box_distribution.items():
        st.write(f"- {truck_type}: {int(box_count)} boxes")
    
    st.write("### Total Boxes of Each Type:")
    for i, carton in enumerate(carton_data):
        st.write(f"- Carton {i+1}: {carton['Demand']} boxes")
    
    remaining_boxes = {}
    if remaining_volume > 0:
        st.write("### Note: Some volume remains unallocated. Consider using additional trucks or different configurations.")
        additional_truck = min(truck_types.items(), key=lambda x: x[1][0])  # Smallest truck
        additional_truck_type, (length, width, height) = additional_truck
        additional_truck_volume = length * width * height
        additional_trucks_needed = int(np.ceil(remaining_volume / additional_truck_volume))
        
        st.write(f"### Recommended Allocation for Remaining Volume:")
        st.write(f"- Use {additional_trucks_needed} additional {additional_truck_type} truck(s) to accommodate remaining volume.")
        st.write(f"- Consider repacking or optimizing stacking methods for better space utilization.")
        
        for carton in carton_data:
            remaining_count = int((remaining_volume // carton["Volume"]))
            remaining_boxes[f"Carton {carton_data.index(carton) + 1}"] = remaining_count
        
        st.write("### Remaining Boxes by Type:")
        for carton_type, count in remaining_boxes.items():
            st.write(f"- {carton_type}: {count} boxes")
    
    # Honeycomb pattern simulation visualization
    st.write("### Space Optimization Using Honeycomb Pattern")
    rows = int(np.sqrt(num_carton_types)) + 1
    cols = (num_carton_types // rows) + 1
    
    fig, ax = plt.subplots(figsize=(6, 6))
    for i in range(rows):
        for j in range(cols):
            x = j + (0.5 * (i % 2))
            y = i * 0.87  # Adjust for hexagonal stacking
            hexagon = plt.Polygon(
                [[x, y], [x+0.5, y+0.25], [x+0.5, y+0.75], [x, y+1], [x-0.5, y+0.75], [x-0.5, y+0.25]],
                edgecolor='black', facecolor='lightblue'
            )
            ax.add_patch(hexagon)
    
    ax.set_xlim(-1, cols + 1)
    ax.set_ylim(-1, rows + 1)
    ax.set_aspect('equal')
    ax.axis('off')
    st.pyplot(fig)
    
    st.write("### Space Optimization Visualization Completed!")
