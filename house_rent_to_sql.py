import sqlite3
import pandas as pd
import os

# Set paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'House_Rent_Dataset.csv')
DB_PATH = os.path.join(BASE_DIR, 'database', 'house_rent.db')

# Load CSV
df = pd.read_csv(CSV_PATH)

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS house_rent (
    Posted_On TEXT,
    BHK INTEGER,
    Rent INTEGER,
    Size INTEGER,
    Floor TEXT,
    Area_Type TEXT,
    Area_Locality TEXT,
    City TEXT,
    Latitude REAL,
    Longitude REAL,
    Furnishing_Status TEXT,
    Tenant_Preferred TEXT,
    Bathroom INTEGER,
    Point_of_Contact TEXT
);
""")

# Insert data
for _, row in df.iterrows():
    cursor.execute("""
    INSERT INTO house_rent (
        Posted_On, BHK, Rent, Size, Floor, Area_Type, Area_Locality,
        City, Latitude, Longitude, Furnishing_Status, Tenant_Preferred,
        Bathroom, Point_of_Contact
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, tuple(row))

# Commit and close
conn.commit()
conn.close()
print("Database and table created successfully.")
