import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import datetime
from firebase_admin import firestore

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import validate_rfid, read_rfid_input, format_currency

class StudentUI:
    def __init__(self, root, db, go_back_callback=None):
        self.root = root
        self.db = db
        self.go_back_callback = go_back_callback
        
        # Clear the current window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.title("RFID Student Wallet - Student Interface")
        
        # Create a frame for the main content
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Show the RFID input screen
        self.show_rfid_input()
    
    def show_rfid_input(self):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Title
        title_label = ttk.Label(self.main_frame, text="Student Information", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame for RFID input
        rfid_frame = ttk.Frame(self.main_frame)
        rfid_frame.pack(pady=20, fill=tk.X)
        
        ttk.Label(rfid_frame, text="Tap or Enter your RFID:").pack(side=tk.LEFT, padx=5)
        self.rfid_entry = ttk.Entry(rfid_frame, width=15)
        self.rfid_entry.pack(side=tk.LEFT, padx=5)
        self.rfid_entry.focus()
        
        # Submit button
        ttk.Button(rfid_frame, text="Submit", 
                  command=self.process_rfid).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to the callback
        self.rfid_entry.bind('<Return>', lambda event: self.process_rfid())
        
        # Back button if callback exists
        if self.go_back_callback:
            ttk.Button(self.main_frame, text="Back to Main Menu", 
                      command=self.go_back_callback).pack(pady=20)
    
    def process_rfid(self):
        rfid = self.rfid_entry.get().strip()
        
        if not validate_rfid(rfid):
            messagebox.showerror("Invalid RFID", "Please enter a valid 10-digit RFID.")
            return
            
        # Get student by RFID
        try:
            students_ref = self.db.collection('students')
            query = students_ref.where(filter=firestore.FieldFilter('rfid', '==', rfid)).limit(1)
            results = query.get()
            
            student = None
            for doc in results:
                student = {'id': doc.id, **doc.to_dict()}
                break
                
            if not student:
                messagebox.showerror("Student Not Found", "No student found with this RFID.")
                return
                
            # Display student information
            self.display_student_info(student)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def display_student_info(self, student):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create a frame for student information
        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header with student info
        header_frame = ttk.Frame(info_frame)
        header_frame.pack(fill=tk.X)
        
        # Student name and header
        name = student.get('name', 'Unknown Student')
        department = student.get('department', 'N/A')
        year = student.get('year', 'N/A')
        section = student.get('section', 'N/A')
        rfid = student.get('rfid', 'N/A')
        
        # Main header with student name
        ttk.Label(header_frame, text=name, font=("Helvetica", 16, "bold")).pack(anchor=tk.W)
        
        # Student details
        details_text = f"RFID: {rfid} | Department: {department} | Year: {year} | Section: {section}"
        ttk.Label(header_frame, text=details_text).pack(anchor=tk.W, pady=(0, 10))
        
        # Create a frame with two columns
        details_frame = ttk.Frame(info_frame)
        details_frame.pack(fill=tk.X, pady=10)
        
        # Left column - Personal details
        left_frame = ttk.Frame(details_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(left_frame, text="Personal Details:", font=("Helvetica", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(left_frame, text=f"RFID: {student.get('rfid', 'N/A')}").pack(anchor=tk.W, pady=2)
        ttk.Label(left_frame, text=f"Department: {student.get('department', 'N/A')}").pack(anchor=tk.W, pady=2)
        ttk.Label(left_frame, text=f"Year: {student.get('year', 'N/A')}").pack(anchor=tk.W, pady=2)
        ttk.Label(left_frame, text=f"Section: {student.get('section', 'N/A')}").pack(anchor=tk.W, pady=2)
        ttk.Label(left_frame, text=f"Parent's Email: {student.get('parent_email', 'N/A')}").pack(anchor=tk.W, pady=2)
        
        # Right column - Wallet & Services
        right_frame = ttk.Frame(details_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(right_frame, text="Wallet:", font=("Helvetica", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(right_frame, text=f"Balance: {format_currency(student.get('wallet_balance', 0))}", 
                 font=("Helvetica", 12)).pack(anchor=tk.W, pady=2)
        
        # Fetch and display attendance percentage
        self.display_attendance_info(right_frame, student['id'])
        
        # Fetch and display library info
        self.display_library_info(right_frame, student['id'])
        
        # Fetch and display bus info
        self.display_bus_info(right_frame, student['id'])
        
        # Recent Activity
        activity_frame = ttk.Frame(info_frame)
        activity_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(activity_frame, text="Recent Activity:", font=("Helvetica", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Create a treeview to display recent activity
        columns = ("date", "type", "details")
        tree = ttk.Treeview(activity_frame, columns=columns, show="headings", height=6)
        
        # Configure column headings
        tree.heading("date", text="Date & Time")
        tree.heading("type", text="Type")
        tree.heading("details", text="Details")
        
        # Configure column widths
        tree.column("date", width=150)
        tree.column("type", width=100)
        tree.column("details", width=350)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(activity_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the treeview and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Fetch and display recent activity
        self.load_recent_activity(tree, student['id'])
        
        # Back button
        ttk.Button(self.main_frame, text="Back", 
                  command=self.show_rfid_input).pack(pady=10)
    
    def display_attendance_info(self, parent_frame, student_id):
        try:
            # Get attendance records for this month
            today = datetime.datetime.now()
            first_day = datetime.datetime(today.year, today.month, 1)
            
            attendance_ref = self.db.collection('attendance')
            # Instead of using timestamp filtering with where clause, we'll fetch all and filter in memory
            query = attendance_ref.where(filter=firestore.FieldFilter('student_id', '==', student_id))
            
            results = query.get()
            
            # Count attendance days after filtering in memory
            present_days = 0
            
            # Track dates to handle potential duplicate entries
            present_dates = set()
            
            for doc in results:
                data = doc.to_dict()
                # Filter by date in memory - ensure naive datetime comparison
                timestamp = data.get('timestamp')
                if timestamp:
                    # Convert to naive datetime if it's timezone-aware
                    if hasattr(timestamp, 'tzinfo') and timestamp.tzinfo is not None:
                        timestamp = timestamp.replace(tzinfo=None)
                    
                    if timestamp >= first_day:
                        # Use date string to avoid duplicates
                        date_str = data.get('date')
                        if date_str and date_str not in present_dates:
                            present_dates.add(date_str)
                            if data.get('status') == 'present':
                                present_days += 1
            
            # Calculate working days in the month (excluding weekends)
            year = today.year
            month = today.month
            
            # Get days in month
            days_in_month = 0
            if month in [1, 3, 5, 7, 8, 10, 12]:
                days_in_month = 31
            elif month in [4, 6, 9, 11]:
                days_in_month = 30
            elif month == 2:
                # Simple leap year check
                if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                    days_in_month = 29
                else:
                    days_in_month = 28
            
            # For this implementation, we'll consider working days as weekdays (Mon-Fri)
            working_days = 0
            for day in range(1, days_in_month + 1):
                date = datetime.datetime(year, month, day)
                # Only count weekdays (0 = Monday, 6 = Sunday)
                if date.weekday() < 5:  # 0-4 are weekdays
                    working_days += 1
            
            # Calculate percentage
            percentage = (present_days / working_days * 100) if working_days > 0 else 0
            
            ttk.Label(parent_frame, text="Attendance:", font=("Helvetica", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))
            ttk.Label(parent_frame, text=f"{present_days}/{working_days} days ({percentage:.1f}%)").pack(anchor=tk.W, pady=2)
            
        except Exception as e:
            print(f"Error loading attendance: {e}")
            ttk.Label(parent_frame, text="Attendance: Error loading data", foreground="red").pack(anchor=tk.W, pady=2)
    
    def display_library_info(self, parent_frame, student_id):
        try:
            # Get books currently borrowed
            library_records_ref = self.db.collection('library_records')
            query = library_records_ref.where(
                filter=firestore.FieldFilter('student_id', '==', student_id)
            ).where(
                filter=firestore.FieldFilter('status', '==', 'lent')
            )
            
            results = query.get()
            
            # Count books
            borrowed_books = []
            
            for doc in results:
                data = doc.to_dict()
                borrowed_books.append({
                    'title': data.get('book_title', 'Unknown Book'),
                    'due_date': data.get('due_date'),
                    'book_id': data.get('book_id', 'Unknown')
                })
            
            ttk.Label(parent_frame, text="Library:", font=("Helvetica", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))
            
            if borrowed_books:
                ttk.Label(parent_frame, text=f"{len(borrowed_books)} book(s) borrowed").pack(anchor=tk.W, pady=2)
                
                # List all borrowed books with their due dates
                for i, book in enumerate(borrowed_books):
                    title = book['title']
                    book_id = book['book_id']
                    
                    # Format due date
                    if book['due_date']:
                        due_date = book['due_date']
                        if isinstance(due_date, datetime.datetime):
                            due_date_str = due_date.strftime("%Y-%m-%d")
                        else:
                            due_date_str = str(due_date)
                    else:
                        due_date_str = "Unknown"
                    
                    # Display each book with a limited title length to fit in the UI
                    if len(title) > 25:
                        title = title[:22] + "..."
                    
                    book_text = f"{i+1}. {title} (Due: {due_date_str})"
                    ttk.Label(parent_frame, text=book_text).pack(anchor=tk.W, pady=1)
            else:
                ttk.Label(parent_frame, text="No books currently borrowed").pack(anchor=tk.W, pady=2)
            
        except Exception as e:
            print(f"Error loading library info: {e}")
            ttk.Label(parent_frame, text="Library: Error loading data", foreground="red").pack(anchor=tk.W, pady=2)
    
    def display_bus_info(self, parent_frame, student_id):
        try:
            # Get bus route information
            student_ref = self.db.collection('students').document(student_id)
            student_data = student_ref.get()
            
            if student_data.exists:
                data = student_data.to_dict()
                bus_route_id = data.get('bus_route')
                
                ttk.Label(parent_frame, text="Transport:", font=("Helvetica", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))
                
                if bus_route_id:
                    # Get route details by route_id field
                    query = self.db.collection('bus_routes').where(
                        filter=firestore.FieldFilter('route_id', '==', bus_route_id)
                    ).limit(1)
                    routes = query.get()
                    
                    if routes and len(routes) > 0:
                        route_info = routes[0].to_dict()
                        route_name = route_info.get('name', 'Unknown')
                        
                        ttk.Label(parent_frame, text=f"Route: {route_name}").pack(anchor=tk.W, pady=2)
                    else:
                        ttk.Label(parent_frame, text=f"Route ID: {bus_route_id}").pack(anchor=tk.W, pady=2)
                else:
                    ttk.Label(parent_frame, text="No bus route assigned").pack(anchor=tk.W, pady=2)
            else:
                ttk.Label(parent_frame, text="Student data not available").pack(anchor=tk.W, pady=2)
            
        except Exception as e:
            print(f"Error loading bus info: {e}")
            ttk.Label(parent_frame, text="Transport: Error loading data", foreground="red").pack(anchor=tk.W, pady=2)
    
    def load_recent_activity(self, tree, student_id):
        try:
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)
                
            # Combine all activities
            all_activities = []
            
            # Get transactions - without using order_by in Firestore
            transactions_ref = self.db.collection('transactions')
            txn_query = transactions_ref.where(filter=firestore.FieldFilter('student_id', '==', student_id))
            transactions = list(txn_query.get())
            
            for tx in transactions:
                tx_data = tx.to_dict()
                timestamp = tx_data.get('timestamp')
                if not timestamp:
                    continue
                
                date_str = timestamp.strftime("%Y-%m-%d %H:%M") if timestamp else "N/A"
                
                amount = format_currency(tx_data.get('amount', 0))
                tx_type = tx_data.get('type', 'unknown')
                description = tx_data.get('description', '')
                
                details = f"{amount} {'received' if tx_type == 'credit' else 'spent'}"
                if description:
                    details += f" - {description}"
                
                all_activities.append({
                    'timestamp': timestamp,
                    'date_str': date_str,
                    'type': 'Wallet',
                    'details': details
                })
            
            # Get attendance - without using order_by in Firestore
            attendance_ref = self.db.collection('attendance')
            att_query = attendance_ref.where(filter=firestore.FieldFilter('student_id', '==', student_id))
            attendance = list(att_query.get())
            
            for att in attendance:
                att_data = att.to_dict()
                timestamp = att_data.get('timestamp')
                if not timestamp:
                    continue
                
                date_str = timestamp.strftime("%Y-%m-%d %H:%M") if timestamp else "N/A"
                
                status = att_data.get('status', 'unknown')
                course = att_data.get('classroom_key', 'Unknown')
                department = att_data.get('department', '')
                year = att_data.get('year', '')
                section = att_data.get('section', '')
                
                # Create a more descriptive course name
                if department and year and section:
                    course_desc = f"{department} Year {year} Section {section}"
                else:
                    course_desc = course
                
                all_activities.append({
                    'timestamp': timestamp,
                    'date_str': date_str,
                    'type': 'Attendance',
                    'details': f"Marked {status} for {course_desc}"
                })
            
            # Get library activity - without using order_by in Firestore
            library_ref = self.db.collection('library_records')
            lib_query = library_ref.where(filter=firestore.FieldFilter('student_id', '==', student_id))
            library = list(lib_query.get())
            
            # Track which books have return records to avoid duplicates
            books_with_return_records = set()
            
            # First pass - identify which books have dedicated return records
            for lib in library:
                lib_data = lib.to_dict()
                if lib_data.get('status') == 'return_record':
                    # Add to our tracking set - combine book_id and original_lent_date to ensure uniqueness
                    book_id = lib_data.get('book_id', '')
                    original_lent_date = lib_data.get('original_lent_date', '')
                    books_with_return_records.add(f"{book_id}_{original_lent_date}")
            
            # Second pass - process all records
            for lib in library:
                lib_data = lib.to_dict()
                timestamp = lib_data.get('timestamp')
                if not timestamp:
                    continue
                
                date_str = timestamp.strftime("%Y-%m-%d %H:%M") if timestamp else "N/A"
                book_title = lib_data.get('book_title', 'Unknown book')
                status = lib_data.get('status')
                book_id = lib_data.get('book_id', '')
                lent_date = lib_data.get('lent_date', '')
                
                # Handle different record types
                if status == 'lent':
                    # Original lending record
                    all_activities.append({
                        'timestamp': timestamp,
                        'date_str': date_str,
                        'type': 'Library',
                        'details': f"Borrowed '{book_title}'"
                    })
                
                elif status == 'return_record':
                    # This is a dedicated return record (new format)
                    all_activities.append({
                        'timestamp': timestamp,
                        'date_str': date_str,
                        'type': 'Library',
                        'details': f"Returned '{book_title}'"
                    })
                
                elif status == 'returned' and not f"{book_id}_{lent_date}" in books_with_return_records:
                    # Old format records that have been updated with returned status
                    # BUT ONLY if we don't already have a dedicated return record for this book
                    # Get the return timestamp if available
                    return_timestamp = lib_data.get('return_timestamp')
                    return_date = lib_data.get('return_date')
                    
                    if return_timestamp:
                        # Use the return timestamp for the activity
                        if hasattr(return_timestamp, 'tzinfo') and return_timestamp.tzinfo is not None:
                            return_timestamp = return_timestamp.replace(tzinfo=None)
                        return_date_str = return_timestamp.strftime("%Y-%m-%d %H:%M")
                    elif return_date:
                        try:
                            # Parse the return date
                            if isinstance(return_date, str):
                                if ' ' in return_date:  # Format: YYYY-MM-DD HH:MM:SS
                                    return_timestamp = datetime.datetime.strptime(return_date, "%Y-%m-%d %H:%M:%S")
                                else:  # Format: YYYY-MM-DD
                                    return_timestamp = datetime.datetime.strptime(return_date, "%Y-%m-%d")
                                return_date_str = return_timestamp.strftime("%Y-%m-%d %H:%M")
                            else:
                                return_date_str = return_date.strftime("%Y-%m-%d %H:%M") if return_date else date_str
                        except Exception as e:
                            print(f"Error parsing return date: {e}")
                            return_date_str = date_str
                            return_timestamp = timestamp
                    else:
                        return_date_str = date_str
                        return_timestamp = timestamp
                        
                    # Add a separate activity for the return
                    all_activities.append({
                        'timestamp': return_timestamp,
                        'date_str': return_date_str,
                        'type': 'Library',
                        'details': f"Returned '{book_title}'"
                    })
            
            # Get bus activity - without using order_by in Firestore
            bus_ref = self.db.collection('bus_activity')
            bus_query = bus_ref.where(filter=firestore.FieldFilter('student_id', '==', student_id))
            bus_activity = list(bus_query.get())
            
            for bus in bus_activity:
                bus_data = bus.to_dict()
                timestamp = bus_data.get('timestamp')
                if not timestamp:
                    continue
                
                date_str = timestamp.strftime("%Y-%m-%d %H:%M") if timestamp else "N/A"
                
                action = bus_data.get('action', 'unknown')
                route_num = bus_data.get('route_num', 'Unknown')
                
                all_activities.append({
                    'timestamp': timestamp,
                    'date_str': date_str,
                    'type': 'Transport',
                    'details': f"{action} on route {route_num}"
                })
            
            # Sort all activities by timestamp (newest first)
            # First normalize all timestamps to naive datetimes to avoid comparison errors
            for activity in all_activities:
                timestamp = activity['timestamp']
                if timestamp and hasattr(timestamp, 'tzinfo') and timestamp.tzinfo is not None:
                    # Convert timezone-aware datetime to naive
                    activity['timestamp'] = timestamp.replace(tzinfo=None)
            
            all_activities.sort(key=lambda x: x['timestamp'] if x['timestamp'] else datetime.datetime.min, reverse=True)
            
            # Display in treeview (limit to 10)
            for i, activity in enumerate(all_activities[:10]):
                tree.insert("", tk.END, values=(
                    activity['date_str'],
                    activity['type'],
                    activity['details']
                ))
                
        except Exception as e:
            print(f"Error loading recent activity: {e}")
            tree.insert("", tk.END, values=("Error", "Error", f"Failed to load activities: {str(e)}")) 