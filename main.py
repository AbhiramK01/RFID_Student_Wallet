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
    """
    Initialize the Firebase database with sample data for testing.
    This will set up the necessary collections and documents.
    """
    print("Initializing Firebase database with sample data...")
    
    try:
        # Check if already initialized
        if firebase_admin._apps:
            database = firestore.client()
        else:
            # Initialize Firebase
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
            database = firestore.client()
        
        # Sample Students
        students_data = [
            {
                "rfid": "0001234567",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "department": "Computer Science",
                "year": 3,
                "section": "A",
                "wallet_balance": 500.0,
                "parent_email": "parent.doe@example.com",
                "photo_url": "",
                "pin": "1234",  # In a real app, this would be hashed
                "bus_route": "Route 1"
            },
            {
                "rfid": "0002345678",
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "department": "Electrical Engineering",
                "year": 2,
                "section": "B",
                "wallet_balance": 750.0,
                "parent_email": "parent.smith@example.com",
                "photo_url": "",
                "pin": "5678",
                "bus_route": "Route 2"
            },
            {
                "rfid": "0003456789",
                "name": "Alex Johnson",
                "email": "alex.johnson@example.com",
                "department": "Mechanical Engineering",
                "year": 4,
                "section": "C",
                "wallet_balance": 350.0,
                "parent_email": "parent.johnson@example.com",
                "photo_url": "",
                "pin": "9012",
                "bus_route": "Route 3"
            }
        ]
        
        # Sample admin
        admin_data = {
            "rfid": "0006435835",
            "name": "Admin User",
            "email": "admin@example.com",
            "role": "admin",
            "pin": "0000"
        }
        
        # Sample Bus Routes
        bus_routes_data = [
            {
                "route_id": "Route 1",
                "name": "City Center Route",
                "stops": ["Campus", "Library", "Downtown", "Mall", "Apartments"]
            },
            {
                "route_id": "Route 2",
                "name": "Suburban Route",
                "stops": ["Campus", "West Housing", "Shopping Center", "Park", "East Housing"]
            },
            {
                "route_id": "Route 3",
                "name": "Express Route",
                "stops": ["Campus", "Main Station", "Airport"]
            }
        ]
        
        # Sample Books
        books_data = [
            {
                "book_id": "B001",
                "title": "Introduction to Python Programming",
                "author": "John Smith",
                "category": "Computer Science",
                "available": True
            },
            {
                "book_id": "B002",
                "title": "Database Management Systems",
                "author": "Mary Johnson",
                "category": "Computer Science",
                "available": True
            },
            {
                "book_id": "B003",
                "title": "Circuit Analysis",
                "author": "Robert Williams",
                "category": "Electrical Engineering",
                "available": True
            },
            {
                "book_id": "B004",
                "title": "Thermodynamics Fundamentals",
                "author": "James Wilson",
                "category": "Mechanical Engineering",
                "available": True
            }
        ]
        
        # Sample Attendance (for today)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        attendance_data = [
            {
                "student_id": "0001234567",
                "date": today,
                "department": "Computer Science",
                "year": 3,
                "section": "A",
                "status": "present",
                "timestamp": firestore.SERVER_TIMESTAMP
            },
            {
                "student_id": "0002345678",
                "date": today,
                "department": "Electrical Engineering",
                "year": 2,
                "section": "B",
                "status": "present",
                "timestamp": firestore.SERVER_TIMESTAMP
            }
        ]
        
        # Sample Transactions
        transactions_data = [
            {
                "student_id": "0001234567",
                "amount": -50.0,
                "type": "debit",
                "description": "Canteen purchase",
                "timestamp": firestore.SERVER_TIMESTAMP,
                "location": "Canteen"
            },
            {
                "student_id": "0001234567",
                "amount": 200.0,
                "type": "credit",
                "description": "Wallet recharge",
                "timestamp": firestore.SERVER_TIMESTAMP,
                "location": "Canteen"
            },
            {
                "student_id": "0002345678",
                "amount": -75.0,
                "type": "debit",
                "description": "Canteen purchase",
                "timestamp": firestore.SERVER_TIMESTAMP,
                "location": "Canteen"
            }
        ]
        
        # Sample Library Records
        library_records_data = [
            {
                "student_id": "0003456789",
                "book_id": "B003",
                "issue_date": (datetime.datetime.now() - datetime.timedelta(days=5)).strftime("%Y-%m-%d"),
                "due_date": (datetime.datetime.now() + datetime.timedelta(days=10)).strftime("%Y-%m-%d"),
                "return_date": None,
                "status": "borrowed"
            }
        ]
        
        # Sample Bus Activity
        bus_activity_data = [
            {
                "student_id": "0002345678",
                "route_id": "Route 2",
                "action": "boarding",
                "timestamp": firestore.SERVER_TIMESTAMP,
                "location": "Campus"
            }
        ]
        
        # Function to add data to collection
        def add_collection_data(collection_name, data_list):
            for data in data_list:
                # For students and admin, use RFID as document ID
                if collection_name == "students" and "rfid" in data:
                    database.collection(collection_name).document(data["rfid"]).set(data)
                else:
                    database.collection(collection_name).add(data)
            print(f"Added {len(data_list)} documents to {collection_name} collection")
        
        # Add data to collections
        add_collection_data("students", students_data)
        database.collection("students").document(admin_data["rfid"]).set(admin_data)
        print(f"Added admin user to students collection")
        
        add_collection_data("bus_routes", bus_routes_data)
        add_collection_data("books", books_data)
        add_collection_data("attendance", attendance_data)
        add_collection_data("transactions", transactions_data)
        add_collection_data("library_records", library_records_data)
        add_collection_data("bus_activity", bus_activity_data)
        
        print("Database initialization completed successfully!")
        return True
    
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

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