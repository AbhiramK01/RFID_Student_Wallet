import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import validate_rfid, validate_pin, get_student_by_rfid, get_similar_books
import datetime
from google.cloud import firestore
import csv

class LibraryUI:
    def __init__(self, root, db, return_callback):
        self.root = root
        self.db = db
        self.return_callback = return_callback
        
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.title("Library Interface - RFID Student Wallet Application")
        
        # Show main library UI
        self.show_library_menu()
    
    def show_library_menu(self):
        """Show the main library menu"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        library_frame = ttk.Frame(self.root, padding=20)
        library_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(library_frame, text="Library Management", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Library functions
        lend_btn = ttk.Button(library_frame, text="Lend Book", 
                             command=self.show_lend_ui)
        lend_btn.pack(fill=tk.X, pady=5)
        
        return_btn = ttk.Button(library_frame, text="Return Book", 
                               command=self.show_return_ui)
        return_btn.pack(fill=tk.X, pady=5)
        
        check_btn = ttk.Button(library_frame, text="Check Books Lent", 
                              command=self.show_check_books_ui)
        check_btn.pack(fill=tk.X, pady=5)
        
        manage_btn = ttk.Button(library_frame, text="Manage Books", 
                               command=self.show_manage_books_ui)
        manage_btn.pack(fill=tk.X, pady=5)
        
        # Back button
        back_btn = ttk.Button(library_frame, text="Back to Main Menu", 
                             command=self.return_callback)
        back_btn.pack(fill=tk.X, pady=(20, 0))
    
    def show_lend_ui(self):
        """Show interface to lend a book"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        lend_frame = ttk.Frame(self.root, padding=20)
        lend_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(lend_frame, text="Lend Book", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Book ID input
        book_frame = ttk.Frame(lend_frame)
        book_frame.pack(fill=tk.X, pady=10)
        
        book_label = ttk.Label(book_frame, text="Book ID:")
        book_label.pack(side=tk.LEFT, padx=5)
        
        self.book_id_entry = ttk.Entry(book_frame, width=15)
        self.book_id_entry.pack(side=tk.LEFT, padx=5)
        self.book_id_entry.focus()
        
        find_book_btn = ttk.Button(book_frame, text="Find Book", 
                                  command=self.find_book_to_lend)
        find_book_btn.pack(side=tk.LEFT, padx=5)
        
        # Book info display (will be populated after search)
        self.book_info_frame = ttk.Frame(lend_frame)
        self.book_info_frame.pack(fill=tk.X, pady=10)
        
        # Student RFID input
        student_frame = ttk.Frame(lend_frame)
        student_frame.pack(fill=tk.X, pady=10)
        
        student_label = ttk.Label(student_frame, text="Student RFID:")
        student_label.pack(side=tk.LEFT, padx=5)
        
        self.student_rfid_entry = ttk.Entry(student_frame, width=15)
        self.student_rfid_entry.pack(side=tk.LEFT, padx=5)
        
        find_student_btn = ttk.Button(student_frame, text="Find Student", 
                                     command=self.find_student_to_lend)
        find_student_btn.pack(side=tk.LEFT, padx=5)
        
        # Student info display (will be populated after search)
        self.student_info_frame = ttk.Frame(lend_frame)
        self.student_info_frame.pack(fill=tk.X, pady=10)
        
        # Process button (initially disabled)
        self.process_lend_btn = ttk.Button(lend_frame, text="Process Lending", 
                                         command=self.process_lending, state=tk.DISABLED)
        self.process_lend_btn.pack(pady=10)
        
        # Back button
        back_btn = ttk.Button(lend_frame, text="Back", 
                             command=self.show_library_menu)
        back_btn.pack(pady=(20, 0))
        
        # Store book and student data
        self.book_data = None
        self.student_data = None
    
    def find_book_to_lend(self):
        """Find a book by ID for lending"""
        book_id = self.book_id_entry.get().strip()
        
        if not book_id:
            messagebox.showerror("Invalid Input", "Please enter a Book ID.")
            return
        
        # Clear previous info
        for widget in self.book_info_frame.winfo_children():
            widget.destroy()
        
        try:
            # Fetch book by book_id field
            book_query = self.db.collection('books').where(
                filter=firestore.FieldFilter('book_id', '==', book_id)
            ).limit(1)
            books = book_query.get()
            
            if not books or len(books) == 0:
                error_label = ttk.Label(self.book_info_frame, text=f"No book found with ID {book_id}.", foreground="red")
                error_label.pack(anchor=tk.W, pady=5)
                self.book_data = None
                self.check_can_process()
                return
            
            # Get book data
            book_doc = books[0]
            self.book_data = book_doc.to_dict()
            self.book_data['id'] = book_doc.id  # Store document ID for reference
            self.book_data['book_id'] = book_id  # Ensure book_id is saved
            
            # Check if already lent
            if self.book_data.get('status') == 'lent':
                lent_date = self.book_data.get('lent_date', 'Unknown')
                due_date = self.book_data.get('due_date', 'Unknown')
                student_id = self.book_data.get('lent_to', 'Unknown')
                
                error_label = ttk.Label(self.book_info_frame, 
                                     text=f"This book is already lent to student ID {student_id}.\nLent on: {lent_date}, Due: {due_date}", 
                                     foreground="red")
                error_label.pack(anchor=tk.W, pady=5)
                self.book_data = None
                self.check_can_process()
                return
            
            # Display book info
            info_text = f"Title: {self.book_data.get('title', 'Unknown')}\n"
            info_text += f"Author: {self.book_data.get('author', 'Unknown')}\n"
            info_text += f"Category: {self.book_data.get('category', 'Unknown')}\n"
            info_text += f"Status: {self.book_data.get('status', 'Unknown')}"
            
            info_label = ttk.Label(self.book_info_frame, text=info_text)
            info_label.pack(anchor=tk.W, pady=5)
            
            # Check if we can proceed
            self.check_can_process()
            
        except Exception as e:
            error_label = ttk.Label(self.book_info_frame, text=f"Error fetching book: {e}", foreground="red")
            error_label.pack(anchor=tk.W, pady=5)
            self.book_data = None
            self.check_can_process()
    
    def find_student_to_lend(self):
        """Find a student by RFID for lending"""
        rfid = self.student_rfid_entry.get().strip()
        
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
            self.student_data = None
            self.check_can_process()
            return
        
        # Store student data
        self.student_data = student
        
        # Display student info
        info_text = f"Name: {student.get('name', 'Unknown')}\n"
        info_text += f"Department: {student.get('department', 'Unknown')}\n"
        info_text += f"Year: {student.get('year', 'Unknown')}, Section: {student.get('section', 'Unknown')}"
        
        info_label = ttk.Label(self.student_info_frame, text=info_text)
        info_label.pack(anchor=tk.W, pady=5)
        
        # Check number of books already borrowed
        try:
            records_ref = self.db.collection('library_records')
            query = records_ref.where(
                filter=firestore.FieldFilter('student_id', '==', student['id'])
            ).where(
                filter=firestore.FieldFilter('status', '==', 'lent')
            )
            
            results = query.get()
            borrowed_count = len(results)
            
            if borrowed_count >= 3:  # Maximum 3 books allowed at a time
                warning_label = ttk.Label(self.student_info_frame, 
                                       text=f"Warning: Student already has {borrowed_count} books borrowed.", 
                                       foreground="orange")
                warning_label.pack(anchor=tk.W, pady=5)
        except Exception as e:
            print(f"Error checking borrowed books: {e}")
        
        # Check if we can proceed
        self.check_can_process()
    
    def check_can_process(self):
        """Check if both book and student are valid for lending"""
        if self.book_data and self.student_data:
            self.process_lend_btn.config(state=tk.NORMAL)
        else:
            self.process_lend_btn.config(state=tk.DISABLED)
    
    def process_lending(self):
        """Process book lending"""
        if not self.book_data or not self.student_data:
            return
        
        try:
            # Set lending dates
            now = datetime.datetime.now()
            lent_date = now.strftime("%Y-%m-%d")
            
            # Set due date (14 days from now)
            due_date = (now + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
            
            # Get document reference using the stored document ID
            book_ref = self.db.collection('books').document(self.book_data['id'])
            book_ref.update({
                'status': 'lent',
                'lent_to': self.student_data['id'],
                'lent_date': lent_date,
                'due_date': due_date,
                'available': False  # Set available to False when lending
            })
            
            # Create lending record
            record_data = {
                'book_id': self.book_data.get('book_id'),  # Use book_id field
                'book_title': self.book_data.get('title', 'Unknown'),
                'student_id': self.student_data['id'],
                'student_name': self.student_data.get('name', 'Unknown'),
                'student_rfid': self.student_data.get('rfid', 'Unknown'),
                'lent_date': lent_date,
                'due_date': due_date,
                'status': 'lent',
                'timestamp': now
            }
            
            self.db.collection('library_records').add(record_data)
            
            # Show success message
            messagebox.showinfo("Success", 
                              f"Book '{self.book_data.get('title')}' successfully lent to {self.student_data.get('name')}.\nDue date: {due_date}")
            
            # Get book recommendations
            similar_books = get_similar_books(self.db, self.book_data.get('book_id'))
            
            if similar_books:
                recommendation_text = "Reader recommendations:\n"
                for book in similar_books:
                    recommendation_text += f"• {book.get('title')} by {book.get('author')}\n"
                
                messagebox.showinfo("Book Recommendations", recommendation_text)
            
            # Return to library menu
            self.show_library_menu()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process lending: {e}")
    
    def show_return_ui(self):
        """Show interface to return a book"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        return_frame = ttk.Frame(self.root, padding=20)
        return_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(return_frame, text="Return Book", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Book ID input
        book_frame = ttk.Frame(return_frame)
        book_frame.pack(fill=tk.X, pady=10)
        
        book_label = ttk.Label(book_frame, text="Book ID:")
        book_label.pack(side=tk.LEFT, padx=5)
        
        self.return_book_entry = ttk.Entry(book_frame, width=15)
        self.return_book_entry.pack(side=tk.LEFT, padx=5)
        self.return_book_entry.focus()
        
        find_book_btn = ttk.Button(book_frame, text="Find Book", 
                                  command=self.find_book_to_return)
        find_book_btn.pack(side=tk.LEFT, padx=5)
        
        # Book info display (will be populated after search)
        self.return_info_frame = ttk.Frame(return_frame)
        self.return_info_frame.pack(fill=tk.X, pady=10)
        
        # Process button (initially disabled)
        self.process_return_btn = ttk.Button(return_frame, text="Process Return", 
                                           command=self.process_return, state=tk.DISABLED)
        self.process_return_btn.pack(pady=10)
        
        # Back button
        back_btn = ttk.Button(return_frame, text="Back", 
                             command=self.show_library_menu)
        back_btn.pack(pady=(20, 0))
        
        # Store book data
        self.return_book_data = None
    
    def find_book_to_return(self):
        """Find a book by ID for returning"""
        book_id = self.return_book_entry.get().strip()
        
        if not book_id:
            messagebox.showerror("Invalid Input", "Please enter a Book ID.")
            return
        
        # Clear previous info
        for widget in self.return_info_frame.winfo_children():
            widget.destroy()
        
        try:
            # Fetch book by book_id field
            book_query = self.db.collection('books').where(
                filter=firestore.FieldFilter('book_id', '==', book_id)
            ).limit(1)
            books = book_query.get()
            
            if not books or len(books) == 0:
                error_label = ttk.Label(self.return_info_frame, text=f"No book found with ID {book_id}.", foreground="red")
                error_label.pack(anchor=tk.W, pady=5)
                self.return_book_data = None
                self.process_return_btn.config(state=tk.DISABLED)
                return
            
            # Get book data
            book_doc = books[0]
            self.return_book_data = book_doc.to_dict()
            self.return_book_data['id'] = book_doc.id  # Store document ID for reference
            self.return_book_data['book_id'] = book_id  # Ensure book_id is saved
            
            # Check if actually lent
            if self.return_book_data.get('status') != 'lent':
                error_label = ttk.Label(self.return_info_frame, 
                                     text=f"This book is not currently lent out. Current status: {self.return_book_data.get('status', 'unknown')}", 
                                     foreground="red")
                error_label.pack(anchor=tk.W, pady=5)
                self.return_book_data = None
                self.process_return_btn.config(state=tk.DISABLED)
                return
            
            # Get student info
            student_id = self.return_book_data.get('lent_to')
            student_ref = self.db.collection('students').document(student_id)
            student = student_ref.get()
            
            if student.exists:
                student_data = student.to_dict()
                student_name = student_data.get('name', 'Unknown')
            else:
                student_name = "Unknown"
            
            # Display book info
            info_text = f"Title: {self.return_book_data.get('title', 'Unknown')}\n"
            info_text += f"Author: {self.return_book_data.get('author', 'Unknown')}\n"
            info_text += f"Lent to: {student_name}\n"
            info_text += f"Lent date: {self.return_book_data.get('lent_date', 'Unknown')}\n"
            info_text += f"Due date: {self.return_book_data.get('due_date', 'Unknown')}"
            
            info_label = ttk.Label(self.return_info_frame, text=info_text)
            info_label.pack(anchor=tk.W, pady=5)
            
            # Check if overdue
            try:
                due_date = datetime.datetime.strptime(self.return_book_data.get('due_date', ''), "%Y-%m-%d")
                today = datetime.datetime.now()
                
                if today > due_date:
                    days_late = (today - due_date).days
                    late_label = ttk.Label(self.return_info_frame, 
                                        text=f"OVERDUE by {days_late} days!", 
                                        foreground="red", font=('Arial', 12, 'bold'))
                    late_label.pack(anchor=tk.W, pady=5)
            except Exception as e:
                print(f"Error checking due date: {e}")
            
            # Enable return button
            self.process_return_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            error_label = ttk.Label(self.return_info_frame, text=f"Error fetching book: {e}", foreground="red")
            error_label.pack(anchor=tk.W, pady=5)
            self.return_book_data = None
            self.process_return_btn.config(state=tk.DISABLED)
    
    def process_return(self):
        """Process book return"""
        if not self.return_book_data:
            return
        
        try:
            # Update book status using document ID
            book_ref = self.db.collection('books').document(self.return_book_data['id'])
            book_ref.update({
                'status': 'available',
                'lent_to': None,
                'lent_date': None,
                'due_date': None,
                'available': True  # Set available to True when returning
            })
            
            # Find the lending record
            records_ref = self.db.collection('library_records')
            query = records_ref.where(
                filter=firestore.FieldFilter('book_id', '==', self.return_book_data.get('book_id'))
            ).where(
                filter=firestore.FieldFilter('status', '==', 'lent')
            )
            
            results = query.get()
            
            # Get current time with hour, minute, second
            now = datetime.datetime.now()
            return_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
            
            # Update status of original lending record but keep it for history
            for doc in results:
                lent_record = doc.to_dict()
                doc.reference.update({
                    'status': 'returned',
                    'return_date': return_date_time,
                    'return_timestamp': now
                })
                
                # Create a new separate record for the return action
                return_record = {
                    'book_id': self.return_book_data.get('book_id'),
                    'book_title': self.return_book_data.get('title', 'Unknown'),
                    'student_id': lent_record.get('student_id'),
                    'student_name': lent_record.get('student_name', 'Unknown'),
                    'student_rfid': lent_record.get('student_rfid', 'Unknown'),
                    'original_lent_date': lent_record.get('lent_date'),
                    'return_date': return_date_time,
                    'status': 'return_record',  # New status to identify return records
                    'timestamp': now,
                    'action_type': 'return'  # Explicitly mark the action type
                }
                
                # Add the return record as a separate document
                self.db.collection('library_records').add(return_record)
            
            # Show success message
            messagebox.showinfo("Success", f"Book '{self.return_book_data.get('title')}' successfully returned.")
            
            # Return to library menu
            self.show_library_menu()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process return: {e}")
    
    def show_check_books_ui(self):
        """Show interface to check books lent to a student"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        check_frame = ttk.Frame(self.root, padding=20)
        check_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(check_frame, text="Check Books Lent", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Student RFID input
        rfid_frame = ttk.Frame(check_frame)
        rfid_frame.pack(fill=tk.X, pady=10)
        
        rfid_label = ttk.Label(rfid_frame, text="Student RFID:")
        rfid_label.pack(side=tk.LEFT, padx=5)
        
        self.check_rfid_entry = ttk.Entry(rfid_frame, width=15)
        self.check_rfid_entry.pack(side=tk.LEFT, padx=5)
        self.check_rfid_entry.focus()
        
        # Submit button
        rfid_submit_btn = ttk.Button(rfid_frame, text="Check Books", 
                                    command=self.check_student_books)
        rfid_submit_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to submit
        self.check_rfid_entry.bind('<Return>', lambda event: self.check_student_books())
        
        # Student info and books display
        self.books_info_frame = ttk.Frame(check_frame)
        self.books_info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Back button
        back_btn = ttk.Button(check_frame, text="Back", 
                             command=self.show_library_menu)
        back_btn.pack(pady=(20, 0))
    
    def check_student_books(self):
        """Check books lent to a student"""
        rfid = self.check_rfid_entry.get().strip()
        
        if not validate_rfid(rfid):
            messagebox.showerror("Invalid RFID", "Please enter a valid 10-digit RFID.")
            return
        
        # Clear previous info
        for widget in self.books_info_frame.winfo_children():
            widget.destroy()
        
        # Check if student exists
        student = get_student_by_rfid(self.db, rfid)
        
        if not student:
            error_label = ttk.Label(self.books_info_frame, text=f"No student found with RFID {rfid}.", foreground="red")
            error_label.pack(anchor=tk.W, pady=5)
            return
        
        # Display student info
        info_text = f"Name: {student.get('name', 'Unknown')}\n"
        info_text += f"Department: {student.get('department', 'Unknown')}\n"
        info_text += f"Year: {student.get('year', 'Unknown')}, Section: {student.get('section', 'Unknown')}"
        
        info_label = ttk.Label(self.books_info_frame, text=info_text)
        info_label.pack(anchor=tk.W, pady=5)
        
        # Fetch books lent to student
        try:
            records_ref = self.db.collection('library_records')
            query = records_ref.where(
                filter=firestore.FieldFilter('student_id', '==', student['id'])
            ).where(
                filter=firestore.FieldFilter('status', '==', 'lent')
            )
            
            results = query.get()
            
            # Display books in treeview
            if len(results) > 0:
                # Create treeview frame
                treeview_frame = ttk.Frame(self.books_info_frame)
                treeview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
                
                # Create treeview
                columns = ('book_id', 'title', 'lent_date', 'due_date', 'status')
                books_tree = ttk.Treeview(treeview_frame, columns=columns, show='headings')
                
                # Define headings
                books_tree.heading('book_id', text='Book ID')
                books_tree.heading('title', text='Book Title')
                books_tree.heading('lent_date', text='Lent Date')
                books_tree.heading('due_date', text='Due Date')
                books_tree.heading('status', text='Status')
                
                # Column widths
                books_tree.column('book_id', width=100)
                books_tree.column('title', width=200)
                books_tree.column('lent_date', width=100)
                books_tree.column('due_date', width=100)
                books_tree.column('status', width=100)
                
                # Add scrollbar
                scrollbar = ttk.Scrollbar(treeview_frame, orient=tk.VERTICAL, command=books_tree.yview)
                books_tree.configure(yscroll=scrollbar.set)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                books_tree.pack(fill=tk.BOTH, expand=True)
                
                # Add data to treeview
                today = datetime.datetime.now().date()
                
                for doc in results:
                    data = doc.to_dict()
                    
                    # Check if overdue
                    status = "On time"
                    try:
                        due_date = datetime.datetime.strptime(data.get('due_date', ''), "%Y-%m-%d").date()
                        if today > due_date:
                            days_late = (today - due_date).days
                            status = f"OVERDUE ({days_late} days)"
                    except Exception as e:
                        print(f"Error parsing due date: {e}")
                        status = "Error"
                    
                    books_tree.insert('', tk.END, values=(
                        data.get('book_id', 'Unknown'),
                        data.get('book_title', 'Unknown'),
                        data.get('lent_date', 'Unknown'),
                        data.get('due_date', 'Unknown'),
                        status
                    ))
            else:
                no_books_label = ttk.Label(self.books_info_frame, text="No books currently lent to this student.")
                no_books_label.pack(anchor=tk.W, pady=10)
                
        except Exception as e:
            error_label = ttk.Label(self.books_info_frame, text=f"Error fetching books: {e}", foreground="red")
            error_label.pack(anchor=tk.W, pady=5)
    
    def show_manage_books_ui(self):
        """Show interface to manage books"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        manage_frame = ttk.Frame(self.root, padding=20)
        manage_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(manage_frame, text="Manage Books", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Book management functions
        add_btn = ttk.Button(manage_frame, text="Add New Book", 
                            command=self.show_add_book_ui)
        add_btn.pack(fill=tk.X, pady=5)
        
        edit_btn = ttk.Button(manage_frame, text="Edit Book Details", 
                             command=self.show_edit_book_ui)
        edit_btn.pack(fill=tk.X, pady=5)
        
        list_btn = ttk.Button(manage_frame, text="List All Books", 
                             command=self.show_list_books_ui)
        list_btn.pack(fill=tk.X, pady=5)
        
        # Back button
        back_btn = ttk.Button(manage_frame, text="Back", 
                             command=self.show_library_menu)
        back_btn.pack(fill=tk.X, pady=(20, 0))
    
    def show_add_book_ui(self):
        """Show interface to add a new book"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        add_frame = ttk.Frame(self.root, padding=20)
        add_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(add_frame, text="Add New Book", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Book details form
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Book ID
        id_frame = ttk.Frame(form_frame)
        id_frame.pack(fill=tk.X, pady=5)
        ttk.Label(id_frame, text="Book ID:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
        self.book_id_entry = ttk.Entry(id_frame, width=30)
        self.book_id_entry.pack(side=tk.LEFT, padx=5)
        
        # Title
        title_frame = ttk.Frame(form_frame)
        title_frame.pack(fill=tk.X, pady=5)
        ttk.Label(title_frame, text="Title:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
        self.title_entry = ttk.Entry(title_frame, width=30)
        self.title_entry.pack(side=tk.LEFT, padx=5)
        
        # Author
        author_frame = ttk.Frame(form_frame)
        author_frame.pack(fill=tk.X, pady=5)
        ttk.Label(author_frame, text="Author:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
        self.author_entry = ttk.Entry(author_frame, width=30)
        self.author_entry.pack(side=tk.LEFT, padx=5)
        
        # Category
        category_frame = ttk.Frame(form_frame)
        category_frame.pack(fill=tk.X, pady=5)
        ttk.Label(category_frame, text="Category:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
        
        # Predefined categories
        categories = ["Fiction", "Non-Fiction", "Science", "Mathematics", "Computer Science", 
                     "Engineering", "Literature", "History", "Philosophy", "Other"]
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(category_frame, textvariable=self.category_var, values=categories, width=28)
        category_combo.pack(side=tk.LEFT, padx=5)
        
        # Publisher
        publisher_frame = ttk.Frame(form_frame)
        publisher_frame.pack(fill=tk.X, pady=5)
        ttk.Label(publisher_frame, text="Publisher:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
        self.publisher_entry = ttk.Entry(publisher_frame, width=30)
        self.publisher_entry.pack(side=tk.LEFT, padx=5)
        
        # Year
        year_frame = ttk.Frame(form_frame)
        year_frame.pack(fill=tk.X, pady=5)
        ttk.Label(year_frame, text="Year:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
        self.year_entry = ttk.Entry(year_frame, width=30)
        self.year_entry.pack(side=tk.LEFT, padx=5)
        
        # ISBN
        isbn_frame = ttk.Frame(form_frame)
        isbn_frame.pack(fill=tk.X, pady=5)
        ttk.Label(isbn_frame, text="ISBN:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
        self.isbn_entry = ttk.Entry(isbn_frame, width=30)
        self.isbn_entry.pack(side=tk.LEFT, padx=5)
        
        # Quantity
        quantity_frame = ttk.Frame(form_frame)
        quantity_frame.pack(fill=tk.X, pady=5)
        ttk.Label(quantity_frame, text="Quantity:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
        self.quantity_entry = ttk.Entry(quantity_frame, width=30)
        self.quantity_entry.pack(side=tk.LEFT, padx=5)
        self.quantity_entry.insert(0, "1")  # Default quantity
        
        # Save button
        save_btn = ttk.Button(add_frame, text="Save Book", 
                             command=self.save_new_book)
        save_btn.pack(pady=20)
        
        # Back button
        back_btn = ttk.Button(add_frame, text="Back", 
                             command=self.show_manage_books_ui)
        back_btn.pack(pady=(0, 10))
        
        # Set focus to the first field
        self.book_id_entry.focus()
    
    def save_new_book(self):
        """Save a new book to the database"""
        # Get form data
        book_id = self.book_id_entry.get().strip()
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        category = self.category_var.get().strip()
        publisher = self.publisher_entry.get().strip()
        year = self.year_entry.get().strip()
        isbn = self.isbn_entry.get().strip()
        quantity_str = self.quantity_entry.get().strip()
        
        # Basic validation
        if not all([book_id, title, author, category]):
            messagebox.showerror("Error", "Book ID, Title, Author, and Category are required!")
            return
        
        try:
            quantity = int(quantity_str) if quantity_str else 1
            if quantity < 1:
                messagebox.showerror("Invalid Quantity", "Quantity must be at least 1.")
                return
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Quantity must be a number.")
            return
        
        # Check if book ID already exists
        book_ref = self.db.collection('books').where(
            filter=firestore.FieldFilter('book_id', '==', book_id)
        ).limit(1).get()
        
        if book_ref:
            messagebox.showerror("Error", f"Book with ID {book_id} already exists!")
            return
        
        # Prepare book data
        book_data = {
            'book_id': book_id,
            'title': title,
            'author': author,
            'category': category,
            'publisher': publisher if publisher else None,
            'year': year if year else None,
            'isbn': isbn if isbn else None,
            'quantity': quantity,
            'available': True,
            'added_on': datetime.datetime.now()
        }
        
        # Save to database
        try:
            self.db.collection('books').add(book_data)
            messagebox.showinfo("Success", f"Book '{title}' added successfully!")
            self.show_manage_books_ui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add book: {e}")
    
    def show_edit_book_ui(self):
        """Show interface to edit a book"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        edit_frame = ttk.Frame(self.root, padding=20)
        edit_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(edit_frame, text="Edit Book", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Search frame for finding the book to edit
        search_frame = ttk.Frame(edit_frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Book ID:").pack(side=tk.LEFT, padx=5)
        self.edit_book_id_entry = ttk.Entry(search_frame, width=15)
        self.edit_book_id_entry.pack(side=tk.LEFT, padx=5)
        self.edit_book_id_entry.focus()
        
        search_btn = ttk.Button(search_frame, text="Find Book", 
                               command=self.find_book_to_edit)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame for book details (populated when a book is found)
        self.edit_details_frame = ttk.Frame(edit_frame)
        self.edit_details_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Back button
        back_btn = ttk.Button(edit_frame, text="Back", 
                             command=self.show_manage_books_ui)
        back_btn.pack(pady=(10, 0))
        
        # Store current book document reference for updating
        self.current_edit_book_ref = None
    
    def find_book_to_edit(self):
        """Find a book by ID for editing"""
        book_id = self.edit_book_id_entry.get().strip()
        
        if not book_id:
            messagebox.showerror("Invalid Input", "Please enter a Book ID.")
            return
        
        # Clear existing form if any
        for widget in self.edit_details_frame.winfo_children():
            widget.destroy()
        
        # Find book by ID
        try:
            book_query = self.db.collection('books').where(
                filter=firestore.FieldFilter('book_id', '==', book_id)
            ).limit(1).get()
            
            if not book_query or len(book_query) == 0:
                ttk.Label(self.edit_details_frame, text=f"No book found with ID {book_id}.", 
                        foreground="red").pack(anchor=tk.W, pady=5)
                return
            
            # Store document reference for later update
            book_doc = book_query[0]
            self.current_edit_book_ref = book_doc.reference
            book_data = book_doc.to_dict()
            
            # Display and allow editing of book details
            form_frame = ttk.Frame(self.edit_details_frame)
            form_frame.pack(fill=tk.X, pady=10)
            
            # Book ID (readonly)
            id_frame = ttk.Frame(form_frame)
            id_frame.pack(fill=tk.X, pady=5)
            ttk.Label(id_frame, text="Book ID:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
            book_id_var = tk.StringVar(value=book_data.get('book_id', ''))
            book_id_entry = ttk.Entry(id_frame, width=30, textvariable=book_id_var, state='readonly')
            book_id_entry.pack(side=tk.LEFT, padx=5)
            
            # Title
            title_frame = ttk.Frame(form_frame)
            title_frame.pack(fill=tk.X, pady=5)
            ttk.Label(title_frame, text="Title:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
            self.edit_title_var = tk.StringVar(value=book_data.get('title', ''))
            title_entry = ttk.Entry(title_frame, width=30, textvariable=self.edit_title_var)
            title_entry.pack(side=tk.LEFT, padx=5)
            
            # Author
            author_frame = ttk.Frame(form_frame)
            author_frame.pack(fill=tk.X, pady=5)
            ttk.Label(author_frame, text="Author:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
            self.edit_author_var = tk.StringVar(value=book_data.get('author', ''))
            author_entry = ttk.Entry(author_frame, width=30, textvariable=self.edit_author_var)
            author_entry.pack(side=tk.LEFT, padx=5)
            
            # Category
            category_frame = ttk.Frame(form_frame)
            category_frame.pack(fill=tk.X, pady=5)
            ttk.Label(category_frame, text="Category:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
            
            # Predefined categories
            categories = ["Fiction", "Non-Fiction", "Science", "Mathematics", "Computer Science", 
                         "Engineering", "Literature", "History", "Philosophy", "Other"]
            self.edit_category_var = tk.StringVar(value=book_data.get('category', ''))
            category_combo = ttk.Combobox(category_frame, textvariable=self.edit_category_var, 
                                        values=categories, width=28)
            category_combo.pack(side=tk.LEFT, padx=5)
            
            # Publisher
            publisher_frame = ttk.Frame(form_frame)
            publisher_frame.pack(fill=tk.X, pady=5)
            ttk.Label(publisher_frame, text="Publisher:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
            self.edit_publisher_var = tk.StringVar(value=book_data.get('publisher', ''))
            publisher_entry = ttk.Entry(publisher_frame, width=30, textvariable=self.edit_publisher_var)
            publisher_entry.pack(side=tk.LEFT, padx=5)
            
            # Year
            year_frame = ttk.Frame(form_frame)
            year_frame.pack(fill=tk.X, pady=5)
            ttk.Label(year_frame, text="Year:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
            self.edit_year_var = tk.StringVar(value=book_data.get('year', ''))
            year_entry = ttk.Entry(year_frame, width=30, textvariable=self.edit_year_var)
            year_entry.pack(side=tk.LEFT, padx=5)
            
            # ISBN
            isbn_frame = ttk.Frame(form_frame)
            isbn_frame.pack(fill=tk.X, pady=5)
            ttk.Label(isbn_frame, text="ISBN:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
            self.edit_isbn_var = tk.StringVar(value=book_data.get('isbn', ''))
            isbn_entry = ttk.Entry(isbn_frame, width=30, textvariable=self.edit_isbn_var)
            isbn_entry.pack(side=tk.LEFT, padx=5)
            
            # Quantity
            quantity_frame = ttk.Frame(form_frame)
            quantity_frame.pack(fill=tk.X, pady=5)
            ttk.Label(quantity_frame, text="Quantity:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
            self.edit_quantity_var = tk.StringVar(value=str(book_data.get('quantity', 1)))
            quantity_entry = ttk.Entry(quantity_frame, width=30, textvariable=self.edit_quantity_var)
            quantity_entry.pack(side=tk.LEFT, padx=5)
            
            # Availability
            avail_frame = ttk.Frame(form_frame)
            avail_frame.pack(fill=tk.X, pady=5)
            ttk.Label(avail_frame, text="Available:").pack(side=tk.LEFT, padx=5, anchor=tk.W)
            self.edit_available_var = tk.BooleanVar(value=book_data.get('available', True))
            ttk.Checkbutton(avail_frame, variable=self.edit_available_var).pack(side=tk.LEFT, padx=5)
            
            # Update button
            update_btn = ttk.Button(self.edit_details_frame, text="Update Book", 
                                   command=self.update_book_details)
            update_btn.pack(pady=10)
            
            # Delete button
            delete_btn = ttk.Button(self.edit_details_frame, text="Delete Book", 
                                   command=self.delete_book)
            delete_btn.pack(pady=5)
            
        except Exception as e:
            ttk.Label(self.edit_details_frame, text=f"Error finding book: {e}", 
                    foreground="red").pack(anchor=tk.W, pady=5)
    
    def update_book_details(self):
        """Update book details in the database"""
        if not self.current_edit_book_ref:
            messagebox.showerror("Error", "No book selected for update.")
            return
        
        # Get form data
        title = self.edit_title_var.get().strip()
        author = self.edit_author_var.get().strip()
        category = self.edit_category_var.get().strip()
        publisher = self.edit_publisher_var.get().strip()
        year = self.edit_year_var.get().strip()
        isbn = self.edit_isbn_var.get().strip()
        quantity_str = self.edit_quantity_var.get().strip()
        available = self.edit_available_var.get()
        
        # Basic validation
        if not all([title, author, category]):
            messagebox.showerror("Error", "Title, Author, and Category are required!")
            return
        
        try:
            quantity = int(quantity_str) if quantity_str else 1
            if quantity < 1:
                messagebox.showerror("Invalid Quantity", "Quantity must be at least 1.")
                return
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Quantity must be a number.")
            return
        
        # Prepare update data
        update_data = {
            'title': title,
            'author': author,
            'category': category,
            'publisher': publisher if publisher else None,
            'year': year if year else None,
            'isbn': isbn if isbn else None,
            'quantity': quantity,
            'available': available,
            'last_updated': datetime.datetime.now()
        }
        
        # Update in database
        try:
            self.current_edit_book_ref.update(update_data)
            messagebox.showinfo("Success", f"Book '{title}' updated successfully!")
            self.show_manage_books_ui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update book: {e}")
    
    def delete_book(self):
        """Delete a book from the database"""
        if not self.current_edit_book_ref:
            messagebox.showerror("Error", "No book selected for deletion.")
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", 
                                     "Are you sure you want to delete this book?\nThis action cannot be undone.")
        if not confirm:
            return
        
        # Get book_id from entry field
        book_id = self.edit_book_id_entry.get().strip()
        
        # Check if book is currently lent
        records_ref = self.db.collection('library_records')
        query = records_ref.where(
            filter=firestore.FieldFilter('book_id', '==', book_id)
        ).where(
            filter=firestore.FieldFilter('status', '==', 'lent')
        ).limit(1)
        
        results = list(query.get())
        if results:
            messagebox.showerror("Cannot Delete", 
                               "This book is currently lent out. Please ensure all copies are returned before deletion.")
            return
        
        # Delete the book
        try:
            self.current_edit_book_ref.delete()
            messagebox.showinfo("Success", "Book deleted successfully!")
            self.show_manage_books_ui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete book: {e}")
    
    def show_list_books_ui(self):
        """Show interface to list all books"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        list_frame = ttk.Frame(self.root, padding=20)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(list_frame, text="Book Catalog", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Filters frame
        filters_frame = ttk.Frame(list_frame)
        filters_frame.pack(fill=tk.X, pady=10)
        
        # Category filter
        ttk.Label(filters_frame, text="Category:").pack(side=tk.LEFT, padx=5)
        categories = ["All Categories", "Fiction", "Non-Fiction", "Science", "Mathematics", 
                     "Computer Science", "Engineering", "Literature", "History", "Philosophy", "Other"]
        self.category_filter_var = tk.StringVar(value="All Categories")
        category_combo = ttk.Combobox(filters_frame, textvariable=self.category_filter_var, 
                                     values=categories, width=15, state="readonly")
        category_combo.pack(side=tk.LEFT, padx=5)
        
        # Availability filter
        ttk.Label(filters_frame, text="Status:").pack(side=tk.LEFT, padx=(15, 5))
        statuses = ["All", "Available", "Borrowed"]
        self.status_filter_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(filters_frame, textvariable=self.status_filter_var, 
                                   values=statuses, width=10, state="readonly")
        status_combo.pack(side=tk.LEFT, padx=5)
        
        # Search field
        ttk.Label(filters_frame, text="Search:").pack(side=tk.LEFT, padx=(15, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filters_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Apply filters button
        filter_btn = ttk.Button(filters_frame, text="Apply Filters", 
                               command=self.filter_books)
        filter_btn.pack(side=tk.LEFT, padx=15)
        
        # Reset filters button
        reset_btn = ttk.Button(filters_frame, text="Reset", 
                             command=self.reset_filters)
        reset_btn.pack(side=tk.LEFT)
        
        # Books list frame
        books_frame = ttk.Frame(list_frame)
        books_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for books
        columns = ('id', 'title', 'author', 'category', 'status', 'quantity')
        self.books_tree = ttk.Treeview(books_frame, columns=columns, show='headings')
        
        # Define headings
        self.books_tree.heading('id', text='Book ID')
        self.books_tree.heading('title', text='Title')
        self.books_tree.heading('author', text='Author')
        self.books_tree.heading('category', text='Category')
        self.books_tree.heading('status', text='Status')
        self.books_tree.heading('quantity', text='Quantity')
        
        # Column widths
        self.books_tree.column('id', width=80)
        self.books_tree.column('title', width=250)
        self.books_tree.column('author', width=150)
        self.books_tree.column('category', width=120)
        self.books_tree.column('status', width=80)
        self.books_tree.column('quantity', width=70)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(books_frame, orient=tk.VERTICAL, command=self.books_tree.yview)
        self.books_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.books_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add double-click event to view book details
        self.books_tree.bind("<Double-1>", self.view_book_details)
        
        # Actions frame
        actions_frame = ttk.Frame(list_frame)
        actions_frame.pack(fill=tk.X, pady=10)
        
        # Export button
        export_btn = ttk.Button(actions_frame, text="Export to CSV", 
                               command=self.export_books_csv)
        export_btn.pack(side=tk.LEFT, pady=10)
        
        # Print catalog button
        print_btn = ttk.Button(actions_frame, text="Print Catalog", 
                              command=self.print_catalog)
        print_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Back button
        back_btn = ttk.Button(list_frame, text="Back", 
                             command=self.show_manage_books_ui)
        back_btn.pack(side=tk.RIGHT, pady=10)
        
        # Status message
        self.status_var = tk.StringVar()
        status_label = ttk.Label(list_frame, textvariable=self.status_var)
        status_label.pack(pady=5)
        
        # Load initial books data
        self.filter_books()
    
    def reset_filters(self):
        """Reset filters to default values"""
        self.category_filter_var.set("All Categories")
        self.status_filter_var.set("All")
        self.search_var.set("")
        self.filter_books()
    
    def filter_books(self):
        """Filter books by category, availability and search term"""
        try:
            # Clear existing data
            for item in self.books_tree.get_children():
                self.books_tree.delete(item)
                
            # Get filter values
            category = self.category_filter_var.get()
            availability = self.status_filter_var.get()
            search_term = self.search_var.get().lower().strip()
            
            # Fetch books
            query = self.db.collection('books')
            
            # Apply category filter in query if needed
            if category != "All Categories":
                query = query.where(
                    filter=firestore.FieldFilter('category', '==', category)
                )
                
            # Execute query
            books = list(query.get())
            
            # Filter results in memory based on search term and availability
            filtered_books = []
            for book in books:
                book_data = book.to_dict()
                
                # Apply search filter if provided
                if search_term:
                    title = str(book_data.get('title', '')).lower()
                    author = str(book_data.get('author', '')).lower()
                    book_id = str(book_data.get('book_id', '')).lower()
                    
                    if (search_term not in title and 
                        search_term not in author and 
                        search_term not in book_id):
                        continue
                
                # Apply availability filter
                is_available = book_data.get('available', True)
                if availability == "Available" and not is_available:
                    continue
                elif availability == "Borrowed" and is_available:
                    continue
                
                filtered_books.append(book_data)
            
            # Sort books by title
            filtered_books.sort(key=lambda x: x.get('title', '').lower())
            
            # Display books in treeview
            for book in filtered_books:
                status = "Available" if book.get('available', True) else "Borrowed"
                self.books_tree.insert('', tk.END, values=(
                    book.get('book_id', ''),
                    book.get('title', ''),
                    book.get('author', ''),
                    book.get('category', ''),
                    status,
                    book.get('quantity', 1)
                ))
            
            self.status_var.set(f"Found {len(filtered_books)} books matching your criteria.")
            
        except Exception as e:
            self.status_var.set(f"Error loading books: {e}")
    
    def view_book_details(self, event):
        """View detailed information about a selected book"""
        # Get selected item
        selection = self.books_tree.selection()
        if not selection:
            return
        
        # Get book ID from selected item
        item = self.books_tree.item(selection[0])
        book_id = item['values'][0]
        
        # Find book in database
        try:
            book_query = self.db.collection('books').where(
                filter=firestore.FieldFilter('book_id', '==', book_id)
            ).limit(1).get()
            
            if not book_query or len(book_query) == 0:
                messagebox.showerror("Error", "Book not found in database.")
                return
            
            book_doc = book_query[0]
            book_data = book_doc.to_dict()
            
            # Display book details in a popup
            details = f"Book ID: {book_data.get('book_id', 'Unknown')}\n\n"
            details += f"Title: {book_data.get('title', 'Unknown')}\n\n"
            details += f"Author: {book_data.get('author', 'Unknown')}\n\n"
            details += f"Category: {book_data.get('category', 'Unknown')}\n\n"
            
            if book_data.get('publisher'):
                details += f"Publisher: {book_data.get('publisher')}\n\n"
            
            if book_data.get('year'):
                details += f"Year: {book_data.get('year')}\n\n"
            
            if book_data.get('isbn'):
                details += f"ISBN: {book_data.get('isbn')}\n\n"
            
            details += f"Quantity: {book_data.get('quantity', 1)}\n\n"
            details += f"Status: {'Available' if book_data.get('available', True) else 'Not Available'}\n\n"
            
            if not book_data.get('available', True) and book_data.get('lent_to'):
                student_id = book_data.get('lent_to')
                student_ref = self.db.collection('students').document(student_id)
                student = student_ref.get()
                
                if student.exists:
                    student_data = student.to_dict()
                    details += f"Borrowed by: {student_data.get('name', 'Unknown')}\n"
                    details += f"Lent on: {book_data.get('lent_date', 'Unknown')}\n"
                    details += f"Due on: {book_data.get('due_date', 'Unknown')}\n"
            
            # Show in messagebox
            messagebox.showinfo(f"Book Details: {book_data.get('title', 'Unknown')}", details)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load book details: {e}")
    
    def export_books_csv(self):
        """Export books to CSV file"""
        try:
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Books List"
            )
            
            if not filename:
                return  # User canceled
            
            # Get books data
            books = self.db.collection('books').get()
            
            # Write to CSV
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Book ID', 'Title', 'Author', 'Category', 'Publisher', 
                               'Year', 'ISBN', 'Quantity', 'Status'])
                
                # Write data
                for book in books:
                    data = book.to_dict()
                    status = "Available" if data.get('available', True) else "Borrowed"
                    
                    writer.writerow([
                        data.get('book_id', ''),
                        data.get('title', ''),
                        data.get('author', ''),
                        data.get('category', ''),
                        data.get('publisher', ''),
                        data.get('year', ''),
                        data.get('isbn', ''),
                        data.get('quantity', 1),
                        status
                    ])
            
            # Success message
            messagebox.showinfo("Export Successful", f"Book catalog exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export books: {e}")
    
    def print_catalog(self):
        """Generate a printable catalog"""
        try:
            from datetime import datetime
            
            # Create a formatted string for printing
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            catalog = f"LIBRARY CATALOG\nGenerated: {timestamp}\n\n"
            
            # Group books by category
            categories = {}
            
            for item in self.books_tree.get_children():
                values = self.books_tree.item(item, 'values')
                book_id, title, author, category, status, quantity = values
                
                if category not in categories:
                    categories[category] = []
                
                categories[category].append({
                    'id': book_id,
                    'title': title,
                    'author': author,
                    'status': status,
                    'quantity': quantity
                })
            
            # Generate catalog content
            for category in sorted(categories.keys()):
                catalog += f"\n{category.upper()}\n"
                catalog += "-" * 80 + "\n"
                catalog += f"{'ID':<10} {'Title':<40} {'Author':<25} {'Status':<10} {'Qty'}\n"
                catalog += "-" * 80 + "\n"
                
                for book in sorted(categories[category], key=lambda x: x['title']):
                    catalog += f"{book['id']:<10} {book['title'][:38]:<40} {book['author'][:23]:<25} {book['status']:<10} {book['quantity']}\n"
            
            # Print preview (just show in messagebox for now)
            # In a real application, this would interface with the system's print dialog
            # or generate a PDF for printing
            messagebox.showinfo("Print Preview", "Print preview would show here.")
            
            # Option to save as text file
            confirm = messagebox.askyesno("Save Catalog", "Would you like to save the catalog as a text file?")
            if confirm:
                filename = f"library_catalog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w') as f:
                    f.write(catalog)
                messagebox.showinfo("Success", f"Catalog saved to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate catalog: {e}") 