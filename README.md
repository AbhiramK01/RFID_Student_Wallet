# RFID Student Wallet Application with Advanced Face Recognition

An all-in-one student management system with RFID card support and high-security face recognition for attendance tracking, wallet management, library management, and transport tracking.

## Key Features

- **High-Security Face Recognition**: Advanced biometric verification using multi-angle face data and strict matching algorithms
- **Student Attendance System**: Mark attendance using RFID + face recognition to prevent proxy attendance
- **Student Wallet**: Process payments and recharge student wallets using RFID + PIN
- **Library Management**: Streamlined book lending and returning with RFID
- **Transport Management**: Track student bus boarding/offboarding and notify parents
- **AI-powered Recommendations**: Suggest wallet recharge amounts and book recommendations

## System Requirements

- Python 3.8 or higher
- Internet connection (for Firebase Firestore)
- Windows, macOS, or Linux operating system
- Webcam for face recognition (720p or higher recommended)
- Minimum 4GB RAM recommended (8GB recommended for better face recognition performance)
- Reasonable GPU recommended for faster face recognition

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/RFID-Student-Wallet.git
   cd RFID-Student-Wallet
   ```

2. Create a virtual environment (recommended):
   ```
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

   > **Note for dlib and face_recognition installation**: 
   > These libraries require specific setup:
   >
   > **Windows**:
   > 1. Install Visual Studio Build Tools with C++ support
   > 2. Install CMake
   > 3. You may need to install dlib separately: `pip install dlib`
   > 4. Then install face_recognition: `pip install face_recognition`
   >
   > **macOS**:
   > ```
   > brew install cmake
   > xcode-select --install
   > pip install dlib
   > pip install face_recognition
   > ```
   >
   > **Linux**:
   > ```
   > sudo apt-get install -y build-essential cmake
   > sudo apt-get install -y libopenblas-dev liblapack-dev
   > sudo apt-get install -y libx11-dev libgtk-3-dev
   > pip install dlib
   > pip install face_recognition
   > ```
   >
   > If you encounter issues, you can try using pre-built wheels:
   > ```
   > pip install https://github.com/jloh02/dlib/releases/download/v19.22/dlib-19.22.99-cp38-cp38-win_amd64.whl
   > pip install face_recognition
   > ```

4. Set up Firebase:
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
   - Enable Firestore database
   - Download your service account key file from Project Settings > Service accounts
   - Save it as `serviceAccountKey.json` in the project root directory
   - Update `firebase_config.json` with your Firebase project details:
     ```json
     {
       "apiKey": "your-api-key",
       "authDomain": "your-project-id.firebaseapp.com",
       "projectId": "your-project-id",
       "storageBucket": "your-project-id.appspot.com",
       "serviceAccount": "serviceAccountKey.json"
     }
     ```

## Running the Application

1. After completing the installation steps, run the application:
   ```
   # Activate the virtual environment if not already active
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate

   # Run the application
   python src/main.py
   ```

2. The main menu will appear with options for different interfaces.

## Login Information for Testing

For testing purposes, you can use these pre-configured credentials:

1. **Admin Interface**:
   - RFID: 0006435835

2. **Student Accounts**:
   - RFID: 0123456789 (Computer Science, Year 3)
   - RFID: 0012345678 (Electrical Engineering, Year 2)
   - RFID: 0012345679 (Mechanical Engineering, Year 1)

## User Interfaces Guide

### 1. Admin Interface

The Admin Interface provides comprehensive management tools for the entire system:

- **Student Management**:
  - Add new students with comprehensive face registration (7 angles)
  - Update existing student information and face data
  - Delete student records
  - View all student information

- **Face Registration**:
  - High-security face data collection with guided positioning
  - 7 different face angles captured for maximum security
  - Quality checks for face size, lighting, and uniqueness

- **Bus Route Management**:
  - Create, edit and delete bus routes
  - Assign students to specific routes

- **Data Export**:
  - Export student data, attendance records, wallet transactions, etc. to CSV
  - Generate reports for analysis

- **System Management**:
  - Clear database (use with caution!)
  - Initialize sample data

### 2. Classroom Interface

The Classroom Interface is designed for taking attendance with high-security face verification:

- **Setup**:
  - Select department, year, and section to define the classroom
  - View current date and time for attendance recording

