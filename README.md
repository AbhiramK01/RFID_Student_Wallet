# RFID Student Wallet Application

> A student management system combining simulated RFID card authentication with face recognition technology.

## 📋 Features

- **Face Recognition**: Basic face detection and matching for student identification
- **Attendance Tracking**: Record student attendance using RFID and face verification
- **Wallet Management**: Simple digital wallet for canteen transactions
- **Library System**: Basic book lending and return functionality
- **Transport Tracking**: Record bus boarding/offboarding events
- **Student Dashboard**: View transactions, attendance, and library activities
- **Smart Recommendations**: Data-driven suggestions for wallet recharge and book selection

## 🔧 Installation

### Prerequisites
- Python 3.8 or higher
- Webcam for facial recognition
- Firebase account

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

This application uses Firebase for backend services:

1. **Create a Firebase Project**:
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create a new project

2. **Set Up Firestore Database**:
   - Enable Firestore Database in test mode

3. **Generate Service Account Credentials**:
   - Go to Project Settings > Service Accounts
   - Generate and download the private key JSON file
   - Save it as `serviceAccountKey.json` in the project root directory

4. **Configure the Application**:
   - Create a `firebase_config.json` file with your Firebase project details

## 🚀 Running the Application

```bash
# Make sure your virtual environment is activated
python run.py
```

### Interfaces
- **Admin**: Manage students and system settings
- **Classroom**: Take attendance
- **Canteen**: Process wallet transactions
- **Library**: Handle book lending/returns
- **Bus**: Track transportation
- **Student**: Access student services

### Admin RFID
Admin RFID for accessing and creating accounts is _0006435835_

## 🔬 Implementation Details

### Face Recognition
- Basic face detection using the face_recognition library
- Simple matching against stored face encodings
- Single-sample enrollment process

### Recommendation Systems
- **Wallet Recharge Suggestions**: Analyzes student's spending history over the past 30 days to calculate a reasonable recharge amount based on their weekly average spending
- **Book Recommendations**:
  - **Similar Books**: Suggests books based on what other students who borrowed the same book have read
  - **Reading Preferences**: Recommends books from categories the student has previously shown interest in
  - Both systems include fallback options when insufficient data is available

### Database Structure
- Firebase Firestore collections for:
  - students
  - library_records
  - transactions
  - attendance
  - bus_records

## 🛠️ Technologies

- **Frontend**: Python tkinter
- **Backend**: Python with Firebase
- **Face Recognition**: face_recognition library (based on dlib)
- **Database**: Firebase Firestore
- **Additional Libraries**: OpenCV

## License
This project is licensed under the terms of the [MIT License](https://github.com/your-username/your-repo/blob/main/LICENSE).


---

*Note: This is a proof-of-concept application that simulates RFID readers while using basic face recognition technology.*
