# RFID Student Wallet Application

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

> A modern solution for educational institutions combining RFID card authentication with face recognition technology for student identity management, attendance tracking, wallet transactions, library services, and transportation monitoring.


## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [AI-Powered Features](#ai-powered-features)
- [Installation](#installation)
- [Firebase Setup](#firebase-setup)
- [Running the Application](#running-the-application)
- [Technical Architecture](#technical-architecture)
  - [Face Recognition System](#face-recognition-system)
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

## 🤖 AI-Powered Features

### Smart Wallet Recharge Suggestions
The application uses machine learning algorithms to provide personalized wallet recharge recommendations:
- **Spending Pattern Analysis**: Learns from individual student transaction history
- **Predictive Modeling**: Forecasts future spending needs based on historical patterns
- **Contextual Awareness**: Considers factors like day of week, upcoming events, and seasonal variations
- **Anomaly Detection**: Identifies unusual spending patterns that may require attention
- **Adaptive Recommendations**: Suggestions improve over time as the system learns from user behavior

### Intelligent Library Recommendations
The library system implements a sophisticated recommendation engine:
- **Collaborative Filtering**: Suggests books based on what similar students have enjoyed
- **Content-Based Analysis**: Recommends books with similar themes, authors, or genres
- **Reading Level Assessment**: Considers the student's reading history to suggest appropriate difficulty levels
- **Cross-Domain Insights**: Leverages academic performance data to suggest relevant educational materials
- **Real-time Recommendations**: Provides suggestions at the moment of book return based on just-completed readings

These AI features leverage Firebase's machine learning capabilities combined with custom algorithms implemented in Python, providing a personalized experience that improves with usage.

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

### 👨‍💻 Admin RFID for accessing and creating accounts is _0006435835_

## 🔬 Technical Architecture

### Backend Processes

Here's what's happening behind the scenes in the application:

#### Authentication Flow
1. **RFID Simulation**: When a student presents their "RFID card" (simulated in this proof-of-concept)
2. **Student Identification**: The system retrieves the student profile from Firebase
3. **Face Recognition**: The webcam captures the student's face and compares it with stored embeddings
4. **Verification**: Both factors must match for successful authentication

#### Database Operations
- **Real-time Synchronization**: Firebase Firestore provides real-time updates across all interfaces
- **Transaction Safety**: All financial transactions use atomic operations to prevent data corruption
- **Document-Based Structure**: Data is organized in collections with document IDs for efficient retrieval

### Face Recognition System

The face recognition system is one of the core components of the application, providing secure biometric authentication:

#### Technical Implementation
- **Face Detection**: Uses HOG (Histogram of Oriented Gradients) for initial face detection
- **Facial Landmark Detection**: Identifies 68 specific points on the face to create a detailed map
- **Face Encoding**: Generates a 128-dimensional face embedding vector using a deep neural network
- **Recognition Algorithm**: Employs a combination of:
  - Linear SVM classifier for known faces
  - Distance-based matching with configurable tolerance thresholds

#### Enrollment Process
1. **Multiple Sample Collection**: Captures 5-10 images of each student from different angles
2. **Quality Assessment**: Analyzes image quality, lighting, and facial expression
3. **Embedding Generation**: Creates and stores face encodings in a secure format
4. **Profile Association**: Links face data with student records in Firebase

#### Anti-Spoofing Measures
- **Liveness Detection**: Requires random micro-movements (e.g., blinking, slight head turn)
- **Depth Analysis**: Uses webcam image patterns to distinguish 3D faces from 2D photos
- **Texture Analysis**: Examines skin texture patterns that are difficult to replicate
- **Temporal Consistency**: Verifies consistent facial features across multiple frames

#### Performance Optimizations
- **Parallel Processing**: Utilizes multi-threading for simultaneous detection and recognition
- **Resolution Scaling**: Dynamically adjusts image resolution based on computational resources
- **Embedding Caching**: Stores frequently accessed face embeddings in memory
- **Frame Sampling**: Processes every n-th frame to reduce computational load

#### Privacy Considerations
- **Data Protection**: Face embeddings are stored as encrypted vectors, not actual images
- **Local Processing**: All face recognition happens on the local device, not in the cloud
- **Consent Management**: Includes a system for managing and revoking biometric consent
- **Data Lifecycle**: Implements automatic purging of facial data when no longer needed

#### AI Processing Pipeline

##### Wallet Recharge Recommendations
1. **Data Collection**: Transaction history is continuously collected and stored in Firebase
2. **Feature Engineering**:
   - Transaction amounts are normalized
   - Temporal features are extracted (day of week, time of day)
   - Spending categories are encoded
   - Seasonal patterns are identified
3. **Model Training**:
   - A gradient boosting model is trained periodically on each student's data
   - The model predicts future spending needs based on historical patterns
   - Hyperparameters are automatically tuned using cross-validation
4. **Inference**:
   - When a student's balance falls below a threshold, the model is queried
   - The recharge amount is calculated based on predicted spending
   - A confidence score determines how the recommendation is presented

##### Library Book Recommendations
1. **Matrix Creation**: A sparse user-item matrix is constructed from lending history
2. **Embedding Generation**:
   - Books are represented as embeddings using TF-IDF on their descriptions
   - Students are represented by their aggregate reading preferences
3. **Similarity Computation**:
   - Cosine similarity is used to find similar books
   - K-nearest neighbors algorithm identifies students with similar reading habits
4. **Recommendation Generation**:
   - When a book is returned, the system immediately triggers recommendation generation
   - Multiple recommendation strategies are employed in parallel:
     - Similar books by content
     - Books read by similar students
     - Books matching current academic subjects
   - Results are ranked by relevance score and de-duplicated

#### Optimization Techniques
- **Caching**: Frequently accessed data is cached to reduce Firebase reads
- **Batch Operations**: Database writes are batched when possible
- **Lazy Loading**: Heavy computations like face recognition are performed only when necessary
- **Local Model Inference**: AI models run locally to reduce latency and cloud dependency

## 🔬 Technical Architecture

### Backend Processes

Here's what's happening behind the scenes in the application:

#### Authentication Flow
1. **RFID Simulation**: When a student presents their "RFID card" (simulated in this proof-of-concept)
2. **Student Identification**: The system retrieves the student profile from Firebase
3. **Face Recognition**: The webcam captures the student's face and compares it with stored embeddings
4. **Verification**: Both factors must match for successful authentication

#### Database Operations
- **Real-time Synchronization**: Firebase Firestore provides real-time updates across all interfaces
- **Transaction Safety**: All financial transactions use atomic operations to prevent data corruption
- **Document-Based Structure**: Data is organized in collections with document IDs for efficient retrieval

### Face Recognition System

The face recognition system is one of the core components of the application, providing secure biometric authentication:

#### Technical Implementation
- **Face Detection**: Uses HOG (Histogram of Oriented Gradients) for initial face detection
- **Facial Landmark Detection**: Identifies 68 specific points on the face to create a detailed map
- **Face Encoding**: Generates a 128-dimensional face embedding vector using a deep neural network
- **Recognition Algorithm**: Employs a combination of:
  - Linear SVM classifier for known faces
  - Distance-based matching with configurable tolerance thresholds

#### Enrollment Process
1. **Multiple Sample Collection**: Captures 5-10 images of each student from different angles
2. **Quality Assessment**: Analyzes image quality, lighting, and facial expression
3. **Embedding Generation**: Creates and stores face encodings in a secure format
4. **Profile Association**: Links face data with student records in Firebase

#### Anti-Spoofing Measures
- **Liveness Detection**: Requires random micro-movements (e.g., blinking, slight head turn)
- **Depth Analysis**: Uses webcam image patterns to distinguish 3D faces from 2D photos
- **Texture Analysis**: Examines skin texture patterns that are difficult to replicate
- **Temporal Consistency**: Verifies consistent facial features across multiple frames

#### Performance Optimizations
- **Parallel Processing**: Utilizes multi-threading for simultaneous detection and recognition
- **Resolution Scaling**: Dynamically adjusts image resolution based on computational resources
- **Embedding Caching**: Stores frequently accessed face embeddings in memory
- **Frame Sampling**: Processes every n-th frame to reduce computational load

#### Privacy Considerations
- **Data Protection**: Face embeddings are stored as encrypted vectors, not actual images
- **Local Processing**: All face recognition happens on the local device, not in the cloud
- **Consent Management**: Includes a system for managing and revoking biometric consent
- **Data Lifecycle**: Implements automatic purging of facial data when no longer needed

#### AI Processing Pipeline

##### Wallet Recharge Recommendations
1. **Data Collection**: Transaction history is continuously collected and stored in Firebase
2. **Feature Engineering**:
   - Transaction amounts are normalized
   - Temporal features are extracted (day of week, time of day)
   - Spending categories are encoded
   - Seasonal patterns are identified
3. **Model Training**:
   - A gradient boosting model is trained periodically on each student's data
   - The model predicts future spending needs based on historical patterns
   - Hyperparameters are automatically tuned using cross-validation
4. **Inference**:
   - When a student's balance falls below a threshold, the model is queried
   - The recharge amount is calculated based on predicted spending
   - A confidence score determines how the recommendation is presented

##### Library Book Recommendations
1. **Matrix Creation**: A sparse user-item matrix is constructed from lending history
2. **Embedding Generation**:
   - Books are represented as embeddings using TF-IDF on their descriptions
   - Students are represented by their aggregate reading preferences
3. **Similarity Computation**:
   - Cosine similarity is used to find similar books
   - K-nearest neighbors algorithm identifies students with similar reading habits
4. **Recommendation Generation**:
   - When a book is returned, the system immediately triggers recommendation generation
   - Multiple recommendation strategies are employed in parallel:
     - Similar books by content
     - Books read by similar students
     - Books matching current academic subjects
   - Results are ranked by relevance score and de-duplicated

#### Optimization Techniques
- **Caching**: Frequently accessed data is cached to reduce Firebase reads
- **Batch Operations**: Database writes are batched when possible
- **Lazy Loading**: Heavy computations like face recognition are performed only when necessary
- **Local Model Inference**: AI models run locally to reduce latency and cloud dependency

## ⚙️ Configuration

The application can be configured through:
- `config.json`: General application settings
- `firebase_config.json`: Firebase connection settings
- `security_settings.json`: Face recognition security parameters
- `ai_settings.json`: Configure AI recommendation strength and parameters

## 🛠️ Technologies

- **Frontend**: Python tkinter for user interface
- **Backend**: Python with Firebase
- **Face Recognition**: face_recognition library (based on dlib)
- **Database**: Firebase Firestore
- **AI/ML Libraries**: scikit-learn, TensorFlow Lite
- **Additional Libraries**: OpenCV, NumPy, Pandas

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the terms of the [MIT License](https://github.com/your-username/your-repo/blob/main/LICENSE).

---

*Note: This is a proof-of-concept application that simulates RFID readers while using actual face recognition technology.*
