import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os
import datetime
from firebase_admin import firestore

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import validate_rfid, read_rfid_input, get_student_by_rfid, format_currency

class CanteenUI:
    def __init__(self, root, db, go_back_callback=None):
        self.root = root
        self.db = db
        self.go_back_callback = go_back_callback
        
        # Clear the current window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.title("RFID Student Wallet - Canteen")
        
        # Create a frame for the main content
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Show the main menu
        self.show_main_menu()
    
    def show_main_menu(self):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Title
        title_label = ttk.Label(self.main_frame, text="Canteen Management", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        # Options frame
        options_frame = ttk.Frame(self.main_frame)
        options_frame.pack(pady=20)
        
        # Buttons for different operations
        ttk.Button(options_frame, text="Process Purchase", width=25, 
                  command=self.show_purchase_screen).pack(pady=5)
        ttk.Button(options_frame, text="Recharge Wallet", width=25, 
                  command=self.show_recharge_screen).pack(pady=5)
        ttk.Button(options_frame, text="Check Balance", width=25, 
                  command=self.show_balance_screen).pack(pady=5)
        
        # Back button
        if self.go_back_callback:
            ttk.Button(self.main_frame, text="Back to Main Menu", 
                      command=self.go_back_callback).pack(pady=20)
    
    def show_purchase_screen(self):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Title
        title_label = ttk.Label(self.main_frame, text="Process Purchase", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame for RFID input
        rfid_frame = ttk.Frame(self.main_frame)
        rfid_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(rfid_frame, text="Student RFID:").pack(side=tk.LEFT, padx=5)
        self.student_rfid_entry = ttk.Entry(rfid_frame, width=15)
        self.student_rfid_entry.pack(side=tk.LEFT, padx=5)
        self.student_rfid_entry.focus()
        
        # Frame for student info (will be populated after RFID is entered)
        self.student_info_frame = ttk.Frame(self.main_frame)
        self.student_info_frame.pack(pady=10, fill=tk.X)
        
        # Frame for transaction details
        self.transaction_frame = ttk.Frame(self.main_frame)
        self.transaction_frame.pack(pady=10, fill=tk.X)
        
        # Back button
        ttk.Button(self.main_frame, text="Back", 
                  command=self.show_main_menu).pack(pady=10)
        
        # Bind Enter key to the callback
        self.student_rfid_entry.bind('<Return>', lambda event: self.process_rfid_for_purchase())
        
        # Button to submit RFID
        ttk.Button(rfid_frame, text="Submit", 
                  command=self.process_rfid_for_purchase).pack(side=tk.LEFT, padx=5)
    
    def process_rfid_for_purchase(self):
        # Clear previous content in frames
        for widget in self.student_info_frame.winfo_children():
            widget.destroy()
        for widget in self.transaction_frame.winfo_children():
            widget.destroy()
            
        rfid = self.student_rfid_entry.get().strip()
        
        if not validate_rfid(rfid):
            messagebox.showerror("Invalid RFID", "Please enter a valid 10-digit RFID.")
            return
            
        # Get student details
        student = get_student_by_rfid(self.db, rfid)
        
        if not student:
            messagebox.showerror("Student Not Found", "No student found with this RFID.")
            return
            
        # Display student info
        ttk.Label(self.student_info_frame, text=f"Student: {student.get('name', 'N/A')}", 
                 font=("Helvetica", 12)).pack(anchor=tk.W, padx=5)
        ttk.Label(self.student_info_frame, text=f"Department: {student.get('department', 'N/A')} - {student.get('year', 'N/A')} Year", 
                 font=("Helvetica", 10)).pack(anchor=tk.W, padx=5)
        ttk.Label(self.student_info_frame, text=f"Current Balance: {format_currency(student.get('wallet_balance', 0))}", 
                 font=("Helvetica", 12, "bold")).pack(anchor=tk.W, padx=5)
        
        # Transaction details frame
        ttk.Label(self.transaction_frame, text="Enter Purchase Details:", 
                 font=("Helvetica", 12)).pack(anchor=tk.W, padx=5, pady=5)
        
        # Amount frame
        amount_frame = ttk.Frame(self.transaction_frame)
        amount_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(amount_frame, text="Amount (₹):").pack(side=tk.LEFT, padx=5)
        self.amount_entry = ttk.Entry(amount_frame, width=10)
        self.amount_entry.pack(side=tk.LEFT, padx=5)
        
        # Item description frame
        desc_frame = ttk.Frame(self.transaction_frame)
        desc_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(desc_frame, text="Description:").pack(side=tk.LEFT, padx=5)
        self.desc_entry = ttk.Entry(desc_frame, width=30)
        self.desc_entry.pack(side=tk.LEFT, padx=5)
        
        # Process button
        ttk.Button(self.transaction_frame, text="Process Payment", 
                  command=lambda: self.process_payment(student)).pack(pady=10)
        
        # Recent transactions
        ttk.Label(self.transaction_frame, text="Recent Transactions:", 
                 font=("Helvetica", 11)).pack(anchor=tk.W, padx=5, pady=(15,5))
        
        # Display recent transactions
        self.display_recent_transactions(self.transaction_frame, student['id'])
    
    def display_recent_transactions(self, parent_frame, student_id):
        # Create a frame for transactions
        transactions_frame = ttk.Frame(parent_frame)
        transactions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add a label for transactions
        ttk.Label(transactions_frame, text="Recent Transactions", 
                 font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
        
        # Create a treeview to display transactions
        columns = ("date", "amount", "type", "location")
        tree = ttk.Treeview(transactions_frame, columns=columns, show="headings", height=6)
        
        # Configure column headings
        tree.heading("date", text="Date")
        tree.heading("amount", text="Amount")
        tree.heading("type", text="Type")
        tree.heading("location", text="Description")
        
        # Configure column widths
        tree.column("date", width=100)
        tree.column("amount", width=80)
        tree.column("type", width=80)
        tree.column("location", width=150)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(transactions_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the treeview and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Fetch recent transactions from Firestore
        try:
            transactions_ref = self.db.collection('transactions')
            query = transactions_ref.where(
                filter=firestore.FieldFilter('student_id', '==', student_id)
            )
            
            # Get all transactions and sort them in memory (to avoid composite index requirement)
            transactions = list(query.get())
            
            # Sort transactions by timestamp (newest first)
            transactions.sort(
                key=lambda doc: doc.to_dict().get('timestamp') if doc.to_dict().get('timestamp') else datetime.datetime.min, 
                reverse=True
            )
            
            # Limit to 10 transactions
            transactions = transactions[:10]
            
            # Insert transactions into the treeview
            for tx in transactions:
                tx_data = tx.to_dict()
                timestamp = tx_data.get('timestamp')
                date_str = timestamp.strftime("%Y-%m-%d %H:%M") if timestamp else "N/A"
                amount = format_currency(tx_data.get('amount', 0))
                tx_type = tx_data.get('type', 'N/A')
                description = tx_data.get('description', 'N/A')
                
                tree.insert("", tk.END, values=(date_str, amount, tx_type, description))
                
        except Exception as e:
            print(f"Error loading recent transactions: {e}")
            error_label = ttk.Label(transactions_frame, text=f"Error loading transactions: {str(e)}", 
                                  foreground="red")
            error_label.pack(pady=10)
    
    def process_payment(self, student):
        try:
            amount_str = self.amount_entry.get().strip()
            description = self.desc_entry.get().strip()
            
            # Validate input
            if not amount_str:
                messagebox.showerror("Invalid Input", "Please enter a valid amount.")
                return
                
            try:
                amount = float(amount_str)
                if amount <= 0:
                    messagebox.showerror("Invalid Amount", "Amount must be greater than zero.")
                    return
            except ValueError:
                messagebox.showerror("Invalid Amount", "Please enter a valid number for amount.")
                return
                
            # Check if student has sufficient balance
            current_balance = student.get('wallet_balance', 0)
            if amount > current_balance:
                messagebox.showerror("Insufficient Balance", 
                                    f"Student has insufficient balance.\nCurrent Balance: {format_currency(current_balance)}\nRequired: {format_currency(amount)}")
                return
                
            # Process the transaction
            transaction = {
                'student_id': student['id'],
                'amount': amount,
                'type': 'debit',
                'description': description if description else 'Canteen Purchase',
                'location': 'Canteen',
                'timestamp': datetime.datetime.now()
            }
            
            # Update student's wallet balance
            new_balance = current_balance - amount
            
            # Perform the database operations in a transaction
            transaction_batch = self.db.batch()
            
            # Add transaction
            transaction_ref = self.db.collection('transactions').document()
            transaction_batch.set(transaction_ref, transaction)
            
            # Update student balance
            student_ref = self.db.collection('students').document(student['id'])
            transaction_batch.update(student_ref, {'wallet_balance': new_balance})
            
            # Commit the batch
            transaction_batch.commit()
            
            # Show success message
            messagebox.showinfo("Payment Successful", 
                              f"Payment of {format_currency(amount)} processed successfully.\nNew Balance: {format_currency(new_balance)}")
                              
            # Clear entries
            self.amount_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            
            # Refresh the student info and transactions display
            self.process_rfid_for_purchase()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while processing payment: {str(e)}")
    
    def show_recharge_screen(self):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Title
        title_label = ttk.Label(self.main_frame, text="Recharge Wallet", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame for RFID input
        rfid_frame = ttk.Frame(self.main_frame)
        rfid_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(rfid_frame, text="Student RFID:").pack(side=tk.LEFT, padx=5)
        self.recharge_rfid_entry = ttk.Entry(rfid_frame, width=15)
        self.recharge_rfid_entry.pack(side=tk.LEFT, padx=5)
        self.recharge_rfid_entry.focus()
        
        # Frame for student info (will be populated after RFID is entered)
        self.recharge_student_info_frame = ttk.Frame(self.main_frame)
        self.recharge_student_info_frame.pack(pady=10, fill=tk.X)
        
        # Frame for recharge details
        self.recharge_details_frame = ttk.Frame(self.main_frame)
        self.recharge_details_frame.pack(pady=10, fill=tk.X)
        
        # Back button
        ttk.Button(self.main_frame, text="Back", 
                  command=self.show_main_menu).pack(pady=10)
        
        # Bind Enter key to the callback
        self.recharge_rfid_entry.bind('<Return>', lambda event: self.process_rfid_for_recharge())
        
        # Button to submit RFID
        ttk.Button(rfid_frame, text="Submit", 
                  command=self.process_rfid_for_recharge).pack(side=tk.LEFT, padx=5)
    
    def process_rfid_for_recharge(self):
        # Clear previous content in frames
        for widget in self.recharge_student_info_frame.winfo_children():
            widget.destroy()
        for widget in self.recharge_details_frame.winfo_children():
            widget.destroy()
            
        rfid = self.recharge_rfid_entry.get().strip()
        
        if not validate_rfid(rfid):
            messagebox.showerror("Invalid RFID", "Please enter a valid 10-digit RFID.")
            return
            
        # Get student details
        student = get_student_by_rfid(self.db, rfid)
        
        if not student:
            messagebox.showerror("Student Not Found", "No student found with this RFID.")
            return
            
        # Display student info
        ttk.Label(self.recharge_student_info_frame, text=f"Student: {student.get('name', 'N/A')}", 
                 font=("Helvetica", 12)).pack(anchor=tk.W, padx=5)
        ttk.Label(self.recharge_student_info_frame, text=f"Department: {student.get('department', 'N/A')} - {student.get('year', 'N/A')} Year", 
                 font=("Helvetica", 10)).pack(anchor=tk.W, padx=5)
        ttk.Label(self.recharge_student_info_frame, text=f"Current Balance: {format_currency(student.get('wallet_balance', 0))}", 
                 font=("Helvetica", 12, "bold")).pack(anchor=tk.W, padx=5)
        
        # Recharge details frame
        ttk.Label(self.recharge_details_frame, text="Enter Recharge Details:", 
                 font=("Helvetica", 12)).pack(anchor=tk.W, padx=5, pady=5)
        
        # Amount frame
        amount_frame = ttk.Frame(self.recharge_details_frame)
        amount_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(amount_frame, text="Amount (₹):").pack(side=tk.LEFT, padx=5)
        self.recharge_amount_entry = ttk.Entry(amount_frame, width=10)
        self.recharge_amount_entry.pack(side=tk.LEFT, padx=5)
        
        # Method frame
        method_frame = ttk.Frame(self.recharge_details_frame)
        method_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(method_frame, text="Method:").pack(side=tk.LEFT, padx=5)
        self.recharge_method_var = tk.StringVar(value="Cash")
        methods = ["Cash", "UPI", "Card"]
        method_combobox = ttk.Combobox(method_frame, textvariable=self.recharge_method_var, 
                                      values=methods, width=10, state="readonly")
        method_combobox.pack(side=tk.LEFT, padx=5)
        
        # Process button
        ttk.Button(self.recharge_details_frame, text="Process Recharge", 
                  command=lambda: self.process_recharge(student)).pack(pady=10)
        
        # Transaction history (will be added in the future)
        ttk.Label(self.recharge_details_frame, text="Recent Transactions:", 
                 font=("Helvetica", 11)).pack(anchor=tk.W, padx=5, pady=(15,5))
        
        # Display recent transactions
        self.display_recent_transactions(self.recharge_details_frame, student['id'])
    
    def process_recharge(self, student):
        try:
            amount_str = self.recharge_amount_entry.get().strip()
            method = self.recharge_method_var.get()
            
            # Validate input
            if not amount_str:
                messagebox.showerror("Invalid Input", "Please enter a valid amount.")
                return
                
            try:
                amount = float(amount_str)
                if amount <= 0:
                    messagebox.showerror("Invalid Amount", "Amount must be greater than zero.")
                    return
            except ValueError:
                messagebox.showerror("Invalid Amount", "Please enter a valid number for amount.")
                return
                
            # Process the transaction
            transaction = {
                'student_id': student['id'],
                'amount': amount,
                'type': 'credit',
                'description': f"Wallet Recharge via {method}",
                'location': 'Canteen',
                'timestamp': datetime.datetime.now()
            }
            
            # Update student's wallet balance
            current_balance = student.get('wallet_balance', 0)
            new_balance = current_balance + amount
            
            # Perform the database operations in a transaction
            transaction_batch = self.db.batch()
            
            # Add transaction
            transaction_ref = self.db.collection('transactions').document()
            transaction_batch.set(transaction_ref, transaction)
            
            # Update student balance
            student_ref = self.db.collection('students').document(student['id'])
            transaction_batch.update(student_ref, {'wallet_balance': new_balance})
            
            # Commit the batch
            transaction_batch.commit()
            
            # Show success message
            messagebox.showinfo("Recharge Successful", 
                              f"Wallet recharged with {format_currency(amount)} successfully.\nNew Balance: {format_currency(new_balance)}")
                              
            # Clear entry
            self.recharge_amount_entry.delete(0, tk.END)
            
            # Refresh the student info and transactions display
            self.process_rfid_for_recharge()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while processing recharge: {str(e)}")
    
    def show_balance_screen(self):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Title
        title_label = ttk.Label(self.main_frame, text="Check Balance", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame for RFID input
        rfid_frame = ttk.Frame(self.main_frame)
        rfid_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(rfid_frame, text="Student RFID:").pack(side=tk.LEFT, padx=5)
        self.balance_rfid_entry = ttk.Entry(rfid_frame, width=15)
        self.balance_rfid_entry.pack(side=tk.LEFT, padx=5)
        self.balance_rfid_entry.focus()
        
        # Frame for student info (will be populated after RFID is entered)
        self.balance_student_info_frame = ttk.Frame(self.main_frame)
        self.balance_student_info_frame.pack(pady=10, fill=tk.X)
        
        # Frame for balance details
        self.balance_details_frame = ttk.Frame(self.main_frame)
        self.balance_details_frame.pack(pady=10, fill=tk.X)
        
        # Back button
        ttk.Button(self.main_frame, text="Back", 
                  command=self.show_main_menu).pack(pady=10)
        
        # Bind Enter key to the callback
        self.balance_rfid_entry.bind('<Return>', lambda event: self.check_balance())
        
        # Button to submit RFID
        ttk.Button(rfid_frame, text="Submit", 
                  command=self.check_balance).pack(side=tk.LEFT, padx=5)
    
    def check_balance(self):
        # Clear previous content in frames
        for widget in self.balance_student_info_frame.winfo_children():
            widget.destroy()
        for widget in self.balance_details_frame.winfo_children():
            widget.destroy()
            
        rfid = self.balance_rfid_entry.get().strip()
        
        if not validate_rfid(rfid):
            messagebox.showerror("Invalid RFID", "Please enter a valid 10-digit RFID.")
            return
            
        # Get student details
        student = get_student_by_rfid(self.db, rfid)
        
        if not student:
            messagebox.showerror("Student Not Found", "No student found with this RFID.")
            return
            
        # Display student info
        ttk.Label(self.balance_student_info_frame, text=f"Student: {student.get('name', 'N/A')}", 
                 font=("Helvetica", 12)).pack(anchor=tk.W, padx=5)
        ttk.Label(self.balance_student_info_frame, text=f"Department: {student.get('department', 'N/A')} - {student.get('year', 'N/A')} Year", 
                 font=("Helvetica", 10)).pack(anchor=tk.W, padx=5)
        
        # Display balance
        balance_frame = ttk.Frame(self.balance_details_frame)
        balance_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(balance_frame, text="Current Balance:", 
                 font=("Helvetica", 14)).pack(side=tk.LEFT, padx=5)
        ttk.Label(balance_frame, text=format_currency(student.get('wallet_balance', 0)), 
                 font=("Helvetica", 14, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Transaction history
        ttk.Label(self.balance_details_frame, text="Recent Transactions:", 
                 font=("Helvetica", 11)).pack(anchor=tk.W, padx=5, pady=(15,5))
        
        # Display recent transactions
        self.display_recent_transactions(self.balance_details_frame, student['id']) 