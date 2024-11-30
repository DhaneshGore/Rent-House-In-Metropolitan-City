from flask import Flask, request, render_template, jsonify
import pandas as pd
import pickle
import os
import folium


# Initialize Flask app
app = Flask(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Load pre-trained models
with open(os.path.join(MODEL_DIR, 'rf_model.pkl'), 'rb') as f:
    rf_model = pickle.load(f)

with open(os.path.join(MODEL_DIR, 'lgb_model.pkl'), 'rb') as f:
    lgb_model = pickle.load(f)

with open(os.path.join(MODEL_DIR, 'xgb_model.pkl'), 'rb') as f:
    xgb_model = pickle.load(f)

# Load feature columns used during training
with open(os.path.join(MODEL_DIR, 'feature_columns.pkl'), 'rb') as f:
    feature_columns = pickle.load(f)

# Load the dataset for map rendering
data = pd.read_csv(os.path.join(DATA_DIR, 'House_Rent_Dataset.csv'))

@app.route('/')
def home():
    """
    Render the interactive HTML form for predictions and map.
    """
    return render_template('interactive.html')

@app.route('/predict_page')
def predict_page():
    """
    Render the prediction form page.
    """
    return render_template('predict.html')


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
    Return available BHK, floor, and area types for the selected city.
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
    
@app.route('/get_city_map_data', methods=['GET'])
def get_city_map_data():
    city = request.args.get('city')
    if not city:
        return jsonify(success=False, error="City not provided"), 400

    # Example city data (replace with database query or API call)
    city_data = {
        "Bangalore": {
            "center": {"lat": 12.9716, "lng": 77.5946},
            "zoom": 12,
            "locations": [
                {"name": "Location A", "lat": 12.9716, "lng": 77.5946, "details": "Info about Location A"},
                {"name": "Location B", "lat": 12.975, "lng": 77.59, "details": "Info about Location B"},
            ]
        },
        "Mumbai": {
            "center": {"lat": 19.076, "lng": 72.8777},
            "zoom": 12,
            "locations": [
                {"name": "Location C", "lat": 19.076, "lng": 72.8777, "details": "Info about Location C"},
                {"name": "Location D", "lat": 19.08, "lng": 72.88, "details": "Info about Location D"},
            ]
        }
    }

    if city in city_data:
        return jsonify(success=True, data=city_data[city])
    else:
        return jsonify(success=False, error="City data not found"), 404


@app.route('/predict', methods=['POST'])
def predict():
    """
    Handle prediction requests and return yearly and monthly rent.
    """
    try:
        # Extract input data from the form
        form_data = request.json

        # Extract numeric floor value (e.g., '2 out of 7' -> 2)
        floor_value = form_data['Floor'].split()[0]  # Get the first part before 'out'

        # Build input data for prediction
        input_data = {
            'BHK': int(form_data['BHK']),
            'Floor': int(floor_value),  # Convert the numeric part to an integer
            'Area Type_Carpet Area': 0,
            'Area Type_Super Area': 0,
            'City_Chennai': 0,
            'City_Delhi': 0,
            'City_Hyderabad': 0,
            'City_Kolkata': 0,
            'City_Mumbai': 0,
            'City_Bangalore': 0
        }

        # Handle one-hot encoding for Area Type and City
        input_data[f"Area Type_{form_data['Area Type']}"] = 1
        input_data[f"City_{form_data['City']}"] = 1

        # Create a DataFrame from the input data and align it with feature columns
        feature_df = pd.DataFrame([input_data], columns=feature_columns).fillna(0)

        # Perform predictions using the loaded models
        prediction_rf = rf_model.predict(feature_df)[0]
        prediction_lgb = lgb_model.predict(feature_df)[0]
        prediction_xgb = xgb_model.predict(feature_df)[0]
        avg_prediction = (prediction_rf + prediction_lgb + prediction_xgb) / 3

        # Calculate yearly and monthly rents
        yearly_rent = (prediction_rf + prediction_xgb) / 12
        monthly_rent = yearly_rent
        
        # Return predictions as a JSON response
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
    Generate a map based on the selected city and return it.
    """
    try:
        city = request.json.get('City')
        city_data = data[data['City'] == city]

        if city_data.empty:
            return jsonify({"success": False, "error": "No data available for the selected city."})

        # Get the center coordinates for the city
        city_lat = city_data['Latitude'].mean()
        city_lon = city_data['Longitude'].mean()

        # Create a Folium map
        city_map = folium.Map(location=[city_lat, city_lon], zoom_start=12)

        # Add markers for each property
        for _, row in city_data.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"{row['Area Locality']}: {row['Rent']} INR"
            ).add_to(city_map)

        # Return the map as HTML
        return jsonify({"success": True, "map": city_map._repr_html_()})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Add your old code here without changing anything in the previous code
@app.route('/old_route', methods=['GET'])
def old_route():
    """
    A placeholder for your old functionality.
    """
    return jsonify({"message": "This is your old route working as before."})

@app.route('/get_average_rent_by_bhk', methods=['GET'])
def get_average_rent_by_bhk():
    try:
        # Group the data by 'BHK' and calculate the average rent
        avg_rent_by_bhk = data.groupby('BHK')['Rent'].mean().reset_index()

        # Return the result as a JSON response
        return jsonify({"success": True, "data": avg_rent_by_bhk.to_dict(orient='records')})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == '__main__':
    app.run(debug=True)
