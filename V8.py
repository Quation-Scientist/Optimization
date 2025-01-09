import streamlit as st
import pandas as pd
import math
from fpdf import FPDF

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
            max_fit = int(remaining_volume // box_volume)
            actual_fit = min(max_fit, box['quantity'])
            box_counts[f"box_type_{i+1}"] = actual_fit
            remaining_volume -= actual_fit * box_volume
        
        # Fit rolls
        for i, roll in enumerate(sorted_rolls):
            roll_volume = roll['volume']
            max_fit = int(remaining_volume // roll_volume)
            actual_fit = min(max_fit, roll['quantity'])
            roll_counts[f"roll_type_{i+1}"] = actual_fit
            remaining_volume -= actual_fit * roll_volume
        
        # Calculate how many more can be accommodated
        additional_boxes = {f"box_type_{i+1}": int(remaining_volume // box['volume']) for i, box in enumerate(sorted_boxes)}
        additional_rolls = {f"roll_type_{i+1}": int(remaining_volume // roll['volume']) for i, roll in enumerate(sorted_rolls)}
        
        results.append({
            'truck': truck,
            'box_counts': box_counts,
            'roll_counts': roll_counts,
            'remaining_volume': remaining_volume,
            'additional_boxes': additional_boxes,
            'additional_rolls': additional_rolls
        })
    
    return results

# Function to generate PDF report
def generate_pdf_report(results):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Truck Load Optimization Report", ln=True, align='C')
    
    for result in results:
        pdf.cell(200, 10, txt=f"Truck Type {results.index(result) + 1}", ln=True, align='L')
        pdf.cell(200, 10, txt="Box Counts:", ln=True, align='L')
        for key, value in result['box_counts'].items():
            pdf.cell(200, 10, txt=f"{key}: {value}", ln=True, align='L')
        pdf.cell(200, 10, txt="Roll Counts:", ln=True, align='L')
        for key, value in result['roll_counts'].items():
            pdf.cell(200, 10, txt=f"{key}: {value}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Remaining Volume: {result['remaining_volume']} cubic inches", ln=True, align='L')
        pdf.cell(200, 10, txt="Additional Boxes that can be accommodated:", ln=True, align='L')
        for key, value in result['additional_boxes'].items():
            pdf.cell(200, 10, txt=f"{key}: {value}", ln=True, align='L')
        pdf.cell(200, 10, txt="Additional Rolls that can be accommodated:", ln=True, align='L')
        for key, value in result['additional_rolls'].items():
            pdf.cell(200, 10, txt=f"{key}: {value}", ln=True, align='L')
        pdf.ln(10)
    
    pdf.output("truck_load_optimization_report.pdf")

# Streamlit App
st.title("Truck Load Optimization")

# Login Section
st.sidebar.header("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_button = st.sidebar.button("Login")

if login_button:
    if username == "admin" and password == "admin":
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
        
        for result in results:
            st.subheader(f"Truck Type {results.index(result) + 1}")
            box_df = pd.DataFrame(result['box_counts'].items(), columns=['Box Type', 'Count'])
            roll_df = pd.DataFrame(result['roll_counts'].items(), columns=['Roll Type', 'Count'])
            additional_boxes_df = pd.DataFrame(result['additional_boxes'].items(), columns=['Box Type', 'Additional Count'])
            additional_rolls_df = pd.DataFrame(result['additional_rolls'].items(), columns=['Roll Type', 'Additional Count'])
            
            st.write("Box Counts:")
            st.table(box_df)
            
            st.write("Roll Counts:")
            st.table(roll_df)
            
            st.write(f"Remaining Volume: {result['remaining_volume']} cubic inches")
            
            st.write("Additional Boxes that can be accommodated:")
            st.table(additional_boxes_df)
            
            st.write("Additional Rolls that can be accommodated:")
            st.table(additional_rolls_df)
        
        # Generate PDF report
        generate_pdf_report(results)
        st.success("PDF report has been generated and saved as 'truck_load_optimization_report.pdf'")
