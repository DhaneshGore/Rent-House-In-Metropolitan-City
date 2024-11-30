# Rent-House-In-Metropolitan-City
This project is a Flask-based web application that provides users with predictions for house rents based on several factors (e.g., city, BHK, area type, floor) and displays property locations on an interactive map. It leverages pre-trained machine learning models for prediction and Folium for map rendering.

# Features
- Predict house rent based on various factors.
* Random Forest
* LightGBM
* XGBoost
- Display property locations on an interactive map.
- Utilize pre-trained machine learning models for accurate predictions.
- Leverage Folium for map rendering and visualization.

# Tech Stack
- Backend: Flask, Python
- Frontend: HTML, JavaScript (for AJAX requests), Jinja2
- Database: CSV file used as a mock database (House_Rent_Dataset.csv)
- Machine Learning Models: Pre-trained models (rf_model.pkl, lgb_model.pkl, xgb_model.pkl)
- Mapping: Folium for generating interactive maps

# Installation
1. Clone the repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Start the Flask server by running `python app.py`.
4. Open a web browser and navigate to `http://localhost:5000` to access the application.

# Project Structure
house-rent-prediction/
├── app.py               # Main Flask application
├── models/
│   ├── rf_model.pkl     # Random Forest model
│   ├── lgb_model.pkl    # LightGBM model
│   ├── xgb_model.pkl    # XGBoost model
│   └── feature_columns.pkl  # Columns used during training
├── data/
│   └── House_Rent_Dataset.csv  # Dataset for predictions and map rendering
├── templates/
|   ├── index.html    # Main page with map and prediction form
│   ├── interactive.html # Homepage with map and prediction interface
│   └── predict.html     # Prediction form page
├── static/
│   └── css/             # Optional CSS for styling
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation

# How to Use
1. Clone the repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Start the Flask server by running `python app.py`.
4. Open a web browser and navigate to `http://localhost:5000` to access the application.

# Models
The project includes pre-trained machine learning models for predicting house rent based on different factors. These models are stored in the `models` directory and can be used for prediction by calling the appropriate functions.


# Data
The project uses a dataset of house rent prices in metropolitan cities. The dataset is stored in the `data` directory and can be loaded using the `pandas` library.

# API Endpoints
The project provides the following API endpoints:
- `/predict`: Predicts house rent based on user input.
- `/map`: Renders an interactive map of property locations based on user input.

# License
This project is licensed under the MIT License.