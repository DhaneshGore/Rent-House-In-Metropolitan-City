from flask import Blueprint, render_template, request
import pandas as pd
import folium
from folium import Popup
import qrcode
from io import BytesIO
import base64

# Define the blueprint for the search app
search_app = Blueprint(
    'search_app', __name__,
    template_folder='templates',  # Template folder specific to search app
    static_folder='static'        # Static folder specific to search app
)

# Load the dataset
data_file_path = 'D:/New folder (2)/City Rent/code/data/House_Rent_Dataset.csv'  # Adjust the path as needed
data = pd.read_csv(data_file_path)

# Function to generate QR code with property details and Google Maps link
def generate_qr_code(row):
    """
    Generates a QR Code containing property details and a Google Maps link.
    """
    property_details = (
        f"Property Details:\n"
        f"Area Locality: {row['Area Locality']}\n"
        f"City: {row['City']}\n"
        f"Rent: {row['Rent']}\n"
        f"BHK: {row['BHK']}\n"
        f"Size: {row['Size']} sq.ft\n"
        f"Furnishing: {row['Furnishing Status']}\n"
        f"Tenant Preference: {row['Tenant Preferred']}\n"
        f"Bathrooms: {row['Bathroom']}\n"
        f"Map: https://www.google.com/maps?q={row['Latitude']},{row['Longitude']}"
    )
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(property_details)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)
    img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_b64

@search_app.route('/', methods=['GET', 'POST'])
def index():
    """
    Render the search page and display properties based on city and BHK filters.
    """
    cities = sorted(data['City'].dropna().unique())
    bhk_options = sorted(data['BHK'].dropna().unique())
    map_html = None
    filtered_data = None

    if request.method == 'POST':
        city = request.form.get('city')
        bhk = request.form.get('bhk')

        # Filter data based on user input
        filtered_data = data[
            (data['City'] == city) & (data['BHK'] == int(bhk))
        ]

        if not filtered_data.empty:
            # Generate QR Codes for filtered properties
            filtered_data['QR Code'] = filtered_data.apply(generate_qr_code, axis=1)

            # Create a map centered on the filtered properties
            center_lat = filtered_data['Latitude'].mean()
            center_lon = filtered_data['Longitude'].mean()
            map_object = folium.Map(location=[center_lat, center_lon], zoom_start=12)

            # Add markers for each property
            for _, row in filtered_data.iterrows():
                popup_content = f"""
                <b>Area Locality:</b> {row['Area Locality']}<br>
                <b>City:</b> {row['City']}<br>
                <b>Rent:</b> {row['Rent']}<br>
                <b>BHK:</b> {row['BHK']}<br>
                <b>Size:</b> {row['Size']} sq.ft<br>
                <b>Furnishing:</b> {row['Furnishing Status']}<br>
                <b>Bathrooms:</b> {row['Bathroom']}<br>
                <a href='https://www.google.com/maps?q={row['Latitude']},{row['Longitude']}' target='_blank'>View on Map</a>
                """
                popup = Popup(popup_content, max_width=300)
                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=popup
                ).add_to(map_object)

            # Convert map to HTML
            map_html = map_object._repr_html_()

    return render_template(
        'index.html', 
        cities=cities, 
        bhk_options=bhk_options, 
        map_html=map_html, 
        data=filtered_data
    )