- **Attendance Marking**:
  - Students present their RFID cards
  - System verifies identity through multi-step face recognition:
    1. Captures face image from webcam
    2. Compares with stored face encodings (7 different angles)
    3. Requires multiple successful matches with consistency checks
    4. Uses strict tolerance (0.42) to prevent false matches
  - Visually displays the verification process with distance metrics
  - Marks attendance only after successful verification

- **Attendance Management**:
  - View current attendance for the day
  - Check attendance history for specific students
  - Export attendance data to CSV

### 3. Canteen Interface

The Canteen Interface manages student wallet transactions:

- **Purchase Processing**:
  - Verify student via RFID
  - Process purchases (debit from wallet)
  - Record transaction details

- **Wallet Management**:
  - View current wallet balance
  - Recharge student wallets (credit)
  - View transaction history

- **Reporting**:
  - Daily transaction reports
  - Low balance alerts

### 4. Library Interface

The Library Interface handles book lending and returns:

- **Book Management**:
  - Add, edit, and delete books in inventory
  - Search for books by title, author, or category

- **Lending Operations**:
  - Process book checkouts via student RFID
  - Handle book returns
  - Manage due dates and overdue books

- **Reporting**:
  - Currently borrowed books
  - Overdue book reports
  - Student borrowing history

### 5. Bus Interface

The Bus Interface tracks student transport:

- **Route Management**:
  - Select active bus route
  - View route details and stops

- **Boarding Management**:
  - Record student boarding via RFID
  - Track offboarding
  - Automatic parent notifications

- **Reporting**:
  - Current bus occupancy
  - Student travel history

### 6. Student Interface

The Student Interface allows students to access their information:

- **Personal Dashboard**:
  - View profile information
  - Check wallet balance
  - See attendance records
  - View borrowed books and due dates
  - Check bus status

## Advanced Face Recognition System

The application uses a highly secure face recognition system designed to prevent proxy attendance and ensure accurate identification.

### Key Features of the Face Recognition System

1. **Multi-Angle Face Encoding**:
   - Captures 7 different face angles during registration:
     - Frontal view (looking straight at camera)
     - Left and right profile views (slight turn)
     - Upward and downward tilt views
     - Closer and further distance views
   - Creates comprehensive face signature that's difficult to spoof

2. **High-Security Verification**:
   - Uses strict matching tolerance (0.42)
   - Requires 5 consecutive successful matches
   - Analyzes both minimum and average face distances
   - Performs consistency checks to prevent video playback attacks
   - Detects face location and size in frame

3. **Quality Control**:
   - Validates face size in frame (not too close/far)
   - Checks for sufficient lighting
   - Ensures face uniqueness during registration
   - Provides clear feedback and guidance to users

4. **Verification Process**:
   - **Step 1**: Student presents RFID card to identify their account
   - **Step 2**: System loads their stored face encodings from database
   - **Step 3**: Camera captures live face image for verification
   - **Step 4**: System compares live face with stored encodings using multiple metrics
   - **Step 5**: Only marks attendance after passing all security checks
   - **Step 6**: Records verification method and security level in attendance record

5. **Technical Details**:
   - Face detection using HOG model
   - 128-dimension face encodings
   - Multiple jitters (3) for better encoding quality
   - Base64 encoding for database storage
   - Visualization of face distances and matching thresholds
   - Detailed logging for troubleshooting

### Adjusting Security Level

The system's security level can be adjusted by modifying parameters in the `verify_face` function in `utils.py`:

- **Tolerance**: Controls how strict the matching is:
  - 0.4: Very strict (may reject valid users in poor conditions)
  - 0.42: High security (default)
  - 0.45: Moderate security
  - 0.5: Standard security
  - 0.6: Permissive (not recommended)

- **Required Matches**: Number of consecutive successful matches needed:
  - Default: 5 (change `required_matches` variable)

- **Consistency Threshold**: How much variation is allowed between matches:
  - Default: 0.03 (change `distance_consistency_threshold` variable)

## Application Architecture

The application follows a modular architecture:

- `src/main.py`: Main entry point and menu system
- `src/utils.py`: Utility functions, shared helpers, and face recognition utilities
- `src/database.py`: Firebase database setup and initialization
- `src/components/`: UI components for different modules
  - `admin_ui.py`: Admin interface
  - `classroom_ui.py`: Classroom attendance management
  - `canteen_ui.py`: Canteen and wallet transactions
  - `library_ui.py`: Library management
  - `bus_ui.py`: Transport management
  - `student_ui.py`: Student self-service portal

