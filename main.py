#!/usr/bin/env python3
"""
RFID Student Wallet Application
Main entry point that runs the application
"""
import tkinter as tk
from tkinter import ttk, messagebox
import firebase_admin
from firebase_admin import credentials, firestore
import os
import sys
import json
import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Initialize Firebase
try:
    # Check if firebase config file exists, else create a placeholder
    if not os.path.exists('firebase_config.json'):
        # This is a placeholder. User needs to replace with actual Firebase config
        firebase_config = {
            "apiKey": "YOUR_API_KEY",
            "authDomain": "YOUR_PROJECT_ID.firebaseapp.com",
            "databaseURL": "https://YOUR_PROJECT_ID.firebaseio.com",
            "projectId": "YOUR_PROJECT_ID",
            "storageBucket": "YOUR_PROJECT_ID.appspot.com",
            "messagingSenderId": "YOUR_MESSAGING_SENDER_ID",
            "appId": "YOUR_APP_ID"
        }
        with open('firebase_config.json', 'w') as f:
            json.dump(firebase_config, f, indent=4)
        
        print("Firebase config file created. Please update with your actual Firebase credentials.")
    
    # Create service account key file if it doesn't exist
    if not os.path.exists('serviceAccountKey.json'):
        # This is a placeholder. User needs to replace with actual service account key
        service_account = {
            "type": "service_account",
            "project_id": "YOUR_PROJECT_ID",
            "private_key_id": "YOUR_PRIVATE_KEY_ID",
            "private_key": "YOUR_PRIVATE_KEY",
            "client_email": "YOUR_CLIENT_EMAIL",
            "client_id": "YOUR_CLIENT_ID",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "YOUR_CLIENT_CERT_URL"
        }
        with open('serviceAccountKey.json', 'w') as f:
            json.dump(service_account, f, indent=4)
        
        print("Service account key file created. Please update with your actual service account credentials.")

    # Initialize Firebase with service account
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase initialized successfully!")
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    messagebox.showerror("Firebase Error", f"Could not initialize Firebase: {e}\nPlease update the firebase_config.json and serviceAccountKey.json files with your actual credentials.")
    db = None

# Import UI modules after Firebase initialization
from components.admin_ui import AdminUI
from components.classroom_ui import ClassroomUI
from components.canteen_ui import CanteenUI
from components.library_ui import LibraryUI
from components.bus_ui import BusUI
from components.student_ui import StudentUI

