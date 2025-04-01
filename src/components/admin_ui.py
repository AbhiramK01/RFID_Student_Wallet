import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import validate_rfid, authenticate_admin, create_entry_with_label, get_student_by_rfid
import csv
import datetime
from firebase_admin import firestore

class AdminUI:
    def __init__(self, root, db, return_callback):
        self.root = root
        self.db = db
        self.return_callback = return_callback
        
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.title("Admin Interface - RFID Student Wallet Application")
        
        # Start with RFID authentication
        self.authenticate_admin()
    
    def authenticate_admin(self):
        """Show the admin authentication screen"""
        auth_frame = ttk.Frame(self.root, padding=20)
        auth_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(auth_frame, text="Admin Authentication", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # RFID input
        rfid_frame = ttk.Frame(auth_frame)
        rfid_frame.pack(fill=tk.X, pady=10)
        
        rfid_label = ttk.Label(rfid_frame, text="Admin RFID:")
        rfid_label.pack(side=tk.LEFT, padx=5)
        
        self.rfid_entry = ttk.Entry(rfid_frame, width=15)
        self.rfid_entry.pack(side=tk.LEFT, padx=5)
        self.rfid_entry.focus()
        
        # Submit button
        submit_btn = ttk.Button(auth_frame, text="Login", command=self.verify_admin)
        submit_btn.pack(pady=10)
        
        # Bind Enter key to submit
        self.rfid_entry.bind('<Return>', lambda event: self.verify_admin())
        
        # Back button
        back_btn = ttk.Button(auth_frame, text="Back to Main Menu", command=self.return_callback)
        back_btn.pack(pady=(20, 0))
    
    def verify_admin(self):
        """Verify the admin RFID"""
        rfid = self.rfid_entry.get().strip()
        
        if not validate_rfid(rfid):
            messagebox.showerror("Invalid RFID", "Please enter a valid 10-digit RFID.")
            return
        
        if not authenticate_admin(rfid):
            messagebox.showerror("Access Denied", "This RFID is not authorized for admin access.")
            return
        
        # Admin verified, show the admin menu
        self.show_admin_menu()
    
    def show_admin_menu(self):
        """Show the admin menu after successful authentication"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        admin_frame = ttk.Frame(self.root, padding=20)
        admin_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(admin_frame, text="Admin Panel", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Admin functions
        student_btn = ttk.Button(admin_frame, text="Manage Students", 
                                 command=self.manage_students)
        student_btn.pack(fill=tk.X, pady=5)
        
        bus_btn = ttk.Button(admin_frame, text="Manage Bus Routes", 
                              command=self.manage_bus_routes)
        bus_btn.pack(fill=tk.X, pady=5)
        
        export_btn = ttk.Button(admin_frame, text="Export Data", 
                               command=self.export_data)
        export_btn.pack(fill=tk.X, pady=5)
        
        clear_btn = ttk.Button(admin_frame, text="Clear Database", 
                              command=self.confirm_clear_database)
        clear_btn.pack(fill=tk.X, pady=5)
        
        # Back button
        back_btn = ttk.Button(admin_frame, text="Back to Main Menu", 
                              command=self.return_callback)
        back_btn.pack(fill=tk.X, pady=(20, 0))
    
    def manage_students(self):
        """Show the student management interface"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        student_frame = ttk.Frame(self.root, padding=20)
        student_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(student_frame, text="Student Management", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Student functions
        add_btn = ttk.Button(student_frame, text="Add New Student", 
                            command=self.add_student)
        add_btn.pack(fill=tk.X, pady=5)
        
        update_btn = ttk.Button(student_frame, text="Update Student", 
                               command=self.update_student)
        update_btn.pack(fill=tk.X, pady=5)
        
        delete_btn = ttk.Button(student_frame, text="Delete Student", 
                               command=self.delete_student)
        delete_btn.pack(fill=tk.X, pady=5)
        
        list_btn = ttk.Button(student_frame, text="List All Students", 
                             command=self.list_students)
        list_btn.pack(fill=tk.X, pady=5)
        
        # Back button
        back_btn = ttk.Button(student_frame, text="Back to Admin Menu", 
                             command=self.show_admin_menu)
        back_btn.pack(fill=tk.X, pady=(20, 0))
    
    def add_student(self):
        """Show form to add a new student"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        form_frame = ttk.Frame(self.root, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(form_frame, text="Add New Student", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create form fields
        input_frame = ttk.Frame(form_frame)
        input_frame.pack(fill=tk.BOTH, padx=20, pady=10)
        
        # Configure grid columns
        input_frame.columnconfigure(1, weight=1)
        
        # Student details form
        self.name_entry = create_entry_with_label(input_frame, "Name:", 0)
        self.rfid_entry = create_entry_with_label(input_frame, "RFID Number:", 1)
        self.pin_entry = create_entry_with_label(input_frame, "PIN (4 digits):", 2, show="*")
        self.dept_entry = create_entry_with_label(input_frame, "Department:", 3)
        self.year_entry = create_entry_with_label(input_frame, "Year:", 4)
        self.section_entry = create_entry_with_label(input_frame, "Section:", 5)
        self.email_entry = create_entry_with_label(input_frame, "Parent's Email:", 6)
        
        # Face registration frame
        face_frame = ttk.Frame(input_frame)
        face_frame.grid(row=7, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Face registration status indicator
        self.face_registered = tk.BooleanVar(value=False)
        self.face_data = None
        
        face_status_label = ttk.Label(face_frame, text="Face Registration:")
        face_status_label.pack(side=tk.LEFT, padx=5)
        
        self.face_status = ttk.Label(face_frame, text="Not Registered", foreground="red")
        self.face_status.pack(side=tk.LEFT, padx=5)
        
        face_reg_btn = ttk.Button(face_frame, text="Register Face", 
                                 command=self.register_face)
        face_reg_btn.pack(side=tk.LEFT, padx=5)
        
        # Bus pass
        self.has_bus_pass = tk.BooleanVar(value=False)
        bus_frame = ttk.Frame(input_frame)
        bus_frame.grid(row=8, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        bus_check = ttk.Checkbutton(bus_frame, text="Has Bus Pass", 
                                   variable=self.has_bus_pass,
                                   command=self.toggle_bus_route)
        bus_check.pack(side=tk.LEFT, padx=5)
        
        self.bus_route_entry = ttk.Entry(bus_frame, width=10, state="disabled")
        self.bus_route_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(bus_frame, text="Route Number").pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        save_btn = ttk.Button(btn_frame, text="Save Student", 
                             command=self.save_new_student)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", 
                               command=self.manage_students)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def register_face(self):
        """Capture and register student's face"""
        # Import here to avoid circular imports
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from utils import capture_face, encode_face_to_base64
        
        # Show a prompt to the user
        messagebox.showinfo("Face Registration - Enhanced Security", 
                          "The camera will now open to register the student's face.\n\n"
                          "ENHANCED SECURITY MODE ENABLED:\n"
                          "To prevent false matches, we require capturing 7 different face angles.\n\n"
                          "Please ensure that:\n"
                          "- Student is looking directly at the camera\n"
                          "- Lighting is bright and even (no shadows on face)\n"
                          "- Only the student's face is visible\n"
                          "- Facial features are clearly visible (no glasses if possible)\n\n"
                          "The system will guide you to capture the following angles:\n"
                          "1. Looking straight at the camera (frontal view)\n"
                          "2. Turned slightly left\n"
                          "3. Turned slightly right\n"
                          "4. Tilted slightly up\n"
                          "5. Tilted slightly down\n"
                          "6. Slightly closer to camera\n"
                          "7. Slightly further from camera\n\n"
                          "Follow the on-screen instructions carefully for each position.")
        
        # Capture multiple face encodings for better accuracy
        face_encodings = capture_face(camera_index=0, required_encodings=7)
        
        if face_encodings is None or len(face_encodings) < 5:
            messagebox.showerror("Registration Failed", 
                               "Could not capture enough face data. Please try again with:\n"
                               "- Better lighting (bright, even light on face)\n"
                               "- Clear face visibility (no obstructions)\n"
                               "- Following the position instructions exactly\n"
                               "- Removing glasses if possible\n"
                               "- Ensuring only one face is in frame")
            return
        
        # Store the face encodings
        self.face_data = face_encodings
        self.face_registered = tk.BooleanVar(value=True)
        
        # Update the status label
        self.face_status.config(text=f"Registered ({len(face_encodings)} angles) - High Security", foreground="green")
        
        messagebox.showinfo("Success", 
                          f"Face registered successfully with {len(face_encodings)} different angles!\n\n"
                          "The system is now configured for high-security face recognition.\n"
                          "This will help prevent false matches and proxy attendance.")
    
    def toggle_bus_route(self):
        """Enable/disable bus route entry based on checkbox"""
        if self.has_bus_pass.get():
            self.bus_route_entry.config(state="normal")
        else:
            self.bus_route_entry.config(state="disabled")
    
    def save_new_student(self):
        """Save a new student to the database"""
        # Validate form data
        name = self.name_entry.get().strip()
        rfid = self.rfid_entry.get().strip()
        pin = self.pin_entry.get().strip()
        dept = self.dept_entry.get().strip()
        year = self.year_entry.get().strip()
        section = self.section_entry.get().strip()
        email = self.email_entry.get().strip()
        
        # Basic validation
        if not all([name, rfid, pin, dept, year, section, email]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if not validate_rfid(rfid):
            messagebox.showerror("Invalid RFID", "RFID must be 10 digits.")
            return
            
        if len(pin) != 4 or not pin.isdigit():
            messagebox.showerror("Invalid PIN", "PIN must be 4 digits.")
            return
        
        # Check if face is registered
        if not hasattr(self, 'face_data') or self.face_data is None:
            response = messagebox.askyesno("Face Not Registered", 
                                         "No face data is registered for this student. Continue anyway?\n\n"
                                         "WARNING: Without face data, the student will not be able to mark attendance "
                                         "in the classroom module.",
                                          icon="warning")
            if not response:
                return
        
        # Check if RFID already exists
        existing_student = get_student_by_rfid(self.db, rfid)
        if existing_student:
            messagebox.showerror("Error", f"Student with RFID {rfid} already exists!")
            return
        
        # Import for face encoding
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from utils import encode_face_to_base64
        
        # Encode face data if available
        face_encoding_base64 = None
        if hasattr(self, 'face_data') and self.face_data is not None:
            face_encoding_base64 = encode_face_to_base64(self.face_data)
        
        # Prepare data
        student_data = {
            'name': name,
            'rfid': rfid,
            'pin': pin,
            'department': dept,
            'year': year,
            'section': section,
            'parent_email': email,
            'wallet_balance': 0,
            'created_at': datetime.datetime.now(),
            'has_bus_pass': self.has_bus_pass.get(),
            'bus_route': None,
            'bus_status': 'outside',  # Default status
            'face_data': face_encoding_base64,  # Store face data in base64 format
            'face_security': 'high' if face_encoding_base64 else None  # Mark this as high security face data
        }
        
        # Add bus route if applicable
        if self.has_bus_pass.get():
            route_id = self.bus_route_entry.get().strip()
            if not route_id:
                messagebox.showerror("Error", "Bus route ID is required for students with bus pass!")
                return
            
            # Verify bus route exists by checking route_id field
            query = self.db.collection('bus_routes').where(filter=firestore.FieldFilter('route_id', '==', route_id)).limit(1)
            routes = query.get()
            
            if not routes or len(routes) == 0:
                messagebox.showerror("Error", f"Bus route with ID {route_id} does not exist!")
                return
                
            student_data['bus_route'] = route_id
        
        # Save to Firebase
        try:
            self.db.collection('students').add(student_data)
            messagebox.showinfo("Success", f"Student {name} added successfully!")
            self.manage_students()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add student: {e}")
    
    def update_student(self):
        """Show search interface to find a student to update"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        search_frame = ttk.Frame(self.root, padding=20)
        search_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(search_frame, text="Find Student to Update", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # RFID input
        rfid_frame = ttk.Frame(search_frame)
        rfid_frame.pack(fill=tk.X, pady=10)
        
        rfid_label = ttk.Label(rfid_frame, text="Student RFID:")
        rfid_label.pack(side=tk.LEFT, padx=5)
        
        self.search_rfid_entry = ttk.Entry(rfid_frame, width=15)
        self.search_rfid_entry.pack(side=tk.LEFT, padx=5)
        self.search_rfid_entry.focus()
        
        # Submit button
        submit_btn = ttk.Button(search_frame, text="Search", 
                               command=self.find_student_to_update)
        submit_btn.pack(pady=10)
        
        # Back button
        back_btn = ttk.Button(search_frame, text="Back", 
                             command=self.manage_students)
        back_btn.pack(pady=(20, 0))
    
    def find_student_to_update(self):
        """Find a student by RFID for updating"""
        rfid = self.search_rfid_entry.get().strip()
        
        if not validate_rfid(rfid):
            messagebox.showerror("Invalid RFID", "Please enter a valid 10-digit RFID.")
            return
        
        # Search for student
        student = get_student_by_rfid(self.db, rfid)
        
        if not student:
            messagebox.showerror("Not Found", f"No student found with RFID {rfid}.")
            return
        
        # Show update form with student data
        self.show_update_form(student)
    
    def show_update_form(self, student):
        """Show form to update student data"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        update_frame = ttk.Frame(self.root, padding=20)
        update_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(update_frame, text="Update Student", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Form frame
        form_frame = ttk.Frame(update_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Name input
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        name_label = ttk.Label(name_frame, text="Full Name:", width=20)
        name_label.pack(side=tk.LEFT, padx=5, anchor=tk.W)
        
        self.update_name_entry = ttk.Entry(name_frame, width=30)
        self.update_name_entry.pack(side=tk.LEFT, padx=5)
        self.update_name_entry.insert(0, student.get('name', ''))
        
        # RFID - display only, not editable
        rfid_frame = ttk.Frame(form_frame)
        rfid_frame.pack(fill=tk.X, pady=5)
        
        rfid_label = ttk.Label(rfid_frame, text="RFID:", width=20)
        rfid_label.pack(side=tk.LEFT, padx=5, anchor=tk.W)
        
        rfid_value = ttk.Entry(rfid_frame, width=30, state='readonly')
        rfid_value.pack(side=tk.LEFT, padx=5)
        rfid_value.insert(0, student.get('rfid', ''))
        
        # PIN input
        pin_frame = ttk.Frame(form_frame)
        pin_frame.pack(fill=tk.X, pady=5)
        
        pin_label = ttk.Label(pin_frame, text="PIN (4 digits):", width=20)
        pin_label.pack(side=tk.LEFT, padx=5, anchor=tk.W)
        
        self.update_pin_entry = ttk.Entry(pin_frame, width=10)
        self.update_pin_entry.pack(side=tk.LEFT, padx=5)
        self.update_pin_entry.insert(0, student.get('pin', ''))
        
        # Department input
        dept_frame = ttk.Frame(form_frame)
        dept_frame.pack(fill=tk.X, pady=5)
        
        dept_label = ttk.Label(dept_frame, text="Department:", width=20)
        dept_label.pack(side=tk.LEFT, padx=5, anchor=tk.W)
        
        self.update_dept_entry = ttk.Entry(dept_frame, width=30)
        self.update_dept_entry.pack(side=tk.LEFT, padx=5)
        self.update_dept_entry.insert(0, student.get('department', ''))
        
        # Year input
        year_frame = ttk.Frame(form_frame)
        year_frame.pack(fill=tk.X, pady=5)
        
        year_label = ttk.Label(year_frame, text="Year:", width=20)
        year_label.pack(side=tk.LEFT, padx=5, anchor=tk.W)
        
        self.update_year_entry = ttk.Entry(year_frame, width=10)
        self.update_year_entry.pack(side=tk.LEFT, padx=5)
        self.update_year_entry.insert(0, student.get('year', ''))
        
        # Section input
        section_frame = ttk.Frame(form_frame)
        section_frame.pack(fill=tk.X, pady=5)
        
        section_label = ttk.Label(section_frame, text="Section:", width=20)
        section_label.pack(side=tk.LEFT, padx=5, anchor=tk.W)
        
        self.update_section_entry = ttk.Entry(section_frame, width=10)
        self.update_section_entry.pack(side=tk.LEFT, padx=5)
        self.update_section_entry.insert(0, student.get('section', ''))
        
        # Parent Email input
        email_frame = ttk.Frame(form_frame)
        email_frame.pack(fill=tk.X, pady=5)
        
        email_label = ttk.Label(email_frame, text="Parent's Email:", width=20)
        email_label.pack(side=tk.LEFT, padx=5, anchor=tk.W)
        
        self.update_email_entry = ttk.Entry(email_frame, width=30)
        self.update_email_entry.pack(side=tk.LEFT, padx=5)
        self.update_email_entry.insert(0, student.get('parent_email', ''))
        
        # Face registration status
        face_frame = ttk.Frame(form_frame)
        face_frame.pack(fill=tk.X, pady=5)
        
        face_label = ttk.Label(face_frame, text="Face Registration:", width=20)
        face_label.pack(side=tk.LEFT, padx=5, anchor=tk.W)
        
        # Check if student has face data
        has_face_data = 'face_data' in student and student['face_data'] is not None
        face_status_text = "Registered" if has_face_data else "Not Registered"
        face_status_color = "green" if has_face_data else "red"
        
        self.face_status = ttk.Label(face_frame, text=face_status_text, foreground=face_status_color)
        self.face_status.pack(side=tk.LEFT, padx=5)
        
        face_update_btn = ttk.Button(face_frame, text="Update Face Data", 
                                    command=lambda: self.update_face_data(student['id']))
        face_update_btn.pack(side=tk.LEFT, padx=5)
        
        # Wallet Balance display
        balance_frame = ttk.Frame(form_frame)
        balance_frame.pack(fill=tk.X, pady=5)
        
        balance_label = ttk.Label(balance_frame, text="Current Balance:", width=20)
        balance_label.pack(side=tk.LEFT, padx=5, anchor=tk.W)
        
        current_balance = student.get('wallet_balance', 0)
        balance_value = ttk.Label(balance_frame, text=f"₹ {current_balance:.2f}")
        balance_value.pack(side=tk.LEFT, padx=5)
        
        # Add Balance frame
        add_balance_frame = ttk.Frame(form_frame)
        add_balance_frame.pack(fill=tk.X, pady=5)
        
        add_balance_label = ttk.Label(add_balance_frame, text="Add Balance:", width=20)
        add_balance_label.pack(side=tk.LEFT, padx=5, anchor=tk.W)
        
        self.update_balance_entry = ttk.Entry(add_balance_frame, width=15)
        self.update_balance_entry.pack(side=tk.LEFT, padx=5)
        self.update_balance_entry.insert(0, "0.00")
        
        # Bus Pass Checkbox
        bus_frame = ttk.Frame(form_frame)
        bus_frame.pack(fill=tk.X, pady=5)
        
        self.update_has_bus_pass = tk.BooleanVar(value=student.get('has_bus_pass', False))
        bus_checkbox = ttk.Checkbutton(bus_frame, text="Has Bus Pass", variable=self.update_has_bus_pass, 
                                      command=self.toggle_update_bus_route)
        bus_checkbox.pack(side=tk.LEFT, padx=5, anchor=tk.W)
        
        # Bus Route input
        self.update_bus_route_entry = ttk.Entry(bus_frame, width=15, 
                                             state="normal" if student.get('has_bus_pass', False) else "disabled")
        self.update_bus_route_entry.pack(side=tk.LEFT, padx=5)
        
        if student.get('bus_route'):
            self.update_bus_route_entry.insert(0, student.get('bus_route', ''))
        
        # Store student ID
        self.student_id = student['id']
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        save_btn = ttk.Button(btn_frame, text="Save Changes", 
                             command=lambda: self.update_student_data(student))
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", 
                               command=self.manage_students)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Status message
        self.status_var = tk.StringVar()
        status_label = ttk.Label(update_frame, textvariable=self.status_var)
        status_label.pack(pady=10)
    
    def toggle_update_bus_route(self):
        """Enable/disable bus route entry in update form based on checkbox"""
        if self.update_has_bus_pass.get():
            self.update_bus_route_entry.config(state="normal")
        else:
            self.update_bus_route_entry.config(state="disabled")
            
    def update_face_data(self, student_id):
        """Update the face data for a student"""
        # Import here to avoid circular imports
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from utils import capture_face, encode_face_to_base64
        
        # Show a prompt to the user
        messagebox.showinfo("Face Registration Update - Enhanced Security", 
                          "The camera will now open to update the student's face data.\n\n"
                          "ENHANCED SECURITY MODE ENABLED:\n"
                          "To prevent false matches, we require capturing 7 different face angles.\n\n"
                          "Please ensure that:\n"
                          "- Student is looking directly at the camera\n"
                          "- Lighting is bright and even (no shadows on face)\n"
                          "- Only the student's face is visible\n"
                          "- Facial features are clearly visible (no glasses if possible)\n\n"
                          "The system will guide you to capture the following angles:\n"
                          "1. Looking straight at the camera (frontal view)\n"
                          "2. Turned slightly left\n"
                          "3. Turned slightly right\n"
                          "4. Tilted slightly up\n"
                          "5. Tilted slightly down\n"
                          "6. Slightly closer to camera\n"
                          "7. Slightly further from camera\n\n"
                          "Follow the on-screen instructions carefully for each position.")
        
        # Capture face encodings
        face_encodings = capture_face(camera_index=0, required_encodings=7)
        
        if face_encodings is None or len(face_encodings) < 5:
            messagebox.showerror("Registration Failed", 
                               "Could not capture enough face data. Please try again with:\n"
                               "- Better lighting (bright, even light on face)\n"
                               "- Clear face visibility (no obstructions)\n"
                               "- Following the position instructions exactly\n"
                               "- Removing glasses if possible\n"
                               "- Ensuring only one face is in frame")
            return
        
        # Encode face data
        face_encoding_base64 = encode_face_to_base64(face_encodings)
        
        if face_encoding_base64 is None:
            messagebox.showerror("Error", "Failed to encode face data.")
            return
        
        # Update face data in Firestore
        try:
            self.db.collection('students').document(student_id).update({
                'face_data': face_encoding_base64,
                'face_security': 'high'  # Mark this as high security face data
            })
            
            # Update status label
            self.face_status.config(text=f"Registered ({len(face_encodings)} angles) - High Security", foreground="green")
            
            messagebox.showinfo("Success", 
                              f"Face data updated successfully with {len(face_encodings)} different angles!\n\n"
                              "The system is now configured for high-security face recognition.\n"
                              "This will help prevent false matches and proxy attendance.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update face data: {e}")
    
    def update_student_data(self, student):
        """Update student data in database"""
        # Get form data
        name = self.update_name_entry.get().strip()
        pin = self.update_pin_entry.get().strip()
        dept = self.update_dept_entry.get().strip()
        year = self.update_year_entry.get().strip()
        section = self.update_section_entry.get().strip()
        email = self.update_email_entry.get().strip()
        additional_balance_str = self.update_balance_entry.get().strip()
        has_bus_pass = self.update_has_bus_pass.get()
        bus_route = self.update_bus_route_entry.get().strip() if has_bus_pass else None
        
        # Basic validation
        if not all([name, pin, dept, year, section, email]):
            self.status_var.set("All fields are required!")
            return
            
        if len(pin) != 4 or not pin.isdigit():
            self.status_var.set("PIN must be 4 digits.")
            return
        
        try:
            # Validate additional balance
            additional_balance = float(additional_balance_str) if additional_balance_str else 0.0
            if additional_balance < 0:
                self.status_var.set("Additional balance cannot be negative.")
                return
                
            # Validate bus route if required
            if has_bus_pass and not bus_route:
                self.status_var.set("Bus route is required for students with bus pass.")
                return
                
            if has_bus_pass:
                # Verify bus route exists
                query = self.db.collection('bus_routes').where(
                    filter=firestore.FieldFilter('route_id', '==', bus_route)
                ).limit(1)
                routes = query.get()
                
                if not routes or len(routes) == 0:
                    self.status_var.set(f"Bus route with ID {bus_route} does not exist!")
                    return
            
            # Calculate new balance
            current_balance = student.get('wallet_balance', 0)
            new_balance = current_balance + additional_balance
        
            # Prepare update data
            update_data = {
                'name': name,
                'pin': pin,
                'department': dept,
                'year': int(year),
                'section': section,
                'parent_email': email,
                'wallet_balance': new_balance,
                'has_bus_pass': has_bus_pass,
                'bus_route': bus_route if has_bus_pass else None,
                'updated_at': datetime.datetime.now()
            }
            
            # Update in database
            self.db.collection('students').document(self.student_id).update(update_data)
            
            # Record transaction if balance was added
            if additional_balance > 0:
                transaction_data = {
                    'student_id': self.student_id,
                    'amount': additional_balance,
                    'type': 'credit',
                    'description': 'Balance added by administrator',
                    'timestamp': datetime.datetime.now()
                }
                self.db.collection('transactions').add(transaction_data)
            
            messagebox.showinfo("Success", f"Student {name} updated successfully!")
            self.manage_students()
            
        except Exception as e:
            self.status_var.set(f"Error updating student: {e}")
    
    def delete_student(self):
        """Show interface to delete a student"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        delete_frame = ttk.Frame(self.root, padding=20)
        delete_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(delete_frame, text="Delete Student", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # RFID input
        rfid_frame = ttk.Frame(delete_frame)
        rfid_frame.pack(fill=tk.X, pady=10)
        
        rfid_label = ttk.Label(rfid_frame, text="Student RFID:")
        rfid_label.pack(side=tk.LEFT, padx=5)
        
        self.delete_rfid_entry = ttk.Entry(rfid_frame, width=15)
        self.delete_rfid_entry.pack(side=tk.LEFT, padx=5)
        self.delete_rfid_entry.focus()
        
        # Submit button
        submit_btn = ttk.Button(delete_frame, text="Find Student", 
                               command=self.find_student_to_delete)
        submit_btn.pack(pady=10)
        
        # Back button
        back_btn = ttk.Button(delete_frame, text="Back", 
                             command=self.manage_students)
        back_btn.pack(pady=(20, 0))
    
    def find_student_to_delete(self):
        """Find a student by RFID for deletion"""
        rfid = self.delete_rfid_entry.get().strip()
        
        if not validate_rfid(rfid):
            messagebox.showerror("Invalid RFID", "Please enter a valid 10-digit RFID.")
            return
        
        # Search for student
        student = get_student_by_rfid(self.db, rfid)
        
        if not student:
            messagebox.showerror("Not Found", f"No student found with RFID {rfid}.")
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", 
                                     f"Are you sure you want to delete student {student.get('name')}?")
        
        if confirm:
            try:
                # Delete student from database
                self.db.collection('students').document(student['id']).delete()
                messagebox.showinfo("Success", f"Student {student.get('name')} deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete student: {e}")
        
        self.manage_students()
    
    def list_students(self):
        """Show a list of all students"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        list_frame = ttk.Frame(self.root, padding=20)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(list_frame, text="Student List", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create tree view
        columns = ('name', 'rfid', 'department', 'year', 'section', 'balance')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Define headings
        tree.heading('name', text='Name')
        tree.heading('rfid', text='RFID')
        tree.heading('department', text='Department')
        tree.heading('year', text='Year')
        tree.heading('section', text='Section')
        tree.heading('balance', text='Wallet Balance')
        
        # Column widths
        tree.column('name', width=150)
        tree.column('rfid', width=100)
        tree.column('department', width=100)
        tree.column('year', width=50)
        tree.column('section', width=50)
        tree.column('balance', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Fetch and display students
        try:
            students_ref = self.db.collection('students').get()
            for student in students_ref:
                data = student.to_dict()
                tree.insert('', tk.END, values=(
                    data.get('name', 'Unknown'),
                    data.get('rfid', 'Unknown'),
                    data.get('department', ''),
                    data.get('year', ''),
                    data.get('section', ''),
                    f"₹ {data.get('wallet_balance', 0):.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch students: {e}")
        
        # Back button
        back_btn = ttk.Button(list_frame, text="Back", 
                             command=self.manage_students)
        back_btn.pack(pady=(20, 0))
    
    def manage_bus_routes(self):
        """Show interface to manage bus routes"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        route_frame = ttk.Frame(self.root, padding=20)
        route_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(route_frame, text="Bus Route Management", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Bus route functions
        add_btn = ttk.Button(route_frame, text="Add New Route", 
                            command=self.add_bus_route)
        add_btn.pack(fill=tk.X, pady=5)
        
        update_btn = ttk.Button(route_frame, text="Update Route", 
                               command=self.update_bus_route)
        update_btn.pack(fill=tk.X, pady=5)
        
        delete_btn = ttk.Button(route_frame, text="Delete Route", 
                               command=self.delete_bus_route)
        delete_btn.pack(fill=tk.X, pady=5)
        
        list_btn = ttk.Button(route_frame, text="List All Routes", 
                             command=self.list_bus_routes)
        list_btn.pack(fill=tk.X, pady=5)
        
        # Back button
        back_btn = ttk.Button(route_frame, text="Back to Admin Menu", 
                             command=self.show_admin_menu)
        back_btn.pack(fill=tk.X, pady=(20, 0))
    
    def add_bus_route(self):
        """Show form to add a new bus route"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        add_route_frame = ttk.Frame(self.root, padding=20)
        add_route_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(add_route_frame, text="Add New Bus Route", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Form frame
        form_frame = ttk.Frame(add_route_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Route ID
        route_id_label = ttk.Label(form_frame, text="Route ID:")
        route_id_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        route_id_entry = ttk.Entry(form_frame, width=30)
        route_id_entry.grid(row=0, column=1, padx=5, pady=5)
        route_id_entry.focus()
        
        # Route Name
        name_label = ttk.Label(form_frame, text="Route Name:")
        name_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        name_entry = ttk.Entry(form_frame, width=30)
        name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Stops
        stops_label = ttk.Label(form_frame, text="Stops (comma separated):")
        stops_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        stops_entry = ttk.Entry(form_frame, width=30)
        stops_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Example
        example_label = ttk.Label(form_frame, text="Example: Campus, Library, Downtown", font=('Arial', 9, 'italic'))
        example_label.grid(row=3, column=1, sticky="w", padx=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(add_route_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        # Add button
        add_btn = ttk.Button(buttons_frame, text="Add Route", 
                            command=lambda: self.save_new_route(
                                route_id_entry.get().strip(),
                                name_entry.get().strip(),
                                stops_entry.get().strip()
                            ))
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_btn = ttk.Button(buttons_frame, text="Clear", 
                              command=lambda: [entry.delete(0, tk.END) for entry in [route_id_entry, name_entry, stops_entry]])
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Back button
        back_btn = ttk.Button(buttons_frame, text="Back", 
                             command=self.manage_bus_routes)
        back_btn.pack(side=tk.RIGHT, padx=5)
        
        # Status message
        self.status_var = tk.StringVar()
        status_label = ttk.Label(add_route_frame, textvariable=self.status_var)
        status_label.pack(pady=10)
    
    def save_new_route(self, route_id, name, stops_str):
        """Save a new bus route to the database"""
        if not route_id or not name or not stops_str:
            self.status_var.set("Please fill in all fields.")
            return
        
        # Parse stops into a list
        stops = [stop.strip() for stop in stops_str.split(',') if stop.strip()]
        
        if len(stops) < 2:
            self.status_var.set("Please enter at least two stops.")
            return
        
        # Check if route ID already exists
        existing_routes = self.db.collection('bus_routes').where(filter=firestore.FieldFilter('route_id', '==', route_id)).limit(1).get()
        if len(list(existing_routes)) > 0:
            self.status_var.set(f"Route ID '{route_id}' already exists. Please use a different ID.")
            return
        
        try:
            # Create route document
            route_data = {
                'route_id': route_id,
                'name': name,
                'stops': stops,
                'timestamp': firestore.SERVER_TIMESTAMP
            }
            
            # Add to Firestore
            self.db.collection('bus_routes').add(route_data)
            
            # Show success message
            messagebox.showinfo("Success", f"Bus route '{name}' added successfully!")
            self.manage_bus_routes()
            
        except Exception as e:
            self.status_var.set(f"Error adding bus route: {e}")
    
    def update_bus_route(self):
        """Show interface to update a bus route"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        update_frame = ttk.Frame(self.root, padding=20)
        update_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(update_frame, text="Update Bus Route", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Search frame
        search_frame = ttk.Frame(update_frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        # Route selector
        search_label = ttk.Label(search_frame, text="Select Route:")
        search_label.pack(side=tk.LEFT, padx=5)
        
        # Get all routes for dropdown
        self.routes_data = {}
        try:
            routes = self.db.collection('bus_routes').get()
            route_ids = ["-- Select Route --"]
            
            for route in routes:
                route_data = route.to_dict()
                route_id = route_data.get('route_id')
                if route_id:
                    route_ids.append(route_id)
                    # Store route data with document ID for later use
                    self.routes_data[route_id] = {
                        'doc_id': route.id,
                        'data': route_data
                    }
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load routes: {e}")
            route_ids = ["-- No Routes Found --"]
        
        # Route dropdown
        self.route_var = tk.StringVar()
        route_dropdown = ttk.Combobox(search_frame, textvariable=self.route_var, values=route_ids, width=20)
        route_dropdown.current(0)
        route_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Select button
        select_btn = ttk.Button(search_frame, text="Select", 
                               command=self.load_route_for_update)
        select_btn.pack(side=tk.LEFT, padx=5)
        
        # Results frame (initially empty)
        self.update_results_frame = ttk.Frame(update_frame)
        self.update_results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Back button
        back_btn = ttk.Button(update_frame, text="Back", 
                             command=self.manage_bus_routes)
        back_btn.pack(side=tk.RIGHT, pady=10)
        
        # Status message
        self.status_var = tk.StringVar()
        status_label = ttk.Label(update_frame, textvariable=self.status_var)
        status_label.pack(pady=10)
    
    def load_route_for_update(self):
        """Load the selected route for updating"""
        route_id = self.route_var.get()
        
        if route_id == "-- Select Route --" or route_id == "-- No Routes Found --":
            self.status_var.set("Please select a valid route.")
            return
            
        if route_id not in self.routes_data:
            self.status_var.set(f"Route data for '{route_id}' not found.")
            return
            
        # Get the route data
        route_info = self.routes_data[route_id]
        doc_id = route_info['doc_id']
        route_data = route_info['data']
        
        # Clear the results frame
        for widget in self.update_results_frame.winfo_children():
            widget.destroy()
            
        # Create update form
        form_frame = ttk.Frame(self.update_results_frame)
        form_frame.pack(fill=tk.BOTH, pady=10)
        
        # Route ID (read-only)
        route_id_label = ttk.Label(form_frame, text="Route ID:")
        route_id_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        route_id_var = tk.StringVar(value=route_data.get('route_id', ''))
        route_id_entry = ttk.Entry(form_frame, width=30, textvariable=route_id_var, state='readonly')
        route_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Route Name
        name_label = ttk.Label(form_frame, text="Route Name:")
        name_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        name_var = tk.StringVar(value=route_data.get('name', ''))
        name_entry = ttk.Entry(form_frame, width=30, textvariable=name_var)
        name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Stops
        stops_label = ttk.Label(form_frame, text="Stops (comma separated):")
        stops_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        stops_str = ', '.join(route_data.get('stops', []))
        stops_var = tk.StringVar(value=stops_str)
        stops_entry = ttk.Entry(form_frame, width=30, textvariable=stops_var)
        stops_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Example
        example_label = ttk.Label(form_frame, text="Example: Campus, Library, Downtown", font=('Arial', 9, 'italic'))
        example_label.grid(row=3, column=1, sticky="w", padx=5)
        
        # Buttons
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Update button
        update_btn = ttk.Button(buttons_frame, text="Update Route", 
                               command=lambda: self.save_updated_route(
                                   doc_id,
                                   route_id_var.get(),
                                   name_var.get().strip(),
                                   stops_var.get().strip()
                               ))
        update_btn.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        delete_btn = ttk.Button(buttons_frame, text="Delete Route", 
                               command=lambda: self.confirm_delete_route(doc_id, route_id_var.get(), name_var.get()))
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_var.set(f"Route {route_id} loaded. Edit details below.")
    
    def save_updated_route(self, doc_id, route_id, name, stops_str):
        """Save updated route information to the database"""
        if not name or not stops_str:
            self.status_var.set("Route name and stops are required.")
            return
        
        # Parse stops into a list
        stops = [stop.strip() for stop in stops_str.split(',') if stop.strip()]
        
        if len(stops) < 2:
            self.status_var.set("Please enter at least two stops.")
            return
        
        try:
            # Update the route document
            route_data = {
                'name': name,
                'stops': stops,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            self.db.collection('bus_routes').document(doc_id).update(route_data)
            
            # Show success message
            messagebox.showinfo("Success", f"Bus route '{name}' updated successfully!")
            self.manage_bus_routes()
            
        except Exception as e:
            self.status_var.set(f"Error updating bus route: {e}")
    
    def confirm_delete_route(self, doc_id, route_id, name):
        """Confirm and delete a bus route"""
        # Check if any students are assigned to this route
        students_on_route = self.db.collection('students').where(filter=firestore.FieldFilter('bus_route', '==', route_id)).limit(1).get()
        
        if len(list(students_on_route)) > 0:
            messagebox.showerror("Cannot Delete", 
                               f"Route '{name}' has students assigned to it. Please reassign students before deleting.")
            return
        
        # Confirm deletion
        confirmed = messagebox.askyesno("Confirm Deletion", 
                                      f"Are you sure you want to delete the route '{name}'?")
        if not confirmed:
            return
            
        try:
            # Delete the route
            self.db.collection('bus_routes').document(doc_id).delete()
            
            # Show success message
            messagebox.showinfo("Success", f"Bus route '{name}' deleted successfully!")
            self.manage_bus_routes()
            
        except Exception as e:
            self.status_var.set(f"Error deleting bus route: {e}")
    
    def delete_bus_route(self):
        """Show interface to delete a bus route"""
        # This function now just redirects to update_bus_route which has delete functionality
        self.update_bus_route()
    
    def list_bus_routes(self):
        """Show a list of all bus routes"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        list_frame = ttk.Frame(self.root, padding=20)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(list_frame, text="Bus Routes", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Routes list frame
        routes_frame = ttk.Frame(list_frame)
        routes_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for routes
        columns = ('route_id', 'name', 'stops')
        self.routes_tree = ttk.Treeview(routes_frame, columns=columns, show='headings', height=10)
        
        # Define headings
        self.routes_tree.heading('route_id', text='Route ID')
        self.routes_tree.heading('name', text='Route Name')
        self.routes_tree.heading('stops', text='Stops')
        
        # Define columns
        self.routes_tree.column('route_id', width=100)
        self.routes_tree.column('name', width=150)
        self.routes_tree.column('stops', width=400)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(routes_frame, orient=tk.VERTICAL, command=self.routes_tree.yview)
        self.routes_tree.configure(yscroll=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.routes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load routes data
        self.load_bus_routes()
        
        # Export button
        export_btn = ttk.Button(list_frame, text="Export to CSV", 
                               command=self.export_routes_csv)
        export_btn.pack(side=tk.LEFT, pady=10)
        
        # Back button
        back_btn = ttk.Button(list_frame, text="Back", 
                             command=self.manage_bus_routes)
        back_btn.pack(side=tk.RIGHT, pady=10)
        
        # Status message
        self.status_var = tk.StringVar()
        status_label = ttk.Label(list_frame, textvariable=self.status_var)
        status_label.pack(pady=5)
    
    def load_bus_routes(self):
        """Load bus routes into the treeview"""
        try:
            # Clear existing data
            for item in self.routes_tree.get_children():
                self.routes_tree.delete(item)
                
            # Fetch bus routes
            routes = self.db.collection('bus_routes').get()
            
            count = 0
            for route in routes:
                route_data = route.to_dict()
                route_id = route_data.get('route_id', '')
                name = route_data.get('name', '')
                stops = ', '.join(route_data.get('stops', []))
                
                # Insert into treeview
                self.routes_tree.insert('', tk.END, values=(route_id, name, stops))
                count += 1
                
            self.status_var.set(f"Loaded {count} bus routes.")
            
        except Exception as e:
            self.status_var.set(f"Error loading bus routes: {e}")
    
    def export_routes_csv(self):
        """Export bus routes to CSV file"""
        try:
            from datetime import datetime
            import csv
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bus_routes_{timestamp}.csv"
            
            # Fetch routes data
            routes = self.db.collection('bus_routes').get()
            
            # Write to CSV
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Route ID', 'Route Name', 'Stops'])
                
                # Write data
                for route in routes:
                    route_data = route.to_dict()
                    route_id = route_data.get('route_id', '')
                    name = route_data.get('name', '')
                    stops = ', '.join(route_data.get('stops', []))
                    
                    writer.writerow([route_id, name, stops])
            
            messagebox.showinfo("Export Successful", f"Bus routes exported to {filename}")
            
        except Exception as e:
            self.status_var.set(f"Error exporting bus routes: {e}")
    
    def export_data(self):
        """Show interface to export data"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        export_frame = ttk.Frame(self.root, padding=20)
        export_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(export_frame, text="Export Data", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Export options
        students_btn = ttk.Button(export_frame, text="Export Students", 
                                 command=lambda: self.export_collection('students'))
        students_btn.pack(fill=tk.X, pady=5)
        
        attendance_btn = ttk.Button(export_frame, text="Export Attendance", 
                                   command=lambda: self.export_collection('attendance'))
        attendance_btn.pack(fill=tk.X, pady=5)
        
        transactions_btn = ttk.Button(export_frame, text="Export Transactions", 
                                     command=lambda: self.export_collection('transactions'))
        transactions_btn.pack(fill=tk.X, pady=5)
        
        library_btn = ttk.Button(export_frame, text="Export Library Records", 
                                command=lambda: self.export_collection('library_records'))
        library_btn.pack(fill=tk.X, pady=5)
        
        # Back button
        back_btn = ttk.Button(export_frame, text="Back to Admin Menu", 
                             command=self.show_admin_menu)
        back_btn.pack(fill=tk.X, pady=(20, 0))
    
    def export_collection(self, collection_name):
        """Export a collection to CSV"""
        try:
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not filename:
                return  # User canceled
            
            # Fetch data
            docs = self.db.collection(collection_name).get()
            
            if not docs:
                messagebox.showinfo("Export", f"No data found in {collection_name} collection.")
                return
            
            # Extract data and process for CSV
            all_data = []
            all_fields = set()
            
            # First pass: collect all data and build a complete set of fields
            for doc in docs:
                data = doc.to_dict()
                
                # Add document ID as a field
                data['document_id'] = doc.id
                
                # Add each field to our master set of fields
                for field in data.keys():
                    all_fields.add(field)
                
                all_data.append(data)
            
            if not all_data:
                messagebox.showinfo("Export", f"No data found in {collection_name} collection.")
                return
            
            # Get a sorted list of headers for consistent columns
            headers = sorted(list(all_fields))
            # Always put document_id first
            if 'document_id' in headers:
                headers.remove('document_id')
                headers.insert(0, 'document_id')
            
            # Convert all data to CSV-compatible format
            csv_data = []
            for item in all_data:
                csv_row = {}
                
                # Process each possible field
                for field in headers:
                    # Get the value if it exists, or empty string if not
                    value = item.get(field, '')
                    
                    # Convert complex types to strings
                    if isinstance(value, dict):
                        # Convert dictionary to a JSON string
                        csv_row[field] = str(value)
                    elif isinstance(value, list):
                        # Convert list to comma-separated string
                        csv_row[field] = ', '.join(str(x) for x in value)
                    elif isinstance(value, datetime.datetime):
                        # Format datetime as string
                        csv_row[field] = value.strftime("%Y-%m-%d %H:%M:%S")
                    elif value is None:
                        # Replace None with empty string
                        csv_row[field] = ''
                    else:
                        # Use value as is for simple types
                        csv_row[field] = value
                
                csv_data.append(csv_row)
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(csv_data)
            
            messagebox.showinfo("Export Successful", f"Data from {collection_name} exported successfully to {filename}!")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")
    
    def confirm_clear_database(self):
        """Confirm database clearing"""
        confirm = messagebox.askyesno("Confirm Clear Database", 
                                     "WARNING: This will delete ALL data from the database. This action cannot be undone. Are you absolutely sure?")
        
        if confirm:
            second_confirm = messagebox.askyesno("Final Confirmation", 
                                               "THIS IS YOUR FINAL WARNING: All data will be permanently deleted. Continue?")
            
            if second_confirm:
                self.clear_database()
    
    def clear_database(self):
        """Clear all data from the database"""
        try:
            # List of collections to clear
            collections = ['students', 'attendance', 'transactions', 'books', 'library_records', 'bus_routes']
            
            for collection in collections:
                docs = self.db.collection(collection).get()
                for doc in docs:
                    doc.reference.delete()
            
            messagebox.showinfo("Success", "Database cleared successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear database: {e}")
        
        self.show_admin_menu() 