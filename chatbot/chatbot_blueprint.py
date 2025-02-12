from flask import Blueprint, render_template, request, jsonify
from chatbot.chatbot import search_properties  # Import your chatbot function

# Create the blueprint, specifying the template and static folders.
chatbot_bp = Blueprint(
    'chatbot_bp',
    __name__,
    template_folder='templates',  # This folder is relative to the chatbot folder
    static_folder='static'
)

@chatbot_bp.route('/')
def index():
    # Now loads 'chatbot_index.html' from D:\New folder (2)\City Rent\code\chatbot\templates\
    return render_template('chatbot_index.html')

@chatbot_bp.route('/query', methods=['POST'])
def query():
    try:
        data = request.get_json()
        user_query = data.get("query", "").strip()
        if not user_query:
            return jsonify({'response': "❌ Please enter a valid search query."})
        
        response = search_properties(user_query)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f"⚠️ Error: {str(e)}"}), 500
