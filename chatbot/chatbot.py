import json
import re
import os

def load_data():
    # Get the directory of the current file (chatbot.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Build the absolute path to the JSON file in the "data" subfolder
    data_path = os.path.join(current_dir, "data", "real_estate_data.json")
    print("Loading JSON from:", data_path)  # Debug print to verify the path
    with open(data_path, "r", encoding="utf-8") as file:
        return json.load(file)

def search_properties(query):
    data = load_data()
    query = query.lower()

    # Extract BHK, City, and Price from query
    bhk_match = re.search(r"(\d+)\s?bhk", query)
    city_match = re.search(r"(chennai|mumbai|delhi|hyderabad|bangalore|kolkata|pune)", query)
    price_match = re.search(r"under\s?₹?([\d.]+)\s?(lakh|cr)?", query)

    bhk = int(bhk_match.group(1)) if bhk_match else None
    city = city_match.group(1).capitalize() if city_match else None
    price_limit = None

    if price_match:
        price_value = float(price_match.group(1))
        price_unit = price_match.group(2)
        if price_unit == "lakh":
            price_limit = price_value * 1_00_000
        elif price_unit == "cr":
            price_limit = price_value * 1_00_00_000

    print(f"🔍 Searching for: {bhk} BHK | City: {city} | Price < {price_limit}")

    results = []

    # Search in the dataset
    for property in data:
        # Extract city from the property JSON format
        property_city = None
        for key in property:
            if key.startswith("City_") and property[key] is True:
                property_city = key.replace("City_", "").strip()

        if city and city.lower() != property_city.lower():
            continue  # Skip if city doesn't match

        # Extract BHK from the "Property Title"
        property_bhk_match = re.search(r"(\d+)\s?BHK", property["Property Title"], re.IGNORECASE)
        property_bhk = int(property_bhk_match.group(1)) if property_bhk_match else None

        if bhk and property_bhk != bhk:
            continue  # Skip if BHK count doesn't match

        # Convert price to INR (Cr to Rupees)
        property_price = property["Price"] * 1_00_00_000

        if price_limit and property_price > price_limit:
            continue  # Skip if price exceeds limit

        results.append(property)

    # Generate response
    if results:
        response = "🏡 **Matching Properties:**\n\n"
        for prop in results:
            response += f"🏠 **{prop['Property Title']}**\n"
            response += f"💰 **Price:** ₹{prop['Price']} Cr\n"
            response += f"📍 **Location:** {city}\n"
            response += f"📐 **Size:** {prop['Total_Area']} sqft\n"
            response += f"🛏️ **Bedrooms:** {property_bhk}\n"
            response += f"🛁 **Bathrooms:** {prop['Baths']}\n"
            response += f"📜 **Description:** {prop['Description'][:150]}...\n\n"
        return response
    else:
        return "❌ No matching properties found."

# Example: Running the chatbot function in standalone mode
if __name__ == "__main__":
    while True:
        user_input = input("🏡 Real Estate Chatbot\nEnter your query: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! 👋")
            break
        response = search_properties(user_input)
        print(response)
