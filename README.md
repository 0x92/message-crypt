# Self-Destructing Messages inspired by Privnote

![image](https://github.com/user-attachments/assets/20760204-29ef-4304-a130-697c401cb69c)

![image](https://github.com/user-attachments/assets/9ba9aa87-d2b7-4275-9919-d943aa12c7a8)

![image](https://github.com/user-attachments/assets/e0477c15-bc2c-4577-930b-bfa89677f9a2)

![image](https://github.com/user-attachments/assets/9f2c8eb3-349f-4941-9fda-84fd390a2589)


This is a Flask-based web application that allows users to encrypt messages and generate a unique link to share them. Once the link is accessed, the message self-destructs and cannot be viewed again.

## Features
- **Secure Encryption**: Messages are encrypted using the `cryptography` library.
- **Self-Destruction**: Links are valid for a single use only.
- **Responsive Design**: Modern UI with animations and responsive layouts.
- **Ease of Use**: Generate, share, and view messages effortlessly.

## Getting Started

### Prerequisites
- Python 3.7 or higher
- `pip` (Python package manager)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/self-destructing-messages.git
   cd self-destructing-messages
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate   # On Windows: env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and go to:
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Usage
1. **Encrypt a Message**:
   - Enter your message in the provided text area.
   - Click "Generate Link" to encrypt the message and get a unique link.

2. **Share the Link**:
   - Copy the generated link and share it securely with the recipient.

3. **View the Message**:
   - Open the link to view the decrypted message.
   - The message self-destructs after being viewed.

## Technologies Used
- **Backend**: Flask
- **Frontend**: HTML, CSS, Bootstrap
- **Encryption**: `cryptography` library

## File Structure
```
self_destructing_messages/
├── static/
│   ├── css/
│   │   └── styles.css
├── templates/
│   ├── index.html
│   ├── confirm.html
│   └── message.html
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add feature-name'`).
4. Push to the branch (`git push origin feature-name`).
5. Create a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments
- Inspired by the concept of secure, self-destructing messages.
- Built using Flask and Bootstrap for simplicity and responsiveness.