### Technologies Used

- **tkinter**: For the graphical user interface
- **Firebase Firestore**: As the cloud database
- **face_recognition & dlib**: For facial recognition
- **OpenCV**: For camera access and image processing
- **Python datetime module**: For time-based operations
- **CSV module**: For data export functionality

## Database Structure

The application uses Firebase Firestore with the following collections:

- `students`: Student profiles with face data, account details
  - Key fields: rfid, name, department, year, section, wallet_balance, face_data, face_security

- `attendance`: Attendance records with face verification status
  - Key fields: student_id, date, timestamp, verification_method, verification_strictness

- `transactions`: Wallet transactions
  - Key fields: student_id, amount, type (credit/debit), timestamp

- `books`: Book inventory
  - Key fields: book_id, title, author, category, available

- `library_records`: Book lending records
  - Key fields: student_id, book_id, checkout_date, due_date, return_date

- `bus_routes`: Bus route information
  - Key fields: route_id, name, stops

- `bus_activity`: Bus boarding/offboarding logs
  - Key fields: student_id, route_id, action (boarding/offboarding), timestamp

## Troubleshooting

### Face Recognition Issues

1. **False Matches (System Accepting Wrong Person)**:
   - Decrease the tolerance value in `verify_face` function (try 0.40)
   - Increase required consecutive matches (e.g., from 5 to 7)
   - Re-register face with better lighting and more distinct angles
   - Ensure face registration was done with only the correct person in frame

2. **False Rejections (System Not Recognizing Correct Person)**:
   - Check lighting conditions - ensure face is well-lit without shadows
   - Make sure face is clearly visible and not obstructed
   - Try removing glasses if applicable
   - Position face at distance and angle similar to registration
   - Re-register face data with current appearance if it has changed significantly

3. **Poor Performance**:
   - Close other applications to free up CPU/memory
   - Ensure adequate lighting in the room
   - Use a better quality webcam if available
   - Consider running on a system with GPU support

### Installation Issues

1. **dlib/face_recognition Installation Failures**:
   - Follow platform-specific instructions in Installation section
   - Ensure you have C++ build tools and CMake installed
   - Try using pre-compiled wheels if direct installation fails
   - On Windows, make sure you have the latest Microsoft Visual C++ Redistributable
   
2. **Firebase Connection Issues**:
   - Verify internet connectivity
   - Check serviceAccountKey.json is correctly placed and formatted
   - Ensure Firestore is enabled in your Firebase project
   - Check firewall settings if applicable

3. **OpenCV Camera Access Issues**:
   - Verify webcam is properly connected and recognized by system
   - Try changing the camera_index parameter (0 for built-in, 1+ for external)
   - Check camera permissions at the OS level

## Security Considerations

This system implements several security features:

1. **Anti-Spoofing Measures**:
   - Multi-angle face data makes photo/video spoofing difficult
   - Consistency checks detect video playback attempts
   - Multiple verification steps prevent simple attacks

2. **Data Security**:
   - Face data is stored as encoded base64 strings
   - PIN numbers required for sensitive operations
   - Firebase security rules should be implemented (not covered in this README)

3. **Privacy**:
   - Face data is only used for verification purposes
   - Data is stored in your own Firebase instance
   - No face images are transmitted to third parties

## Extending the System

The application can be extended in various ways:

1. **Hardware Integration**:
   - Add actual RFID reader hardware
   - Integrate with turnstiles or gates for physical access
   - Add touchscreen support for kiosk mode

2. **Additional Features**:
   - Mobile app for students
   - Parent portal
   - Notification system
   - Advanced analytics dashboard

3. **Performance Enhancements**:
   - GPU acceleration for face recognition
   - Offline mode with synchronization
   - Batch processing for large datasets

## License

This project is licensed under the terms of the [MIT License](LICENSE).

## Acknowledgments

- Face recognition powered by [face_recognition](https://github.com/ageitgey/face_recognition) library
- Database functionality provided by Firebase Firestore
- Image processing capabilities from OpenCV

## Note

This is a proof-of-concept application that simulates RFID readers while using actual face recognition. In a production environment, you would need to integrate with actual RFID readers and implement additional security measures appropriate for your specific use case. 
