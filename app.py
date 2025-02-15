from flask import Flask, request, render_template, jsonify
import pandas as pd
import pickle
import os
import folium

# Import the Search blueprint
from search.aap import search_app

# Import the Chatbot blueprint (make sure you created chatbot_blueprint.py in the chatbot folder)
from chatbot.chatbot_blueprint import chatbot_bp

# Initialize the Flask app
app = Flask(__name__)

# -----------------------------------------------------------------------------
# Register Blueprints
# -----------------------------------------------------------------------------
# Search App: accessible at http://localhost:5000/search/
app.register_blueprint(search_app, url_prefix='/search')

# Chatbot: accessible at http://localhost:5000/chatbot/
app.register_blueprint(chatbot_bp, url_prefix='/chatbot')

# -----------------------------------------------------------------------------
# Paths for Models and Data
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# -----------------------------------------------------------------------------
# Load Pre-trained Models and Feature Columns
# -----------------------------------------------------------------------------
with open(os.path.join(MODEL_DIR, 'rf_model.pkl'), 'rb') as f:
    rf_model = pickle.load(f)

with open(os.path.join(MODEL_DIR, 'lgb_model.pkl'), 'rb') as f:
    lgb_model = pickle.load(f)

with open(os.path.join(MODEL_DIR, 'xgb_model.pkl'), 'rb') as f:
    xgb_model = pickle.load(f)

with open(os.path.join(MODEL_DIR, 'feature_columns.pkl'), 'rb') as f:
    feature_columns = pickle.load(f)

# -----------------------------------------------------------------------------
# Load the House Rent Dataset (for prediction and map rendering)
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
data_file_path = os.path.join(DATA_DIR, 'House_Rent_Dataset.csv')

# Load the House Rent Dataset (for prediction and map rendering)
data = pd.read_csv(data_file_path)
data = pd.read_csv(os.path.join(DATA_DIR, 'House_Rent_Dataset.csv'))

# -----------------------------------------------------------------------------
# Routes for the Main Application
# -----------------------------------------------------------------------------
@app.route('/')
def main_home():
    """
    Render the interactive prediction page.
    Accessible at http://localhost:5000/
    """
    return render_template('interactive.html')


@app.route('/get_cities', methods=['GET'])
def get_cities():
    """
    Return a list of unique cities from the dataset.
    """
    try:
        cities = data['City'].unique().tolist()
        return jsonify({"success": True, "cities": cities})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/get_city_details', methods=['GET'])
def get_city_details():
    """
    Return available BHK, Floor, and Area Type options for the selected city.
    """
    try:
        city = request.args.get('city')
        city_data = data[data['City'] == city]

        if city_data.empty:
            return jsonify({"success": False, "error": "City not found in dataset."})

        bhk_options = city_data['BHK'].unique().tolist()
        floor_options = city_data['Floor'].unique().tolist()
        area_type_options = city_data['Area Type'].unique().tolist()

        return jsonify({
            "success": True,
            "bhkOptions": sorted(bhk_options),
            "floorOptions": sorted(floor_options),
            "areaTypeOptions": sorted(area_type_options)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/predict', methods=['POST'])
def predict():
    """
    Process prediction requests.
    """
    try:
        # Extract input data from the POSTed JSON
        form_data = request.json

        # Extract the numeric part of the floor (e.g., "2 out of 7")
        floor_value = form_data['Floor'].split()[0]

        # Build the input dictionary (using one-hot encoding for Area Type and City)
        input_data = {
            'BHK': int(form_data['BHK']),
            'Floor': int(floor_value),
            'Area Type_Carpet Area': 0,
            'Area Type_Super Area': 0,
            'City_Chennai': 0,
            'City_Delhi': 0,
            'City_Hyderabad': 0,
            'City_Kolkata': 0,
            'City_Mumbai': 0,
            'City_Bangalore': 0
        }
        input_data[f"Area Type_{form_data['Area Type']}"] = 1
        input_data[f"City_{form_data['City']}"] = 1

        # Create a DataFrame and align with the training feature columns
        feature_df = pd.DataFrame([input_data], columns=feature_columns).fillna(0)

        # Perform predictions using the loaded models
        prediction_rf = rf_model.predict(feature_df)[0]
        prediction_lgb = lgb_model.predict(feature_df)[0]
        prediction_xgb = xgb_model.predict(feature_df)[0]
        avg_prediction = (prediction_rf + prediction_lgb + prediction_xgb) / 3

        # Calculate monthly rent (example calculation)
        monthly_rent = (prediction_rf + prediction_xgb) / 12

        # Return the predictions as a JSON response
        return jsonify({
            "success": True,
            "predictions": {
                "House rent Starting from": f"{monthly_rent:.2f} INR/Month",
                "Highest Bank EMI on Monthly base": f"{prediction_lgb:.2f} INR/Month",
                "Highest upto Rent": f"{prediction_xgb:.2f} INR/Month",
                "Average Bank EMI on Monthly base": f"{avg_prediction:.2f} INR/Month",
                "Monthly Rent Average": f"{prediction_rf:.2f} INR/month"
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/get_map', methods=['POST'])
def get_map():
    """
    Generate and return an HTML representation of a map based on the selected city.
    """
    try:
        city = request.json.get('City')
        city_data = data[data['City'] == city]

        if city_data.empty:
            return jsonify({"success": False, "error": "No data available for the selected city."})

        # Determine center coordinates for the city
        city_lat = city_data['Latitude'].mean()
        city_lon = city_data['Longitude'].mean()

        # Create a Folium map
        city_map = folium.Map(location=[city_lat, city_lon], zoom_start=12)

        # Add markers for each property in the city
        for _, row in city_data.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"{row['Area Locality']}: {row['Rent']} INR"
            ).add_to(city_map)

        # Return the map as HTML
        return jsonify({"success": True, "map": city_map._repr_html_()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# -----------------------------------------------------------------------------
# Run the Unified Application
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
