from flask import Flask, request, jsonify, render_template, redirect, url_for, abort
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import uuid
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

# Thread-safe in-memory storage for messages
storage = {}
storage_lock = threading.Lock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_message():
    data = request.form
    message = data.get('message')

    if not message:
        return render_template('index.html', error="No message provided.")

    if len(message) > 1000:
        return render_template('index.html', error="Message is too long. Maximum 1000 characters allowed.")

    # Encrypt the message
    encrypted_message = cipher_suite.encrypt(message.encode()).decode()

    # Generate a unique ID for the message
    message_id = str(uuid.uuid4())

    # Set expiration time for the message
    expiration_time = datetime.utcnow() + timedelta(minutes=30)

    # Store the encrypted message and expiration in memory
    with storage_lock:
        storage[message_id] = {"encrypted_message": encrypted_message, "expires_at": expiration_time}

    # Generate a link to retrieve the message
    link = url_for('decrypt_message', message_id=message_id, _external=True)
    return render_template('index.html', link=link)

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
