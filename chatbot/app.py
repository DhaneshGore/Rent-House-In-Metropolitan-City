from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from chatbot import search_properties

app = Flask(__name__)
CORS(app)  # ✅ Allow front-end requests (CORS enabled)

# 🏡 Home Page Route
@app.route('/')
def home():
    return render_template('chatbot_index.html')  # Ensure 'index.html' exists in 'templates/' folder

# 🔍 Search Route (Handles Chatbot Queries)
@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        user_query = data.get("query", "").strip()

        if not user_query:
            return jsonify({'response': "❌ Please enter a valid search query."})

        # 🏠 Call search function from chatbot.py
        response = search_properties(user_query)

        # ✅ Send response to front-end
        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'response': f"⚠️ Error: {str(e)}"}), 500  # Handle errors

# 🚀 Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)
