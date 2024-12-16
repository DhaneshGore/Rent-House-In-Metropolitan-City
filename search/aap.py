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
data_file_path = 'D:/New folder (2)/City Rent/code/data/House_Rent_Dataset.csv'  # Ensure the correct relative path
data = pd.read_csv(data_file_path)

# Function to generate QR code for location
def generate_qr_code(lat, lon):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    location_url = f"https://www.google.com/maps?q={lat},{lon}"
    qr.add_data(location_url)
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
        filtered_data = data[
            (data['City'] == city) & (data['BHK'] == int(bhk))
        ]

        if not filtered_data.empty:
            # Generate QR codes for each row
            filtered_data['QR Code'] = filtered_data.apply(
                lambda row: generate_qr_code(row['Latitude'], row['Longitude']),
                axis=1
            )

            # Create a map centered on the filtered data
            center_lat = filtered_data['Latitude'].mean()
            center_lon = filtered_data['Longitude'].mean()
            map_object = folium.Map(location=[center_lat, center_lon], zoom_start=12)

            # Add markers for filtered data
            for _, row in filtered_data.iterrows():
                popup_content = f"""
                <b>Area:</b> {row['Area Locality']}<br>
                <b>City:</b> {row['City']}<br>
                <b>Rent:</b> {row['Rent']}<br>
                <b>BHK:</b> {row['BHK']}<br>
                <b>Size:</b> {row['Size']} sq.ft<br>
                <b>Furnishing:</b> {row['Furnishing Status']}<br>
                <b>Bathroom:</b> {row['Bathroom']}
                """
                popup = Popup(popup_content, max_width=300)
                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=popup
                ).add_to(map_object)

            map_html = map_object._repr_html_()

    return render_template(
        'index.html', 
        cities=cities, 
        bhk_options=bhk_options, 
        map_html=map_html, 
        data=filtered_data
    )