# Function to initialize database with sample data
def initialize_database():
    """Initialize database with sample data."""
    db = firestore.client()
    
    print("Initializing database with sample data...")
    
    # Check if data already exists
    students_ref = db.collection('students')
    students = students_ref.limit(1).get()
    
    if len(list(students)) > 0:
        print("Database already contains data, skipping initialization.")
        return
    
    # Sample Admin
    admin_data = {
        'name': 'Admin User',
        'email': 'admin@example.com',
        'rfid': '0006435835',
        'pin': '1234',
        'role': 'admin',
        'department': 'Administration',
        'created_at': datetime.datetime.now()
    }
    
    # Sample Students
    students_data = [
        {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'rfid': '0001234567',
            'pin': '1234',
            'department': 'Computer Science',
            'year': '3rd',
            'wallet_balance': 1500.00,
            'face_data': None,
            'created_at': datetime.datetime.now()
        },
        {
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com',
            'rfid': '0002345678',
            'pin': '5678',
            'department': 'Electrical Engineering',
            'year': '2nd',
            'wallet_balance': 1000.00,
            'face_data': None,
            'created_at': datetime.datetime.now()
        },
        {
            'name': 'Alex Johnson',
            'email': 'alex.johnson@example.com',
            'rfid': '0003456789',
            'pin': '9012',
            'department': 'Mechanical Engineering',
            'year': '4th',
            'wallet_balance': 1200.00,
            'face_data': None,
            'created_at': datetime.datetime.now()
        }
    ]
    
    # Sample Routes
    routes_data = [
        {
            'name': 'Campus to Downtown',
            'start_point': 'Campus Main Gate',
            'end_point': 'Downtown Station',
            'stops': ['Science Building', 'Library', 'University Hospital', 'Market Square'],
            'fare': 25.00,
            'schedule': [
                {'departure': '08:00', 'arrival': '08:45'},
                {'departure': '12:00', 'arrival': '12:45'},
                {'departure': '16:00', 'arrival': '16:45'}
            ]
        },
        {
            'name': 'Suburban Route',
            'start_point': 'Campus',
            'end_point': 'East Housing',
            'stops': ['Campus', 'West Housing', 'Shopping Center', 'Park', 'East Housing'],
            'fare': 15.00,
            'schedule': [
                {'departure': '07:00', 'arrival': '07:45'},
                {'departure': '13:00', 'arrival': '13:45'},
                {'departure': '18:00', 'arrival': '18:45'}
            ]
        },
        {
            'name': 'Express Route',
            'start_point': 'Campus',
            'end_point': 'Airport',
            'stops': ['Campus', 'Main Station', 'Airport'],
            'fare': 50.00,
            'schedule': [
                {'departure': '06:00', 'arrival': '06:45'},
                {'departure': '10:00', 'arrival': '10:45'},
                {'departure': '14:00', 'arrival': '14:45'}
            ]
        }
    ]
    
    # Sample Books
    books_data = [
        {
            'book_id': 'CS101',
            'title': 'Introduction to Computer Science',
            'author': 'Dr. Jane Smith',
            'publisher': 'Academic Press',
            'year': 2020,
            'category': 'Computer Science',
            'available': True,
            'status': 'available'
        },
        {
            'book_id': 'DB101',
            'title': 'Database Management Systems',
            'author': 'Mary Johnson',
            'publisher': 'Academic Press',
            'year': 2021,
            'category': 'Computer Science',
            'available': True,
            'status': 'available'
        },
        {
            'book_id': 'ME101',
            'title': 'Circuit Analysis',
            'author': 'Robert Williams',
            'publisher': 'Academic Press',
            'year': 2022,
            'category': 'Electrical Engineering',
            'available': True,
            'status': 'available'
        },
        {
            'book_id': 'ME201',
            'title': 'Thermodynamics Fundamentals',
            'author': 'James Wilson',
            'publisher': 'Academic Press',
            'year': 2023,
            'category': 'Mechanical Engineering',
            'available': True,
            'status': 'available'
        }
    ]
    
    # Sample Transactions
    transactions_data = [
        {
            'student_id': '',  # Will be filled after student creation
            'student_name': 'John Doe',
            'type': 'credit',
            'amount': 1000.00,
            'description': 'Initial wallet credit',
            'location': 'Admin Office',
            'timestamp': datetime.datetime.now() - datetime.timedelta(days=5)
        },
        {
            'student_id': '',
            'student_name': 'Jane Smith',
            'type': 'credit',
            'amount': 1000.00,
            'description': 'Initial wallet credit',
            'location': 'Admin Office',
            'timestamp': datetime.datetime.now() - datetime.timedelta(days=5)
        },
        {
            'student_id': '',
            'student_name': 'Alex Johnson',
            'type': 'credit',
            'amount': 1000.00,
            'description': 'Initial wallet credit',
            'location': 'Admin Office',
            'timestamp': datetime.datetime.now() - datetime.timedelta(days=5)
        }
    ]
    
    # Sample Lendings (initially empty)
    lendings_data = []
    
    # Sample Returns (initially empty)
    returns_data = []
    
    # Helper function to add data to a collection
    def add_collection_data(collection_name, data_list):
        collection_ref = db.collection(collection_name)
        for data in data_list:
            doc_ref = collection_ref.add(data)
            print(f"Added document {doc_ref[1].id} to {collection_name}")
            if collection_name == 'students' and 'name' in data and data['name'] == 'John Doe':
                # Update transaction with student ID
                for tx in transactions_data:
                    if tx['student_name'] == 'John Doe':
                        tx['student_id'] = doc_ref[1].id
    
    # Add data to collections
    add_collection_data("admin", [admin_data])
    add_collection_data("students", students_data)
    add_collection_data("routes", routes_data)
    add_collection_data("books", books_data)
    add_collection_data("transactions", transactions_data)
    add_collection_data("lendings", lendings_data)
    add_collection_data("returns", returns_data)
    
    print("Database initialized successfully with sample data.")

class RFIDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RFID Student Wallet Application")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set style
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 12))
        self.style.configure('TLabel', font=('Arial', 12), background='#f0f0f0')
        
        self.create_main_menu()
    
    def create_main_menu(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="RFID Student Wallet Application", font=('Arial', 18, 'bold'))
        title_label.pack(pady=20)
        
        # Create buttons for each interface
        btn_admin = ttk.Button(main_frame, text="Admin Interface", command=self.open_admin_ui)
        btn_classroom = ttk.Button(main_frame, text="Classroom Interface", command=self.open_classroom_ui)
        btn_canteen = ttk.Button(main_frame, text="Canteen Interface", command=self.open_canteen_ui)
        btn_library = ttk.Button(main_frame, text="Library Interface", command=self.open_library_ui)
        btn_bus = ttk.Button(main_frame, text="Bus Interface", command=self.open_bus_ui)
        btn_student = ttk.Button(main_frame, text="Student Interface", command=self.open_student_ui)
        
        # Add buttons to the frame with some padding
        btn_admin.pack(fill=tk.X, pady=10)
        btn_classroom.pack(fill=tk.X, pady=10)
        btn_canteen.pack(fill=tk.X, pady=10)
        btn_library.pack(fill=tk.X, pady=10)
        btn_bus.pack(fill=tk.X, pady=10)
        btn_student.pack(fill=tk.X, pady=10)
        
        # Init DB button
        btn_init_db = ttk.Button(main_frame, text="Initialize Database with Sample Data", command=self.init_database)
        btn_init_db.pack(fill=tk.X, pady=10)
        
        # Exit button
        btn_exit = ttk.Button(main_frame, text="Exit", command=self.root.destroy)
        btn_exit.pack(fill=tk.X, pady=20)
    
    def init_database(self):
        if db:
            result = messagebox.askyesno("Initialize Database", "This will populate the database with sample data. Continue?")
            if result:
                success = initialize_database()
                if success:
                    messagebox.showinfo("Success", "Database initialized successfully with sample data!")
                else:
                    messagebox.showerror("Error", "Failed to initialize database. Check console for details.")
        else:
            messagebox.showerror("Firebase Error", "Database not initialized. Please check Firebase credentials.")
    
    def open_admin_ui(self):
        if db:
            AdminUI(self.root, db, self.create_main_menu)
        else:
            messagebox.showerror("Firebase Error", "Database not initialized. Please check Firebase credentials.")
    
    def open_classroom_ui(self):
        if db:
            ClassroomUI(self.root, db, self.create_main_menu)
        else:
            messagebox.showerror("Firebase Error", "Database not initialized. Please check Firebase credentials.")
    
    def open_canteen_ui(self):
        if db:
            CanteenUI(self.root, db, self.create_main_menu)
        else:
            messagebox.showerror("Firebase Error", "Database not initialized. Please check Firebase credentials.")
    
    def open_library_ui(self):
        if db:
            LibraryUI(self.root, db, self.create_main_menu)
        else:
            messagebox.showerror("Firebase Error", "Database not initialized. Please check Firebase credentials.")
    
    def open_bus_ui(self):
        if db:
            BusUI(self.root, db, self.create_main_menu)
        else:
            messagebox.showerror("Firebase Error", "Database not initialized. Please check Firebase credentials.")
    
    def open_student_ui(self):
        if db:
            StudentUI(self.root, db, self.create_main_menu)
        else:
            messagebox.showerror("Firebase Error", "Database not initialized. Please check Firebase credentials.")

def main():
    """
    Main entry point for the application.
    """
    root = tk.Tk()
    app = RFIDApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 