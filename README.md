# Password Manager App

## About the App
The **Password Manager App** is a secure and user-friendly tool designed to help users store and manage their passwords efficiently. It encrypts passwords and protects access with a master password. A security phrase is used for resetting the master password. The app is built with Python, leveraging `Tkinter` for the GUI and `cryptography` for robust encryption.

## Features
- Save and retrieve encrypted passwords.
- Secure access with a master password.
- Reset master password using a security phrase.
- View saved passwords in a scrollable table.
- Clean and modern UI with an About section.

## Technology Stack
- **Languages**: Python
- **Libraries**: Tkinter, Cryptography
- **Packaging Tool**: PyInstaller

## Getting Started
Run the app as a Python script or as a standalone `.exe` built using PyInstaller. Ensure a clean environment for a virus-free executable.

## Making installer
pyinstaller --onefile --noconsole --manifest app.manifest password_manager.py



## License
This project is open-source and free to use under the MIT License.
