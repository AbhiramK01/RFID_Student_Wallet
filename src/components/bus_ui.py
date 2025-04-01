import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import validate_rfid, get_student_by_rfid, send_email
import datetime
from google.cloud import firestore

class BusUI:
    def __init__(self, root, db, return_callback):
        self.root = root
        self.db = db
        self.return_callback = return_callback
        
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.title("Bus Interface - RFID Student Wallet Application")
        
        # Show bus route selection UI
        self.show_bus_route_selection()
    
    def show_bus_route_selection(self):
        """Show interface to select bus route"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        selection_frame = ttk.Frame(self.root, padding=20)
        selection_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(selection_frame, text="Bus Transport Management", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Bus route selection
        route_frame = ttk.Frame(selection_frame)
        route_frame.pack(fill=tk.X, pady=10)
        
        route_label = ttk.Label(route_frame, text="Select Bus Route:")
        route_label.pack(side=tk.LEFT, padx=5)
        
        self.route_entry = ttk.Entry(route_frame, width=10)
        self.route_entry.pack(side=tk.LEFT, padx=5)
        self.route_entry.focus()
        
        # Submit button
        submit_btn = ttk.Button(route_frame, text="Enter", 
                               command=self.process_route_selection)
        submit_btn.pack(side=tk.LEFT, padx=5)
        
        # Available routes display
        self.routes_frame = ttk.Frame(selection_frame)
        self.routes_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        routes_label = ttk.Label(self.routes_frame, text="Available Bus Routes:")
        routes_label.pack(anchor=tk.W, pady=5)
        
        # Load and display available routes
        self.load_bus_routes()
        
        # Back button
        back_btn = ttk.Button(selection_frame, text="Back to Main Menu", 
                             command=self.return_callback)
        back_btn.pack(pady=(20, 0))
    
    def load_bus_routes(self):
        """Load and display available bus routes"""
        try:
            # Create treeview for bus routes
            columns = ('route_id', 'name', 'stops')
            routes_tree = ttk.Treeview(self.routes_frame, columns=columns, show='headings')
            
            # Define headings
            routes_tree.heading('route_id', text='Route ID')
            routes_tree.heading('name', text='Route Name')
            routes_tree.heading('stops', text='Stops')
            
            # Column widths
            routes_tree.column('route_id', width=100)
            routes_tree.column('name', width=150) 
            routes_tree.column('stops', width=350)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(self.routes_frame, orient=tk.VERTICAL, command=routes_tree.yview)
            routes_tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            routes_tree.pack(fill=tk.BOTH, expand=True)
            
            # Fetch routes from database
            routes_ref = self.db.collection('bus_routes').get()
            
            for route in routes_ref:
                route_data = route.to_dict()
                route_id = route_data.get('route_id', 'Unknown')
                name = route_data.get('name', 'Unknown')
                stops = ', '.join(route_data.get('stops', []))
                
                routes_tree.insert('', tk.END, values=(route_id, name, stops))
                
        except Exception as e:
            error_label = ttk.Label(self.routes_frame, text=f"Error loading bus routes: {e}", foreground="red")
            error_label.pack(pady=5)
    
    def process_route_selection(self):
        """Process bus route selection"""
        route_id = self.route_entry.get().strip()
        
        if not route_id:
            messagebox.showerror("Invalid Input", "Please enter a bus route ID.")
            return
        
        try:
            # Check if route exists by querying for route_id field
            routes_ref = self.db.collection('bus_routes')
            query = routes_ref.where(filter=firestore.FieldFilter('route_id', '==', route_id)).limit(1)
            routes = query.get()
            
            if not routes or len(routes) == 0:
                messagebox.showerror("Invalid Route", f"Bus route with ID {route_id} does not exist.")
                return
            
            # Store route data and proceed to boarding interface
            route_doc = routes[0]
            self.route_data = route_doc.to_dict()
            
            # Make sure route_id is accessible
            self.route_data['route_id'] = route_id
            
            self.show_boarding_ui()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process route selection: {e}")
    
    def show_boarding_ui(self):
        """Show interface for student boarding/offboarding"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        boarding_frame = ttk.Frame(self.root, padding=20)
        boarding_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title and route info
        route_name = self.route_data.get('name', f"Route {self.route_data['route_id']}")
        title_label = ttk.Label(boarding_frame, text=f"Bus {route_name}", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Display stops
        stops_text = "Stops: " + ', '.join(self.route_data.get('stops', []))
        stops_label = ttk.Label(boarding_frame, text=stops_text)
        stops_label.pack(pady=(0, 20))
        
        # RFID input
        rfid_frame = ttk.Frame(boarding_frame)
        rfid_frame.pack(fill=tk.X, pady=10)
        
        rfid_label = ttk.Label(rfid_frame, text="Student RFID:")
        rfid_label.pack(side=tk.LEFT, padx=5)
        
        self.board_rfid_entry = ttk.Entry(rfid_frame, width=15)
        self.board_rfid_entry.pack(side=tk.LEFT, padx=5)
        self.board_rfid_entry.focus()
        
        # Submit button
        submit_btn = ttk.Button(rfid_frame, text="Process", 
                               command=self.process_student_rfid)
        submit_btn.pack(side=tk.LEFT, padx=5)
        
        # Student info and boarding options (will be populated after RFID scan)
        self.student_info_frame = ttk.Frame(boarding_frame)
        self.student_info_frame.pack(fill=tk.X, pady=10)
        
        # Recent activity log
        log_frame = ttk.Frame(boarding_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        log_label = ttk.Label(log_frame, text="Recent Activity:")
        log_label.pack(anchor=tk.W, pady=5)
        
        # Create treeview for activity log
        columns = ('time', 'name', 'rfid', 'action', 'stop')
        self.log_tree = ttk.Treeview(log_frame, columns=columns, show='headings')
        
        # Define headings
        self.log_tree.heading('time', text='Time')
        self.log_tree.heading('name', text='Student Name')
        self.log_tree.heading('rfid', text='RFID')
        self.log_tree.heading('action', text='Action')
        self.log_tree.heading('stop', text='Stop')
        
        # Column widths
        self.log_tree.column('time', width=100)
        self.log_tree.column('name', width=150)
        self.log_tree.column('rfid', width=100)
        self.log_tree.column('action', width=100)
        self.log_tree.column('stop', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_tree.yview)
        self.log_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load recent activity
        self.load_recent_activity()
        
        # Back button
        back_btn = ttk.Button(boarding_frame, text="Change Route", 
                             command=self.show_bus_route_selection)
        back_btn.pack(pady=(10, 0))
    
    def load_recent_activity(self):
        """Load recent bus activity for this route"""
        try:
            # Clear existing items
            for item in self.log_tree.get_children():
                self.log_tree.delete(item)
            
            # Fetch recent activity
            activity_ref = self.db.collection('bus_activity')
            query = activity_ref.where(
                filter=firestore.FieldFilter('route_num', '==', self.route_data['route_id'])
            )
            
            # Get results first, then sort them in memory (to avoid composite index requirement)
            results = list(query.get())
            # Sort results by timestamp (newest first)
            results.sort(key=lambda doc: doc.to_dict().get('timestamp') if doc.to_dict().get('timestamp') else datetime.datetime.min, reverse=True)
            # Limit to 20 results after sorting
            results = results[:20]
            
            for doc in results:
                data = doc.to_dict()
                time_str = data.get('timestamp').strftime("%H:%M:%S") if data.get('timestamp') else "Unknown"
                
                self.log_tree.insert('', tk.END, values=(
                    time_str,
                    data.get('student_name', 'Unknown'),
                    data.get('student_rfid', 'Unknown'),
                    data.get('action', 'Unknown'),
                    data.get('stop', 'Unknown')
                ))
                
        except Exception as e:
            print(f"Error loading recent activity: {e}")
    
    def process_student_rfid(self):
        """Process student RFID for bus boarding/offboarding"""
        rfid = self.board_rfid_entry.get().strip()
        
        if not validate_rfid(rfid):
            messagebox.showerror("Invalid RFID", "Please enter a valid 10-digit RFID.")
            return
        
        # Clear previous info
        for widget in self.student_info_frame.winfo_children():
            widget.destroy()
        
        # Check if student exists
        student = get_student_by_rfid(self.db, rfid)
        
        if not student:
            error_label = ttk.Label(self.student_info_frame, text=f"No student found with RFID {rfid}.", foreground="red")
            error_label.pack(anchor=tk.W, pady=5)
            return
        
        # Check if student has bus pass
        if not student.get('has_bus_pass', False):
            error_label = ttk.Label(self.student_info_frame, 
                                  text=f"Student {student.get('name')} does not have a bus pass.", 
                                  foreground="red")
            error_label.pack(anchor=tk.W, pady=5)
            return
        
        # Check if student is assigned to this route
        student_route = student.get('bus_route')
        if student_route != self.route_data['route_id']:
            error_label = ttk.Label(self.student_info_frame, 
                                  text=f"Student {student.get('name')} is assigned to route {student_route}, not route {self.route_data['route_id']}.", 
                                  foreground="red")
            error_label.pack(anchor=tk.W, pady=5)
            return
        
        # Display student info
        info_text = f"Student: {student.get('name')}\n"
        info_text += f"Department: {student.get('department')}, Year: {student.get('year')}, Section: {student.get('section')}\n"
        info_text += f"Current Status: {student.get('bus_status', 'Unknown')}"
        
        info_label = ttk.Label(self.student_info_frame, text=info_text)
        info_label.pack(anchor=tk.W, pady=5)
        
        # Create boarding options
        options_frame = ttk.Frame(self.student_info_frame)
        options_frame.pack(fill=tk.X, pady=10)
        
        # Stop selection
        stop_label = ttk.Label(options_frame, text="Select Stop:")
        stop_label.pack(side=tk.LEFT, padx=5)
        
        self.stop_var = tk.StringVar()
        stop_combo = ttk.Combobox(options_frame, textvariable=self.stop_var, values=self.route_data.get('stops', []), state="readonly")
        stop_combo.pack(side=tk.LEFT, padx=5)
        if self.route_data.get('stops'):
            stop_combo.current(0)
        
        # Action buttons
        action_frame = ttk.Frame(self.student_info_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        # Based on current status, show appropriate action buttons
        current_status = student.get('bus_status', 'outside')
        
        if current_status == 'outside':
            board_btn = ttk.Button(action_frame, text="Board Bus", 
                                  command=lambda: self.process_boarding(student))
            board_btn.pack(side=tk.LEFT, padx=5)
        elif current_status == 'inside':
            offboard_btn = ttk.Button(action_frame, text="Exit Bus", 
                                     command=lambda: self.process_offboarding(student))
            offboard_btn.pack(side=tk.LEFT, padx=5)
        else:
            # Both options if status is unknown
            board_btn = ttk.Button(action_frame, text="Board Bus", 
                                  command=lambda: self.process_boarding(student))
            board_btn.pack(side=tk.LEFT, padx=5)
            
            offboard_btn = ttk.Button(action_frame, text="Exit Bus", 
                                     command=lambda: self.process_offboarding(student))
            offboard_btn.pack(side=tk.LEFT, padx=5)
    
    def process_boarding(self, student):
        """Process student boarding the bus"""
        # Check for required fields
        selected_stop = self.stop_var.get()
        if not selected_stop:
            messagebox.showerror("Missing Information", "Please select a stop.")
            return
        
        # Check if already inside
        current_status = student.get('bus_status', 'outside')
        if current_status == 'inside':
            confirm = messagebox.askyesno("Already Boarded", 
                                        f"Student {student.get('name')} is already marked as inside the bus. Do you want to update boarding information?")
            if not confirm:
                return
        
        try:
            # Update student status
            now = datetime.datetime.now()
            
            self.db.collection('students').document(student['id']).update({
                'bus_status': 'inside',
                'last_bus_action': {
                    'action': 'board',
                    'timestamp': now,
                    'route': self.route_data['route_id'],
                    'stop': selected_stop
                }
            })
            
            # Record bus activity
            activity_data = {
                'student_id': student['id'],
                'student_name': student.get('name'),
                'student_rfid': student.get('rfid'),
                'action': 'board',
                'route_num': self.route_data['route_id'],
                'stop': selected_stop,
                'timestamp': now,
                'email_sent': False
            }
            
            activity_ref = self.db.collection('bus_activity').add(activity_data)
            
            # Send email notification
            parent_email = student.get('parent_email')
            if parent_email:
                subject = "Bus Boarding Notification"
                message = f"""
                Dear Parent/Guardian,
                
                This is to inform you that {student.get('name')} has boarded the bus (Route {self.route_data['route_id']}) at {selected_stop} at {now.strftime('%H:%M:%S')}.
                
                This is an automated message from the Student RFID System.
                """
                
                email_sent = send_email(parent_email, subject, message)
                
                # Just skip updating the email_sent status to avoid errors
                # The main functionality (boarding) has already been completed
            
            # Show success message
            messagebox.showinfo("Success", f"Student {student.get('name')} successfully boarded the bus at {selected_stop}.")
            
            # Update activity log
            self.load_recent_activity()
            
            # Clear RFID entry for next student
            self.board_rfid_entry.delete(0, tk.END)
            self.board_rfid_entry.focus()
            
            # Clear student info
            for widget in self.student_info_frame.winfo_children():
                widget.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process boarding: {e}")
    
    def process_offboarding(self, student):
        """Process student exiting the bus"""
        # Check for required fields
        selected_stop = self.stop_var.get()
        if not selected_stop:
            messagebox.showerror("Missing Information", "Please select a stop.")
            return
        
        # Check if already outside
        current_status = student.get('bus_status', 'outside')
        if current_status == 'outside':
            confirm = messagebox.askyesno("Already Offboarded", 
                                        f"Student {student.get('name')} is already marked as outside the bus. Do you want to update offboarding information?")
            if not confirm:
                return
        
        try:
            # Update student status
            now = datetime.datetime.now()
            
            self.db.collection('students').document(student['id']).update({
                'bus_status': 'outside',
                'last_bus_action': {
                    'action': 'exit',
                    'timestamp': now,
                    'route': self.route_data['route_id'],
                    'stop': selected_stop
                }
            })
            
            # Record bus activity
            activity_data = {
                'student_id': student['id'],
                'student_name': student.get('name'),
                'student_rfid': student.get('rfid'),
                'action': 'exit',
                'route_num': self.route_data['route_id'],
                'stop': selected_stop,
                'timestamp': now,
                'email_sent': False
            }
            
            activity_ref = self.db.collection('bus_activity').add(activity_data)
            
            # Send email notification
            parent_email = student.get('parent_email')
            if parent_email:
                subject = "Bus Offboarding Notification"
                message = f"""
                Dear Parent/Guardian,
                
                This is to inform you that {student.get('name')} has exited the bus (Route {self.route_data['route_id']}) at {selected_stop} at {now.strftime('%H:%M:%S')}.
                
                This is an automated message from the Student RFID System.
                """
                
                email_sent = send_email(parent_email, subject, message)
                
                # Just skip updating the email_sent status to avoid errors
                # The main functionality (offboarding) has already been completed
            
            # Show success message
            messagebox.showinfo("Success", f"Student {student.get('name')} successfully exited the bus at {selected_stop}.")
            
            # Update activity log
            self.load_recent_activity()
            
            # Clear RFID entry for next student
            self.board_rfid_entry.delete(0, tk.END)
            self.board_rfid_entry.focus()
            
            # Clear student info
            for widget in self.student_info_frame.winfo_children():
                widget.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process offboarding: {e}") 