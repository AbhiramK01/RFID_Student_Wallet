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
            
        # Create a parent frame for both the scrollable area and the back button
        parent_frame = ttk.Frame(self.main_frame)
        parent_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a separate frame for the back button at the bottom
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # Add the back button to the bottom frame (this will always be visible)
        back_btn = ttk.Button(button_frame, text="Back", command=self.show_student_menu)
        back_btn.pack(pady=5)
        
        # Create a canvas with scrollbar for scrollable content
        canvas = tk.Canvas(parent_frame)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure the canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Bind mouse wheel events for scrolling - with proper cleanup
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mouse_wheel():
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mouse_wheel():
            canvas.unbind_all("<MouseWheel>")
        
        # Bind the mousewheel when entering the canvas, unbind when leaving
        canvas.bind("<Enter>", lambda e: _bind_mouse_wheel())
        canvas.bind("<Leave>", lambda e: _unbind_mouse_wheel())
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Set minimum sizes to ensure scrolling works properly
        self.main_frame.update_idletasks()
        width = self.main_frame.winfo_width()
        height = self.main_frame.winfo_height() - 50  # Reserve space for back button
        canvas.config(width=width-20, height=height)
        
        # Pack the scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Create a frame for student information
        info_frame = ttk.Frame(scrollable_frame)
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
        tree_scrollbar = ttk.Scrollbar(activity_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Pack the treeview and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Fetch and display recent activity
        self.load_recent_activity(tree, student['id'])
    
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
            # Track books by their ID to avoid duplicates
            books_by_id = {}
            returned_books = set()
            
            # First, get all return records to know which books have been returned
            library_records_ref = self.db.collection('library_records')
            returns_query = library_records_ref.where(
                filter=firestore.FieldFilter('student_id', '==', student_id)
            ).where(
                filter=firestore.FieldFilter('status', 'in', ['returned', 'return_record'])
            )
            
            for doc in returns_query.get():
                data = doc.to_dict()
                book_id = data.get('book_id')
                if book_id:
                    returned_books.add(book_id)
            
            # Now get all lending records
            lending_query = library_records_ref.where(
                filter=firestore.FieldFilter('student_id', '==', student_id)
            ).where(
                filter=firestore.FieldFilter('status', '==', 'lent')
            )
            
            for doc in lending_query.get():
                data = doc.to_dict()
                book_id = data.get('book_id')
                
                # Only add books that haven't been returned
                if book_id and book_id not in returned_books:
                    books_by_id[book_id] = {
                    'title': data.get('book_title', 'Unknown Book'),
                    'due_date': data.get('due_date'),
                        'book_id': book_id
                    }
            
            # Convert to list for display
            borrowed_books = list(books_by_id.values())
            
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
            import traceback
            traceback.print_exc()
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
        """Load recent activity for the student"""
        try:
            # Show a loading indicator
            tree.insert("", tk.END, values=("Loading...", "", "Please wait, loading activities..."))
            self.root.update_idletasks()
            self.root.config(cursor="wait")
            
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)
            
            # Collect all activities
            activity_list = []
            
            # Track already processed activities to avoid duplicates
            processed_activities = {}  # key = book_id + timestamp, value = True
            
            # Add specific fetching for library records to guarantee we get both borrowed and returned books
            try:
                # First fetch actual return records from returns collection 
                # to prioritize these over library_records that were updated
                returns_query = self.db.collection('returns').where(
                    filter=firestore.FieldFilter('student_id', '==', student_id)
                ).limit(15)
                
                for doc in returns_query.get():
                    data = doc.to_dict()
                    timestamp = data.get('return_timestamp')
                    book_id = data.get('book_id')
                    
                    if timestamp and book_id:
                        # Format as a return activity
                        book_title = data.get('book_title', 'Unknown book')
                        
                        # Create a unique key for this activity
                        activity_key = f"{book_id}_{timestamp.strftime('%Y%m%d%H%M%S')}_return"
                        processed_activities[activity_key] = True
                        
                        activity_list.append({
                            'date': timestamp,
                            'type': 'Library',
                            'details': f"Returned: {book_title}",
                            'raw_timestamp': timestamp,
                            'book_id': book_id,
                            'is_return': True
                        })
                
                # Then fetch original lending records - ALWAYS show these for borrowing activity
                # even if the book has been returned
                lendings_query = self.db.collection('lendings').where(
                    filter=firestore.FieldFilter('student_id', '==', student_id)
                ).limit(15)
                
                for doc in lendings_query.get():
                    data = doc.to_dict()
                    timestamp = data.get('timestamp')
                    book_id = data.get('book_id')
                    
                    if timestamp and book_id:
                        # Format as a borrow activity regardless of status
                        book_title = data.get('book_title', 'Unknown book')
                        due_date = data.get('due_date', 'Unknown')
                        
                        # Create a unique key for this activity
                        activity_key = f"{book_id}_{timestamp.strftime('%Y%m%d%H%M%S')}_borrow"
                        
                        # Only add if not already processed
                        if activity_key not in processed_activities:
                            processed_activities[activity_key] = True
                            
                            activity_list.append({
                                'date': timestamp,
                                'type': 'Library',
                                'details': f"Borrowed: {book_title} - Due: {due_date}",
                                'raw_timestamp': timestamp,
                                'book_id': book_id,
                                'is_return': False
                            })
                
                # Finally fetch from library_records as backup, but be careful about duplicates
                library_query = self.db.collection('library_records').where(
                    filter=firestore.FieldFilter('student_id', '==', student_id)
                ).limit(20)
                
                for doc in library_query.get():
                    data = doc.to_dict()
                    timestamp = data.get('timestamp')
                    return_timestamp = data.get('return_timestamp')
                    book_id = data.get('book_id')
                    status = data.get('status')
                    is_return_record = status == 'return_record' or 'return_record' in data.get('activity_type', '')
                    
                    # Skip records that are simply updates of lending records
                    # (these cause the duplicate "Returned" entries with the same timestamp)
                    if status == 'returned' and not is_return_record and timestamp and not return_timestamp:
                        continue
                        
                    if book_id:
                        # For return records, use return_timestamp if available
                        if (status == 'returned' or is_return_record) and return_timestamp:
                            actual_timestamp = return_timestamp
                            is_return = True
                            details_prefix = "Returned: "
                            activity_type = "return"
                        else:
                            # Always show the borrow activity regardless of whether the book was returned
                            if not timestamp:
                                continue  # Skip records without timestamp
                            actual_timestamp = timestamp
                            is_return = False
                            details_prefix = "Borrowed: "
                            activity_type = "borrow"
                            
                        book_title = data.get('book_title', 'Unknown book')
                        
                        # Create unique activity key based on book_id and timestamp
                        activity_key = f"{book_id}_{actual_timestamp.strftime('%Y%m%d%H%M%S')}_{activity_type}"
                        
                        # Only add if we haven't processed this activity yet
                        if activity_key not in processed_activities:
                            processed_activities[activity_key] = True
                            
                            if is_return:
                                details = f"{details_prefix}{book_title}"
                            else:
                                due_date = data.get('due_date', 'Unknown')
                                details = f"{details_prefix}{book_title} - Due: {due_date}"
                            
                            activity_list.append({
                                'date': actual_timestamp,
                                'type': 'Library',
                                'details': details,
                                'raw_timestamp': actual_timestamp,
                                'book_id': book_id,
                                'is_return': is_return
                            })
            except Exception as e:
                print(f"Error fetching library records: {e}")
                import traceback
                traceback.print_exc()
            
            # Add other activity types
            activity_sources = [
                {
                    'collection': 'transactions',
                    'student_field': 'student_id',
                    'timestamp_field': 'timestamp',
                    'limit': 10,
                    'type_name': 'Wallet',
                    'format_func': self._format_wallet_activity
                },
                {
                    'collection': 'bus_logs',
                    'student_field': 'student_id',
                    'timestamp_field': 'timestamp',
                    'limit': 10,
                    'type_name': 'Bus',
                    'format_func': self._format_bus_activity
                },
                {
                    'collection': 'attendance',
                    'student_field': 'student_id',
                    'timestamp_field': 'timestamp',
                    'limit': 10,
                    'type_name': 'Attendance',
                    'format_func': self._format_attendance_activity
                }
            ]
            
            # Process each activity source
            for source in activity_sources:
                try:
                    # Create query with limit for better performance
                    query = self.db.collection(source['collection']).where(
                        filter=firestore.FieldFilter(source['student_field'], '==', student_id)
                    ).limit(source['limit'])
                    
                    # Process results
                    for doc in query.get():
                        data = doc.to_dict()
                        timestamp = data.get(source['timestamp_field'])
                        
                        if timestamp:
                            # Format the activity details
                            details = source['format_func'](data)
                            if details:  # Skip if formatter returns None
                                activity_list.append({
                                    'date': timestamp,
                                    'type': source['type_name'],
                                    'details': details,
                                    'raw_timestamp': timestamp  # For sorting
                                })
                except Exception as e:
                    print(f"Error fetching {source['collection']}: {e}")
                    continue  # Skip to next activity source
                
            # Sort by timestamp (most recent first)
            activity_list.sort(key=lambda x: x['raw_timestamp'], reverse=True)
            
            # Limit to 20 most recent activities across all categories for better performance
            activity_list = activity_list[:20]
            
            # Add to treeview
            for activity in activity_list:
                date_str = activity['date'].strftime("%Y-%m-%d %H:%M:%S")
                tree.insert("", tk.END, values=(date_str, activity['type'], activity['details']))
            
            # If no activities found, show message
            if not activity_list:
                tree.insert("", tk.END, values=("N/A", "N/A", "No recent activity found."))
                
            # Reset cursor
            self.root.config(cursor="")
                
        except Exception as e:
            # Reset cursor
            self.root.config(cursor="")
            
            print(f"Error loading recent activity: {e}")
            import traceback
            traceback.print_exc()
            tree.insert("", tk.END, values=("Error", "Error", f"Failed to load activities: {str(e)}"))

    def _format_library_activity(self, data):
        """Format library activity for display"""
        status = data.get('status')
        book_title = data.get('book_title', 'Unknown book')
        due_date = data.get('due_date', 'Unknown')
        is_return_record = 'return_record' in data.get('activity_type', '')
        
        # Always show lending records regardless of status
        if status == 'lent' or status == 'borrowed':
            return f"Borrowed: {book_title} - Due: {due_date}"
        elif status == 'returned' or is_return_record:
            return f"Returned: {book_title}"
        
        # As a fallback, check if this is a lending record that should be displayed
        # even if it doesn't have the expected status
        if 'lent_date' in data and not is_return_record:
            return f"Borrowed: {book_title} - Due: {due_date}"
        
        return f"Activity: {book_title}"

    def _format_wallet_activity(self, data):
        """Format wallet activity for display"""
        return f"{data.get('type', 'Transaction')}: {format_currency(data.get('amount', 0))} - {data.get('description', '')}"

    def _format_bus_activity(self, data):
        """Format bus activity for display"""
        return f"{data.get('direction', 'Boarding')}: {data.get('route_name', 'Unknown route')}"

    def _format_attendance_activity(self, data):
        """Format attendance activity for display"""
        return f"{data.get('status', 'Present')} - {data.get('class_name', 'Unknown class')}"

    def show_student_menu(self):
        """Show the student menu after viewing detailed info"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Recreate the main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Show the RFID input screen
        self.show_rfid_input() 