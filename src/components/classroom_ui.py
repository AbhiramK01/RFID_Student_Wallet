import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import validate_rfid, get_student_by_rfid, check_attendance_exists, verify_face, decode_base64_to_face
import datetime
import csv
from firebase_admin import firestore

class ClassroomUI:
    def __init__(self, root, db, return_callback):
        self.root = root
        self.db = db
        self.return_callback = return_callback
        self.classroom_info = None
        
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.title("Classroom Interface - RFID Student Wallet Application")
        
        # Start with classroom selection
        self.classroom_selection()
    
    def classroom_selection(self):
        """Show classroom selection screen"""
        selection_frame = ttk.Frame(self.root, padding=20)
        selection_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(selection_frame, text="Classroom Selection", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Form for department, year, section
        form_frame = ttk.Frame(selection_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
        # Department
        dept_label = ttk.Label(form_frame, text="Department:")
        dept_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.dept_entry = ttk.Entry(form_frame)
        self.dept_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Year
        year_label = ttk.Label(form_frame, text="Year:")
        year_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.year_entry = ttk.Entry(form_frame)
        self.year_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Section
        section_label = ttk.Label(form_frame, text="Section:")
        section_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        self.section_entry = ttk.Entry(form_frame)
        self.section_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # Submit button
        submit_btn = ttk.Button(selection_frame, text="Enter Classroom", 
                               command=self.enter_classroom)
        submit_btn.pack(pady=10)
        
        # Back button
        back_btn = ttk.Button(selection_frame, text="Back to Main Menu", 
                             command=self.return_callback)
        back_btn.pack(pady=(20, 0))
    
    def enter_classroom(self):
        """Process classroom selection and enter classroom"""
        department = self.dept_entry.get().strip().upper()
        year = self.year_entry.get().strip()
        section = self.section_entry.get().strip().upper()
        
        # Basic validation
        if not all([department, year, section]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        try:
            year = int(year)
            if year < 1 or year > 5:
                raise ValueError("Year must be between 1 and 5")
        except ValueError as e:
            messagebox.showerror("Invalid Year", str(e))
            return
        
        if len(section) != 1 or not section.isalpha():
            messagebox.showerror("Invalid Section", "Section must be a single letter.")
            return
        
        # Store classroom info
        self.classroom_info = {
            'department': department,
            'year': year,
            'section': section,
            'key': f"{department}_{year}_{section}"
        }
        
        # Check if classroom exists, if not create it
        classroom_ref = self.db.collection('classrooms').document(self.classroom_info['key'])
        classroom_doc = classroom_ref.get()
        
        if not classroom_doc.exists:
            # Create new classroom record
            classroom_ref.set({
                'department': department,
                'year': year,
                'section': section,
                'created_at': datetime.datetime.now()
            })
        
        # Show classroom interface
        self.show_classroom_ui()
    
    def show_classroom_ui(self):
        """Show the main classroom interface"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        classroom_frame = ttk.Frame(self.root, padding=20)
        classroom_frame.pack(fill=tk.BOTH, expand=True)
        
        # Classroom info header
        info_text = f"Department: {self.classroom_info['department']} | Year: {self.classroom_info['year']} | Section: {self.classroom_info['section']}"
        info_label = ttk.Label(classroom_frame, text=info_text, font=('Arial', 12, 'bold'))
        info_label.pack(pady=(0, 20))
        
        # Date display
        today = datetime.datetime.now().strftime("%d-%m-%Y")
        date_label = ttk.Label(classroom_frame, text=f"Date: {today}")
        date_label.pack(pady=(0, 20))
        
        # Classroom functions
        mark_btn = ttk.Button(classroom_frame, text="Mark Attendance", 
                             command=self.mark_attendance_ui)
        mark_btn.pack(fill=tk.X, pady=5)
        
        check_btn = ttk.Button(classroom_frame, text="Check Student Attendance", 
                              command=self.check_attendance_ui)
        check_btn.pack(fill=tk.X, pady=5)
        
        export_btn = ttk.Button(classroom_frame, text="Export Attendance Sheet", 
                               command=self.export_attendance)
        export_btn.pack(fill=tk.X, pady=5)
        
        # Back button
        back_btn = ttk.Button(classroom_frame, text="Change Classroom", 
                             command=self.classroom_selection)
        back_btn.pack(fill=tk.X, pady=5)
        
        main_menu_btn = ttk.Button(classroom_frame, text="Back to Main Menu", 
                                  command=self.return_callback)
        main_menu_btn.pack(fill=tk.X, pady=(20, 0))
    
    def mark_attendance_ui(self):
        """Show interface to mark attendance"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        attendance_frame = ttk.Frame(self.root, padding=20)
        attendance_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title and info
        title_label = ttk.Label(attendance_frame, 
                              text=f"Mark Attendance - {self.classroom_info['department']} Year {self.classroom_info['year']} Section {self.classroom_info['section']}", 
                              font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Date display
        today = datetime.datetime.now().strftime("%d-%m-%Y")
        date_label = ttk.Label(attendance_frame, text=f"Date: {today}")
        date_label.pack(pady=(0, 10))
        
        # Instructions
        instr_label = ttk.Label(attendance_frame, 
                              text="Tap RFID card to mark attendance. Face verification will be required.")
        instr_label.pack(pady=(0, 20))
        
        # RFID input
        rfid_frame = ttk.Frame(attendance_frame)
        rfid_frame.pack(fill=tk.X, pady=10)
        
        rfid_label = ttk.Label(rfid_frame, text="Student RFID:")
        rfid_label.pack(side=tk.LEFT, padx=5)
        
        self.attendance_rfid_entry = ttk.Entry(rfid_frame, width=15)
        self.attendance_rfid_entry.pack(side=tk.LEFT, padx=5)
        self.attendance_rfid_entry.focus()
        
        # Submit button
        submit_btn = ttk.Button(rfid_frame, text="Submit", 
                               command=self.process_attendance)
        submit_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to submit
        self.attendance_rfid_entry.bind('<Return>', lambda event: self.process_attendance())
        
        # Status label for feedback
        self.status_label = ttk.Label(attendance_frame, text="")
        self.status_label.pack(pady=(10, 0))
        
        # Treeview to display marked attendance
        tree_frame = ttk.Frame(attendance_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=20)
        
        # Create columns
        columns = ('time', 'name', 'rfid', 'status')
        self.attendance_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Define headings
        self.attendance_tree.heading('time', text='Time')
        self.attendance_tree.heading('name', text='Student Name')
        self.attendance_tree.heading('rfid', text='RFID')
        self.attendance_tree.heading('status', text='Status')
        
        # Column widths
        self.attendance_tree.column('time', width=100)
        self.attendance_tree.column('name', width=200)
        self.attendance_tree.column('rfid', width=100)
        self.attendance_tree.column('status', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.attendance_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load today's attendance
        self.load_today_attendance()
        
        # Back button
        back_btn = ttk.Button(attendance_frame, text="Back", 
                             command=self.show_classroom_ui)
        back_btn.pack(pady=(10, 0))
    
    def load_today_attendance(self):
        """Load today's attendance records for the classroom"""
        try:
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Clear existing tree items
            for item in self.attendance_tree.get_children():
                self.attendance_tree.delete(item)
            
            # Query for today's attendance for this classroom
            attendance_ref = self.db.collection('attendance')
            query = attendance_ref.where(
                filter=firestore.FieldFilter('classroom_key', '==', self.classroom_info['key'])
            ).where(
                filter=firestore.FieldFilter('date', '==', today_str)
            )
            
            results = query.get()
            
            for doc in results:
                data = doc.to_dict()
                time_str = data.get('timestamp').strftime("%H:%M:%S") if data.get('timestamp') else "Unknown"
                self.attendance_tree.insert('', tk.END, values=(
                    time_str,
                    data.get('student_name', 'Unknown'),
                    data.get('student_rfid', 'Unknown'),
                    "Present"
                ))
        except Exception as e:
            print(f"Error loading attendance records: {e}")
    
    def process_attendance(self):
        """Process student attendance with RFID and face verification"""
        rfid = self.attendance_rfid_entry.get().strip()
        
        if not validate_rfid(rfid):
            self.status_label.config(text="Invalid RFID format. Please try again.", foreground="red")
            return
        
        # Check if student exists
        student = get_student_by_rfid(self.db, rfid)
        
        if not student:
            self.status_label.config(text=f"No student found with RFID {rfid}.", foreground="red")
            return
        
        # Check if student belongs to this classroom
        if student.get('department') != self.classroom_info['department'] or \
           int(student.get('year')) != self.classroom_info['year'] or \
           student.get('section') != self.classroom_info['section']:
            
            self.status_label.config(
                text=f"Student {student.get('name')} does not belong to this classroom.",
                foreground="red"
            )
            return
        
        # Check if attendance already marked for today
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        already_marked = check_attendance_exists(self.db, student['id'], today_str)
        
        if already_marked:
            self.status_label.config(
                text=f"Attendance for {student.get('name')} already marked today.",
                foreground="orange"
            )
            return
        
        # Get the stored face data
        face_data_base64 = student.get('face_data')
        
        if not face_data_base64:
            self.status_label.config(
                text=f"No face data registered for {student.get('name')}. Cannot verify identity.",
                foreground="red"
            )
            return
        
        # Decode face data
        known_face_encodings = decode_base64_to_face(face_data_base64)
        
        if known_face_encodings is None:
            self.status_label.config(
                text=f"Error decoding face data for {student.get('name')}.",
                foreground="red"
            )
            return
        
        # Show message before face verification
        self.status_label.config(
            text=f"Starting face verification for {student.get('name')}. Please look at the camera.\n"
                 "You'll need to match your face for 5 consecutive good quality frames.\n"
                 "Keep your face steady and ensure good lighting.",
            foreground="blue"
        )
        self.root.update()  # Update the display to show the message
        
        # Perform face verification with very strict tolerance
        # Use 0.4 for even stricter matching if needed
        face_verified = verify_face(known_face_encodings, camera_index=0, tolerance=0.45)
        
        if not face_verified:
            self.status_label.config(
                text=f"Face verification failed. Face does not match registered data for {student.get('name')}.\n"
                     "This may be due to:\n"
                     "1. Different person attempting verification\n"
                     "2. Poor lighting conditions\n"
                     "3. Face not clearly visible or at wrong angle",
                foreground="red"
            )
            return
        
        # All checks passed, mark attendance
        now = datetime.datetime.now()
        
        attendance_data = {
            'student_id': student['id'],
            'student_name': student.get('name'),
            'student_rfid': rfid,
            'classroom_key': self.classroom_info['key'],
            'department': self.classroom_info['department'],
            'year': self.classroom_info['year'],
            'section': self.classroom_info['section'],
            'date': today_str,
            'timestamp': now,
            'time_str': now.strftime("%H:%M:%S"),
            'status': 'present',
            'verification_method': 'face_recognition',
            'verification_strictness': 'high',
            'course': f"{self.classroom_info['department']} Year {self.classroom_info['year']} Section {self.classroom_info['section']}"
        }
        
        try:
            # Add to database
            self.db.collection('attendance').add(attendance_data)
            
            # Update UI
            self.status_label.config(
                text=f"Attendance marked successfully for {student.get('name')}.\n"
                     f"Face verification passed at {now.strftime('%H:%M:%S')} with high security settings.",
                foreground="green"
            )
            
            # Add to treeview
            self.attendance_tree.insert('', 0, values=(
                now.strftime("%H:%M:%S"),
                student.get('name'),
                rfid,
                "Present (Face Verified)"
            ))
            
            # Clear RFID entry for next student
            self.attendance_rfid_entry.delete(0, tk.END)
            self.attendance_rfid_entry.focus()
            
        except Exception as e:
            self.status_label.config(
                text=f"Error marking attendance: {e}",
                foreground="red"
            )
    
    def check_attendance_ui(self):
        """Show interface to check a student's attendance"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        check_frame = ttk.Frame(self.root, padding=20)
        check_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(check_frame, text="Check Student Attendance", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # RFID input
        rfid_frame = ttk.Frame(check_frame)
        rfid_frame.pack(fill=tk.X, pady=10)
        
        rfid_label = ttk.Label(rfid_frame, text="Student RFID:")
        rfid_label.pack(side=tk.LEFT, padx=5)
        
        self.check_rfid_entry = ttk.Entry(rfid_frame, width=15)
        self.check_rfid_entry.pack(side=tk.LEFT, padx=5)
        self.check_rfid_entry.focus()
        
        # Submit button
        submit_btn = ttk.Button(rfid_frame, text="Check", 
                               command=self.display_student_attendance)
        submit_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to submit
        self.check_rfid_entry.bind('<Return>', lambda event: self.display_student_attendance())
        
        # Student info display
        self.student_info_label = ttk.Label(check_frame, text="")
        self.student_info_label.pack(pady=10)
        
        # Month selection
        month_frame = ttk.Frame(check_frame)
        month_frame.pack(fill=tk.X, pady=10)
        
        month_label = ttk.Label(month_frame, text="Month:")
        month_label.pack(side=tk.LEFT, padx=5)
        
        # Month dropdown
        months = ["January", "February", "March", "April", "May", "June", 
                 "July", "August", "September", "October", "November", "December"]
        current_month = datetime.datetime.now().month - 1  # 0-based index
        
        self.month_var = tk.StringVar(value=months[current_month])
        month_dropdown = ttk.Combobox(month_frame, textvariable=self.month_var, values=months, state="readonly")
        month_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Year entry
        year_label = ttk.Label(month_frame, text="Year:")
        year_label.pack(side=tk.LEFT, padx=5)
        
        current_year = datetime.datetime.now().year
        self.year_var = tk.StringVar(value=str(current_year))
        year_entry = ttk.Entry(month_frame, textvariable=self.year_var, width=6)
        year_entry.pack(side=tk.LEFT, padx=5)
        
        # Attendance display
        attendance_frame = ttk.Frame(check_frame)
        attendance_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for listing attendance
        columns = ('date', 'time', 'status')
        self.check_tree = ttk.Treeview(attendance_frame, columns=columns, show='headings')
        
        # Define headings
        self.check_tree.heading('date', text='Date')
        self.check_tree.heading('time', text='Time')
        self.check_tree.heading('status', text='Status')
        
        # Column widths
        self.check_tree.column('date', width=100)
        self.check_tree.column('time', width=100)
        self.check_tree.column('status', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(attendance_frame, orient=tk.VERTICAL, command=self.check_tree.yview)
        self.check_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.check_tree.pack(fill=tk.BOTH, expand=True)
        
        # Attendance summary
        self.summary_label = ttk.Label(check_frame, text="")
        self.summary_label.pack(pady=10)
        
        # Back button
        back_btn = ttk.Button(check_frame, text="Back", 
                             command=self.show_classroom_ui)
        back_btn.pack(pady=(10, 0))
    
    def display_student_attendance(self):
        """Display attendance records for a student"""
        rfid = self.check_rfid_entry.get().strip()
        
        if not validate_rfid(rfid):
            self.student_info_label.config(text="Invalid RFID format. Please try again.", foreground="red")
            return
        
        # Check if student exists
        student = get_student_by_rfid(self.db, rfid)
        
        if not student:
            self.student_info_label.config(text=f"No student found with RFID {rfid}.", foreground="red")
            return
        
        # Display student info
        self.student_info_label.config(
            text=f"Student: {student.get('name')} ({student.get('department')} Year {student.get('year')} Section {student.get('section')})",
            foreground="black"
        )
        
        # Get selected month and year
        month_str = self.month_var.get()
        months = ["January", "February", "March", "April", "May", "June", 
                 "July", "August", "September", "October", "November", "December"]
        month_num = months.index(month_str) + 1  # 1-based month number
        
        try:
            year = int(self.year_var.get())
        except ValueError:
            self.summary_label.config(text="Invalid year format.", foreground="red")
            return
        
        # Clear existing tree items
        for item in self.check_tree.get_children():
            self.check_tree.delete(item)
        
        try:
            # Query for attendance in the selected month/year for this student
            # This is a simplified approach - in a real app, you'd use proper date filtering
            attendance_ref = self.db.collection('attendance')
            all_records = attendance_ref.where(
                filter=firestore.FieldFilter('student_id', '==', student['id'])
            ).get()
            
            # Filter by month/year manually (Firestore doesn't have built-in date part filtering)
            month_records = []
            for doc in all_records:
                data = doc.to_dict()
                date_obj = datetime.datetime.strptime(data.get('date', ''), "%Y-%m-%d")
                
                if date_obj.month == month_num and date_obj.year == year:
                    month_records.append(data)
            
            # Sort by date
            month_records.sort(key=lambda x: x.get('date', ''))
            
            # Display in treeview
            for record in month_records:
                date_str = datetime.datetime.strptime(record.get('date', ''), "%Y-%m-%d").strftime("%d-%m-%Y")
                time_str = record.get('time_str', 'Unknown')
                
                self.check_tree.insert('', tk.END, values=(
                    date_str,
                    time_str,
                    "Present"
                ))
            
            # Calculate attendance percentage
            # Get days in month
            days_in_month = 0
            if month_num in [1, 3, 5, 7, 8, 10, 12]:
                days_in_month = 31
            elif month_num in [4, 6, 9, 11]:
                days_in_month = 30
            elif month_num == 2:
                # Simple leap year check
                if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                    days_in_month = 29
                else:
                    days_in_month = 28
            
            # For a simple implementation, assume all days are working days
            # A real application would account for holidays, weekends, etc.
            working_days = days_in_month  # Simplified
            present_days = len(month_records)
            
            if working_days > 0:
                attendance_percentage = (present_days / working_days) * 100
                self.summary_label.config(
                    text=f"Present: {present_days} days out of {working_days} working days ({attendance_percentage:.2f}%)",
                    foreground="black"
                )
            else:
                self.summary_label.config(
                    text="No working days in selected month.",
                    foreground="black"
                )
                
        except Exception as e:
            self.summary_label.config(
                text=f"Error retrieving attendance records: {e}",
                foreground="red"
            )
    
    def export_attendance(self):
        """Export attendance sheet for the classroom"""
        try:
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not filename:
                return  # User canceled
            
            # Get month and year for export
            today = datetime.datetime.now()
            month_num = today.month
            year = today.year
            
            # Fetch students in this classroom
            students_ref = self.db.collection('students')
            query = students_ref.where(
                filter=firestore.FieldFilter('department', '==', self.classroom_info['department'])
            ).where(
                filter=firestore.FieldFilter('year', '==', str(self.classroom_info['year']))
            ).where(
                filter=firestore.FieldFilter('section', '==', self.classroom_info['section'])
            )
            
            students = {}
            for doc in query.get():
                student_data = doc.to_dict()
                students[doc.id] = student_data
            
            if not students:
                messagebox.showinfo("Export", "No students found in this classroom.")
                return
            
            # Fetch attendance records for this classroom
            attendance_ref = self.db.collection('attendance')
            query = attendance_ref.where(
                filter=firestore.FieldFilter('classroom_key', '==', self.classroom_info['key'])
            )
            
            all_records = query.get()
            
            # Filter by month/year manually
            month_records = {}
            for doc in all_records:
                data = doc.to_dict()
                date_obj = datetime.datetime.strptime(data.get('date', ''), "%Y-%m-%d")
                
                if date_obj.month == month_num and date_obj.year == year:
                    student_id = data.get('student_id')
                    date = data.get('date')
                    
                    if student_id not in month_records:
                        month_records[student_id] = set()
                    
                    month_records[student_id].add(date)
            
            # Get all dates in the month
            days_in_month = 31  # Simplification - a real app would calculate correctly
            all_days = []
            for day in range(1, days_in_month + 1):
                date_str = f"{year}-{month_num:02d}-{day:02d}"
                all_days.append(date_str)
            
            # Prepare data for CSV
            csv_data = []
            headers = ['Roll No', 'Name', 'RFID'] + [f'{day}' for day in range(1, days_in_month + 1)] + ['Present', 'Absent', 'Percentage']
            
            for student_id, student_data in students.items():
                row = [
                    student_data.get('id', 'Unknown'),
                    student_data.get('name', 'Unknown'),
                    student_data.get('rfid', 'Unknown')
                ]
                
                # Add attendance for each day
                present_count = 0
                for day_str in all_days:
                    if student_id in month_records and day_str in month_records[student_id]:
                        row.append('P')
                        present_count += 1
                    else:
                        row.append('A')
                
                # Add summary
                absent_count = days_in_month - present_count
                if days_in_month > 0:
                    percentage = (present_count / days_in_month) * 100
                else:
                    percentage = 0
                
                row.extend([present_count, absent_count, f"{percentage:.2f}%"])
                csv_data.append(row)
            
            # Write to CSV
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(csv_data)
            
            messagebox.showinfo("Export Successful", f"Attendance sheet exported successfully to {filename}!")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export attendance: {e}") 