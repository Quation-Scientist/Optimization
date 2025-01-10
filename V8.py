import streamlit as st
import pandas as pd
import math
import io

# Conversion factors
FEET_TO_INCHES = 12

# Helper function to calculate volume
def calculate_volume(length, width, height):
    return length * width * height

# Helper function to calculate cylinder volume
def calculate_cylinder_volume(diameter, height):
    radius = diameter / 2
    return math.pi * (radius ** 2) * height

# Function to optimize loading
def optimize_loading(trucks, boxes, rolls):
    results = []
    
    for truck in trucks:
        truck_volume = calculate_volume(truck['length'] * FEET_TO_INCHES, 
                                        truck['width'] * FEET_TO_INCHES, 
                                        truck['height'] * FEET_TO_INCHES)
        remaining_volume = truck_volume
        
        # Initialize counts
        box_counts = {f"box_type_{i+1}": 0 for i in range(len(boxes))}
        roll_counts = {f"roll_type_{i+1}": 0 for i in range(len(rolls))}
        
        # Sort boxes and rolls by volume (descending)
        sorted_boxes = sorted(boxes, key=lambda b: b['volume'], reverse=True)
        sorted_rolls = sorted(rolls, key=lambda r: r['volume'], reverse=True)
        
        # Fit boxes
        for i, box in enumerate(sorted_boxes):
            box_volume = box['volume']
            if remaining_volume >= box_volume and box['quantity'] > 0:
                max_fit = int(remaining_volume // box_volume)
                actual_fit = min(max_fit, box['quantity'])
                box_counts[f"box_type_{i+1}"] = actual_fit
                remaining_volume -= actual_fit * box_volume
            else:
                box_counts[f"box_type_{i+1}"] = 0
        
        # Fit rolls
        for i, roll in enumerate(sorted_rolls):
            roll_volume = roll['volume']
            if remaining_volume >= roll_volume and roll['quantity'] > 0:
                max_fit = int(remaining_volume // roll_volume)
                actual_fit = min(max_fit, roll['quantity'])
                roll_counts[f"roll_type_{i+1}"] = actual_fit
                remaining_volume -= actual_fit * roll_volume
            else:
                roll_counts[f"roll_type_{i+1}"] = 0
        
        # Calculate how many more can be accommodated
        additional_boxes = {f"box_type_{i+1}": int(remaining_volume // box['volume']) if box['volume'] > 0 else 0 for i, box in enumerate(sorted_boxes)}
        additional_rolls = {f"roll_type_{i+1}": int(remaining_volume // roll['volume']) if roll['volume'] > 0 else 0 for i, roll in enumerate(sorted_rolls)}
        
        results.append({
            'truck': truck,
            'box_counts': box_counts,
            'roll_counts': roll_counts,
            'remaining_volume': remaining_volume,
            'additional_boxes': additional_boxes,
            'additional_rolls': additional_rolls
        })
    
    return results

# Streamlit App
st.title("Truck Load Optimization")

# Login Section
st.sidebar.header("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_button = st.sidebar.button("Login")

if login_button:
    if username == "admin" and password == "password":
        st.sidebar.success("Logged in successfully!")
    else:
        st.sidebar.error("Invalid username or password")

# Add a background image
page_bg_img = '''
<style>
body {
    background-image: url("https://www.example.com/truck-background.jpg");
    background-size: cover;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

if username == "admin" and password == "password":
    st.sidebar.header("Input Data")

    # Input for trucks (in feet)
    num_trucks = st.sidebar.number_input("Number of Truck Types", min_value=1, step=1)
    trucks = []
    for i in range(num_trucks):
        st.sidebar.subheader(f"Truck Type {i+1}")
        length = st.sidebar.number_input(f"Length (ft) for Truck Type {i+1}", min_value=1.0, step=0.1)
        width = st.sidebar.number_input(f"Width (ft) for Truck Type {i+1}", min_value=1.0, step=0.1)
        height = st.sidebar.number_input(f"Height (ft) for Truck Type {i+1}", min_value=1.0, step=0.1)
        quantity = st.sidebar.number_input(f"Quantity for Truck Type {i+1}", min_value=1, step=1)
        trucks.append({'length': length, 'width': width, 'height': height, 'quantity': quantity})

    # Input for boxes (in inches)
    num_boxes = st.sidebar.number_input("Number of Box Types", min_value=1, step=1)
    boxes = []
    for i in range(num_boxes):
        st.sidebar.subheader(f"Box Type {i+1}")
        length = st.sidebar.number_input(f"Length (in) for Box Type {i+1}", min_value=0.1, step=0.1)
        width = st.sidebar.number_input(f"Width (in) for Box Type {i+1}", min_value=0.1, step=0.1)
        height = st.sidebar.number_input(f"Height (in) for Box Type {i+1}", min_value=0.1, step=0.1)
        quantity = st.sidebar.number_input(f"Quantity for Box Type {i+1}", min_value=1, step=1)
        volume = calculate_volume(length, width, height)
        boxes.append({'length': length, 'width': width, 'height': height, 'quantity': quantity, 'volume': volume})

    # Input for rolls (in inches)
    num_rolls = st.sidebar.number_input("Number of Roll Types", min_value=1, step=1)
    rolls = []
    for i in range(num_rolls):
        st.sidebar.subheader(f"Roll Type {i+1}")
        diameter = st.sidebar.number_input(f"Diameter (in) for Roll Type {i+1}", min_value=0.1, step=0.1)
        length = st.sidebar.number_input(f"Length (in) for Roll Type {i+1}", min_value=0.1, step=0.1)
        quantity = st.sidebar.number_input(f"Quantity for Roll Type {i+1}", min_value=1, step=1)
        volume = calculate_cylinder_volume(diameter, length)
        rolls.append({'diameter': diameter, 'length': length, 'quantity': quantity, 'volume': volume})

    # Add a run button
    if st.button("Run Optimization"):
        results = optimize_loading(trucks, boxes, rolls)
        
        report_data = []
        for result in results:
            truck_type = f"Truck Type {results.index(result) + 1}"
            box_df = pd.DataFrame(result['box_counts'].items(), columns=['Box Type', 'Count'])
            roll_df = pd.DataFrame(result['roll_counts'].items(), columns=['Roll Type', 'Count'])
            additional_boxes_df = pd.DataFrame(result['additional_boxes'].items(), columns=['Box Type', 'Additional Count'])
            additional_rolls_df = pd.DataFrame(result['additional_rolls'].items(), columns=['Roll Type', 'Additional Count'])
            
            report_data.append({
                'Truck Type': truck_type,
                'Box Counts': box_df.to_dict(orient='records'),
                'Roll Counts': roll_df.to_dict(orient='records'),
                'Remaining Volume': result['remaining_volume'],
                'Additional Boxes': additional_boxes_df.to_dict(orient='records'),
                'Additional Rolls': additional_rolls_df.to_dict(orient='records')
            })
            
            st.write(truck_type)
            st.write("Box Counts:")
            st.table(box_df)
            
            st.write("Roll Counts:")
            st.table(roll_df)
            
            st.write(f"Remaining Volume: {result['remaining_volume']} cubic inches")
            
            st.write("Additional Boxes that can be accommodated:")
            st.table(additional_boxes_df)
            
            st.write("Additional Rolls that can be accommodated:")
            st.table(additional_rolls_df)
        
        
