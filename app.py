from flask import Flask, request, render_template, abort, url_for, jsonify
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import uuid
import random
import string
import threading
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')

# Generate or load a key for encryption/decryption
key_path = 'key.key'
if os.path.exists(key_path):
    with open(key_path, 'rb') as key_file:
        key = key_file.read()
else:
    key = Fernet.generate_key()
    with open(key_path, 'wb') as key_file:
        key_file.write(key)

cipher_suite = Fernet(key)

# Thread-safe in-memory storage for messages and chats
storage = {}
storage_lock = threading.Lock()

# Store active chats and their expiration times
active_chats = {}
user_mapping = {}  # Map user IPs to Anonymous IDs

@app.route('/')
def index():
    encryption_info = "We use Fernet encryption (AES-256) for your messages, ensuring secure and strong protection."
    return render_template('index.html', encryption_info=encryption_info)

@app.route('/livechat')
def livechat():
    return render_template('livechat.html')

@app.route('/create_chat', methods=['POST'])
def create_chat():
    expiration_time = int(request.form.get('expiration_time', 30))  # Default: 30 minutes
    chat_id = str(uuid.uuid4())
    expiration = datetime.utcnow() + timedelta(minutes=expiration_time)
    
    active_chats[chat_id] = {
        'messages': [],
        'expires_at': expiration,
        'creator': request.remote_addr  # Using IP address as a basic creator identifier
    }

    chat_link = url_for('chat_room', chat_id=chat_id, _external=True)
    return render_template('chat_created.html', chat_link=chat_link, expiration_time=expiration_time)

@app.route('/chat/<chat_id>', methods=['GET', 'POST'])
def chat_room(chat_id):
    chat = active_chats.get(chat_id)

    if not chat or datetime.utcnow() > chat['expires_at']:
        return "Chat has expired or does not exist.", 404

    user_ip = request.remote_addr
    if user_ip not in user_mapping:
        user_mapping[user_ip] = f"Anonymous{len(user_mapping)}"

    if request.method == 'POST':
        message = request.json.get('message')
        if message:
            chat['messages'].append({
                'user': user_mapping[user_ip],
                'message': message,
                'timestamp': datetime.utcnow()
            })
            return jsonify(success=True)

    return render_template('chat_room.html', chat_id=chat_id)

@app.route('/chat/<chat_id>/messages', methods=['GET'])
def get_messages(chat_id):
    chat = active_chats.get(chat_id)

    if not chat or datetime.utcnow() > chat['expires_at']:
        return jsonify(error="Chat has expired or does not exist."), 404

    return jsonify(chat['messages'])

@app.route('/terminate_chat', methods=['POST'])
def terminate_chat():
    chat_id = request.form.get('chat_id')

    if not chat_id:
        return jsonify({"error": "Chat ID is required."}), 400

    chat = active_chats.get(chat_id)

    if not chat:
        return render_template('chat_terminated.html', success=False, message="Chat not found or already terminated."), 404

    # Only the creator of the chat should be allowed to terminate it
    chat_creator = chat.get('creator')
    current_user = request.remote_addr  # Assuming the user's IP address as identifier

    if chat_creator != current_user:
        return render_template('chat_terminated.html', success=False, message="You are not authorized to terminate this chat."), 403

    # Terminate the chat
    del active_chats[chat_id]

    return render_template('chat_terminated.html', success=True, message="Chat terminated successfully.")

@app.route('/encrypt', methods=['POST'])
def encrypt_message():
    data = request.form
    message = data.get('message')
    expiration_minutes = int(data.get('expiration_time', 30))  # Default to 30 minutes

    if not message:
        return render_template('index.html', error="No message provided.")

    if len(message) > 1000:
        return render_template('index.html', error="Message is too long. Maximum 1000 characters allowed.")

    # Verwende das eingegebene Passwort oder lasse es leer
    password = data.get('password')
    password_in_url = f"?password={password}" if password else ""

    # Encrypt the message
    encrypted_message = cipher_suite.encrypt(message.encode()).decode()

    # Generate a unique ID for the message
    message_id = str(uuid.uuid4())

    # Set expiration time for the message
    expiration_time = datetime.utcnow() + timedelta(minutes=expiration_minutes)

    # Store the encrypted message and expiration in memory
    with storage_lock:
        storage[message_id] = {
            "encrypted_message": encrypted_message,
            "expires_at": expiration_time
        }

    # Generate a link to retrieve the message
    link = url_for('decrypt_message', message_id=message_id, _external=True) + password_in_url
    expiration_seconds = expiration_minutes * 60  # Convert to seconds for the timer
    return render_template('index.html', link=link, password=password if password else None, expiration_time=expiration_seconds)

@app.route('/decrypt/<message_id>', methods=['GET', 'POST'])
def decrypt_message(message_id):
    with storage_lock:
        message_entry = storage.get(message_id)

        if not message_entry:
            return abort(404, "Message not found or already accessed.")

        if datetime.utcnow() > message_entry['expires_at']:
            storage.pop(message_id, None)
            return abort(410, "The message has expired.")

        if request.method == 'GET':
            return render_template('confirm.html', message_id=message_id)

        elif request.method == 'POST':
            encrypted_message = storage.pop(message_id, {}).get('encrypted_message')
            if not encrypted_message:
                return abort(404, "Message not found or already accessed.")

            # Decrypt the message
            decrypted_message = cipher_suite.decrypt(encrypted_message.encode()).decode()
            return render_template('message.html', message=decrypted_message)

if __name__ == '__main__':
    app.run(debug=True)
