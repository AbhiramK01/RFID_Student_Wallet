# RFID Student Wallet Application

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

> A modern solution for educational institutions combining RFID card authentication with face recognition technology for student identity management, attendance tracking, wallet transactions, library services, and transportation monitoring.

![Application Screenshot](./assets/screenshot.png)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Firebase Setup](#firebase-setup)
- [Configuration](#configuration)
- [Technologies](#technologies)
- [Contributing](#contributing)
- [License](#license)

## 🔍 Overview

The RFID Student Wallet Application provides a unified platform for managing various student services using a combination of RFID card authentication and facial recognition. This proof-of-concept application simulates RFID readers while implementing actual face recognition technology to demonstrate the potential of this integrated approach.

## ✨ Features

### Security and Authentication
- Multi-angle facial recognition with anti-spoofing technology
- RFID card integration for two-factor authentication
- Configurable security levels for different operations

### Student Services
- **Attendance System**: Automated tracking with timestamp recording
- **Digital Wallet**: Secure transactions with spending analytics and AI-based recharge recommendations
- **Library Management**: Book circulation system with personalized reading suggestions
- **Transport Tracking**: Bus boarding/offboarding monitoring with parental notifications
- **Student Dashboard**: Unified access to all services and personal information

### Administrative Tools
- Comprehensive student management interface
- Data analytics and reporting
- System configuration and monitoring

## 🔧 Installation

### Prerequisites
- Python 3.8 or higher
- Webcam for facial recognition
- Firebase account
- Required Python packages

### Setup Steps
```bash
# Clone the repository
git clone https://github.com/yourusername/rfid-student-wallet.git
cd rfid-student-wallet

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🔥 Firebase Setup

This application uses Firebase for backend services. Follow these steps to set up Firebase:

1. **Create a Firebase Project**:
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Click "Add project" and follow the prompts to create a new project
   - Enable Google Analytics if desired

2. **Set Up Firestore Database**:
   - In the Firebase console, click on "Firestore Database"
   - Click "Create database"
   - Start in test mode (you can adjust security rules later)
   - Choose a database location closest to your users

3. **Create Authentication Methods**:
   - Go to "Authentication" in the Firebase console
   - Enable Email/Password authentication
   - (Optional) Set up other authentication methods as needed

4. **Generate Service Account Credentials**:
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Save the downloaded JSON file as `serviceAccountKey.json` in the project root directory

5. **Configure the Application**:
   - Create a `firebase_config.json` file in the project root with the following structure:
   ```json
   {
     "apiKey": "YOUR_API_KEY",
     "authDomain": "YOUR_PROJECT_ID.firebaseapp.com",
     "projectId": "YOUR_PROJECT_ID",
     "storageBucket": "YOUR_PROJECT_ID.appspot.com",
     "messagingSenderId": "YOUR_MESSAGING_SENDER_ID",
     "appId": "YOUR_APP_ID",
     "databaseURL": "https://YOUR_PROJECT_ID.firebaseio.com"
   }
   ```
   - These values can be found in your Firebase project settings

6. **Initialize Firestore Collections**:
   - The application will automatically create necessary collections on first run
   - Alternatively, you can manually create the following collections:
     - `students`
     - `library_records`
     - `transactions`
     - `attendance`
     - `bus_records`

## 🚀 Running the Application

### Starting the Application
```bash
# Make sure your virtual environment is activated
python run.py
```

### First-Time Setup
1. On first launch, you'll be prompted to create an admin account
2. Use the admin interface to:
   - Add student records
   - Configure system settings
   - Set up library inventory
   - Initialize wallet balances

### Interface Navigation
The main menu provides access to all modules:
- **Admin**: Enter admin credentials for full system access
- **Classroom**: Select a class to take attendance
- **Canteen**: Process food purchases and wallet recharges
- **Library**: Manage book circulation
- **Bus**: Track transportation
- **Student**: Access individual student portal

### Test Accounts
For testing, you can use these credentials:
- Admin: admin@school.edu / password
- Student: student@school.edu / student123

## ⚙️ Configuration

The application can be configured through:
- `config.json`: General application settings
- `firebase_config.json`: Firebase connection settings
- `security_settings.json`: Face recognition security parameters

## 🛠️ Technologies

- **Frontend**: Python tkinter for user interface
- **Backend**: Python with Firebase
- **Face Recognition**: face_recognition library (based on dlib)
- **Database**: Firebase Firestore
- **Additional Libraries**: OpenCV, NumPy, Pandas

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*Note: This is a proof-of-concept application that simulates RFID readers while using actual face recognition technology.*