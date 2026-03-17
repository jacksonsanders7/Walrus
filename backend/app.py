"""
ChatGPT AI Clone - Main Application
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import openai
from datetime import datetime
import json
from pathlib import Path

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

# Chat history storage
CHAT_HISTORY_FILE = 'chat_history.json'

class ChatGPTClone:
    def __init__(self):
        self.conversations = {}
        self.load_conversations()
    
    def load_conversations(self):
        """Load conversation history from file"""
        if Path(CHAT_HISTORY_FILE).exists():
            with open(CHAT_HISTORY_FILE, 'r') as f:
                self.conversations = json.load(f)
    
    def save_conversations(self):
        """Save conversation history to file"""
        with open(CHAT_HISTORY_FILE, 'w') as f:
            json.dump(self.conversations, f, indent=2)
    
    def create_conversation(self, conversation_id):
        """Create a new conversation"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                'id': conversation_id,
                'title': 'New Chat',
                'messages': [],
                'created_at': datetime.now().isoformat()
            }
            self.save_conversations()
    
    def add_message(self, conversation_id, role, content):
        """Add a message to a conversation"""
        if conversation_id not in self.conversations:
            self.create_conversation(conversation_id)
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self.conversations[conversation_id]['messages'].append(message)
        self.save_conversations()
        return message
    
    def get_conversation(self, conversation_id):
        """Get a conversation"""
        return self.conversations.get(conversation_id)
    
    def get_all_conversations(self):
        """Get all conversations"""
        return self.conversations
    
    def delete_conversation(self, conversation_id):
        """Delete a conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            self.save_conversations()
            return True
        return False
    
    def generate_response(self, conversation_id, user_message):
        """Generate AI response using OpenAI API"""
        try:
            # Add user message
            self.add_message(conversation_id, 'user', user_message)
            
            # Get conversation history for context
            conversation = self.get_conversation(conversation_id)
            messages = [
                {'role': msg['role'], 'content': msg['content']}
                for msg in conversation['messages'][:-1]  # Exclude the just-added message
            ]
            messages.append({'role': 'user', 'content': user_message})
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=messages,
                temperature=0.7,
                max_tokens=2048
            )
            
            # Extract response
            ai_message = response['choices'][0]['message']['content']
            self.add_message(conversation_id, 'assistant', ai_message)
            
            return ai_message
        
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            self.add_message(conversation_id, 'assistant', error_message)
            return error_message

# Initialize chatbot
chatbot = ChatGPTClone()

# API Routes
@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations"""
    return jsonify(chatbot.get_all_conversations())

@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    """Create a new conversation"""
    data = request.json
    conversation_id = data.get('id', str(datetime.now().timestamp()))
    chatbot.create_conversation(conversation_id)
    return jsonify(chatbot.get_conversation(conversation_id))

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get a specific conversation"""
    conversation = chatbot.get_conversation(conversation_id)
    if conversation:
        return jsonify(conversation)
    return jsonify({'error': 'Conversation not found'}), 404

@app.route('/api/conversations/<conversation_id>/messages', methods=['POST'])
def send_message(conversation_id):
    """Send a message and get AI response"""
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    try:
        response = chatbot.generate_response(conversation_id, user_message)
        return jsonify({
            'user_message': user_message,
            'ai_response': response,
            'conversation': chatbot.get_conversation(conversation_id)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation"""
    if chatbot.delete_conversation(conversation_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Conversation not found'}), 404

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
