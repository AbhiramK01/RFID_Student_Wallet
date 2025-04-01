import tkinter as tk
from tkinter import ttk, messagebox
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import random
from functools import wraps
from firebase_admin import firestore
import cv2
import numpy as np
import face_recognition
import base64
import io
from PIL import Image, ImageTk

# RFID handling
def validate_rfid(rfid):
    """Validate if the RFID is in the correct format (10 digits)"""
    if rfid and re.match(r'^\d{10}$', rfid):
        return True
    return False

def read_rfid_input(entry):
    """Simulate reading RFID from a reader by getting the value from an entry widget"""
    rfid = entry.get().strip()
    if validate_rfid(rfid):
        return rfid
    return None

def authenticate_admin(rfid):
    """Check if the RFID belongs to an admin"""
    return rfid == "0006435835"  # Admin RFID as specified in the requirements

def validate_pin(pin):
    """Validate if the PIN is in the correct format (4 digits)"""
    if pin and re.match(r'^\d{4}$', pin):
        return True
    return False

# Firebase helpers
def get_student_by_rfid(db, rfid):
    """Get student document from Firebase by RFID"""
    if not validate_rfid(rfid):
        return None
    
    students_ref = db.collection('students')
    query = students_ref.where(filter=firestore.FieldFilter('rfid', '==', rfid)).limit(1)
    results = query.get()
    
    for doc in results:
        return {'id': doc.id, **doc.to_dict()}
    
    return None

def simulate_biometric_auth():
    """This function is kept for compatibility but should not be used anymore"""
    print("WARNING: simulate_biometric_auth is deprecated. Use verify_face instead.")
    return random.random() < 0.9

def check_attendance_exists(db, student_id, date_str=None):
    """Check if attendance already exists for the student on the given date"""
    if date_str is None:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    attendance_ref = db.collection('attendance')
    query = attendance_ref.where(
        filter=firestore.FieldFilter('student_id', '==', student_id)
    ).where(
        filter=firestore.FieldFilter('date', '==', date_str)
    )
    
    results = query.get()
    return len(results) > 0

def send_email(to_email, subject, message):
    """Send email using SMTP (placeholder function)"""
    # This is a placeholder. In a real application, you would configure the SMTP server
    # For the POC, we'll just simulate email sending
    try:
        print(f"Email sent to: {to_email}")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def format_currency(amount):
    """Format amount as currency"""
    return f"₹ {amount:.2f}"

def create_entry_with_label(parent, label_text, row, column=0, width=20, show=None):
    """Helper function to create a labeled entry field"""
    label = ttk.Label(parent, text=label_text)
    label.grid(row=row, column=column, sticky="w", padx=5, pady=5)
    
    entry = ttk.Entry(parent, width=width)
    if show:
        entry.config(show=show)
    entry.grid(row=row, column=column+1, padx=5, pady=5, sticky="ew")
    
    return entry

def create_rfid_frame(parent, callback):
    """Create a standard RFID input frame"""
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.X, padx=20, pady=10)
    
    label = ttk.Label(frame, text="Tap or Enter RFID:")
    label.pack(side=tk.LEFT, padx=5)
    
    entry = ttk.Entry(frame, width=15)
    entry.pack(side=tk.LEFT, padx=5)
    entry.focus()
    
    button = ttk.Button(frame, text="Submit", 
                         command=lambda: callback(entry.get()))
    button.pack(side=tk.LEFT, padx=5)
    
    # Bind Enter key to the callback
    entry.bind('<Return>', lambda event: callback(entry.get()))
    
    return frame, entry

def get_spending_pattern(db, student_id, days=30):
    """Analyze student spending pattern for AI recommendations"""
    try:
        # Get all transactions for this student in the past 'days' days
        today = datetime.datetime.now()
        start_date = today - datetime.timedelta(days=days)
        
        # Use only student_id filter in the Firestore query
        transactions_ref = db.collection('transactions')
        query = transactions_ref.where(
            filter=firestore.FieldFilter('student_id', '==', student_id)
        )
        
        # Get all transactions and filter in memory
        transactions = list(query.get())
        if not transactions:
            return None
            
        # Filter by date and type in Python
        filtered_transactions = []
        for tx_doc in transactions:
            tx_data = tx_doc.to_dict()
            tx_timestamp = tx_data.get('timestamp')
            tx_type = tx_data.get('type')
            
            # Handle timezone awareness issue - convert both to naive datetime for comparison
            # or skip comparison if timestamp is missing
            if tx_timestamp:
                # If timestamp is timezone-aware, convert to naive by replacing tzinfo
                if hasattr(tx_timestamp, 'tzinfo') and tx_timestamp.tzinfo is not None:
                    naive_timestamp = tx_timestamp.replace(tzinfo=None)
                else:
                    naive_timestamp = tx_timestamp
                    
                if naive_timestamp >= start_date and tx_type == 'debit':
                    filtered_transactions.append(tx_data)
            
        # If no relevant transactions found after filtering
        if not filtered_transactions:
            return None
            
        total_amount = 0
        transaction_count = len(filtered_transactions)
        
        for tx_data in filtered_transactions:
            total_amount += tx_data.get('amount', 0)
        
        if transaction_count == 0:
            return None
            
        # Calculate daily and weekly average spending
        daily_avg = total_amount / days
        weekly_avg = daily_avg * 7
        
        return {
            'daily_avg': daily_avg,
            'weekly_avg': weekly_avg,
            'transaction_count': transaction_count,
            'total_spent': total_amount
        }
    except Exception as e:
        print(f"Error analyzing spending pattern: {e}")
        return None

def recommend_recharge_amount(spending_pattern):
    """Recommend recharge amount based on spending pattern"""
    if not spending_pattern:
        return 500  # Default recommendation if no pattern available
    
    # Recommend two week's worth of spending, rounded to nearest 100
    recommendation = spending_pattern['weekly_avg'] * 2
    return round(recommendation / 100) * 100

def get_similar_books(db, book_id):
    """Get similar books based on lending history ("users who read this also read") or category"""
    try:
        # First, get the current book's details
        book_ref = db.collection('books').document(book_id)
        book_doc = book_ref.get()
        
        if not book_doc.exists:
            # Try to search by the book_id field instead of document ID
            books_query = db.collection('books').where(
                filter=firestore.FieldFilter('book_id', '==', book_id)
            ).limit(1)
            book_results = list(books_query.get())
            if not book_results:
                return []
            book_doc = book_results[0]
            
        current_book = book_doc.to_dict()
        current_category = current_book.get('category')
        
        # Get lending history for this book
        lending_ref = db.collection('lendings')
        query = lending_ref.where(
            filter=firestore.FieldFilter('book_id', '==', book_id)
        ).where(
            filter=firestore.FieldFilter('status', '==', 'returned')
        )
        
        lending_results = list(query.get())
        
        # If no results found, try with the document ID
        if not lending_results:
            query = lending_ref.where(
                filter=firestore.FieldFilter('book_id', '==', book_doc.id)
            ).where(
                filter=firestore.FieldFilter('status', '==', 'returned')
            )
            lending_results = list(query.get())
        
        student_ids = set()
        
        # Collect student IDs who have borrowed this book
        for doc in lending_results:
            student_id = doc.to_dict().get('student_id')
            if student_id:
                student_ids.add(student_id)
        
        similar_books = []
        book_scores = {}  # book_id -> score
        
        if student_ids:
            # Find other books borrowed by these students - "users who read this also read"
            for student_id in student_ids:
                student_query = lending_ref.where(
                    filter=firestore.FieldFilter('student_id', '==', student_id)
                ).where(
                    filter=firestore.FieldFilter('status', '==', 'returned')
                )
                
                for doc in student_query.get():
                    lending_data = doc.to_dict()
                    other_book_id = lending_data.get('book_id')
                    if other_book_id and other_book_id != book_id and other_book_id != book_doc.id:
                        if other_book_id not in book_scores:
                            book_scores[other_book_id] = 0
                        book_scores[other_book_id] += 1
            
            # Sort books by how many students borrowed them
            sorted_books = sorted(book_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Get book details for the most frequently borrowed books
            for other_book_id, score in sorted_books[:5]:  # Get top 5
                other_book_ref = db.collection('books').document(other_book_id)
                other_book_doc = other_book_ref.get()
                
                if other_book_doc.exists:
                    other_book = other_book_doc.to_dict()
                    other_book['id'] = other_book_doc.id
                    if other_book.get('available', True):  # Only recommend available books
                        similar_books.append(other_book)
        
        # If we don't have enough recommendations from lending history,
        # fall back to category-based recommendations
        if len(similar_books) < 3 and current_category:
            category_query = db.collection('books').where(
                filter=firestore.FieldFilter('category', '==', current_category)
            ).where(
                filter=firestore.FieldFilter('available', '==', True)
            ).limit(10)
            
            for doc in category_query.get():
                book_data = doc.to_dict()
                book_data['id'] = doc.id
                book_doc_id = doc.id
                doc_book_id = book_data.get('book_id', book_doc_id)
                
                # Skip the current book and books already in similar_books
                if (doc_book_id != book_id and book_doc_id != book_id and 
                    not any(b.get('id') == book_doc_id for b in similar_books)):
                    similar_books.append(book_data)
        
        # Randomly select 3 books if we have more
        if len(similar_books) > 3:
            return random.sample(similar_books, 3)
        return similar_books
        
    except Exception as e:
        print(f"Error getting similar books: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_book_recommendations(db, student_id):
    """Get personalized book recommendations based on student's reading history"""
    try:
        # Get student's lending history
        lending_ref = db.collection('lendings')
        query = lending_ref.where(
            filter=firestore.FieldFilter('student_id', '==', student_id)
        ).where(
            filter=firestore.FieldFilter('status', '==', 'returned')
        )
        
        lending_results = query.get()
        if not lending_results:
            return []
        
        # Collect categories of books the student has read and the book IDs they've read
        read_categories = set()
        read_book_ids = set()
        
        for doc in lending_results:
            lending_data = doc.to_dict()
            book_id = lending_data.get('book_id')
            if book_id:
                read_book_ids.add(book_id)
                book_ref = db.collection('books').document(book_id)
                book_doc = book_ref.get()
                if book_doc.exists:
                    book_data = book_doc.to_dict()
                    category = book_data.get('category')
                    if category:
                        read_categories.add(category)
        
        if not read_categories:
            return []
        
        # Get recommendations from the same categories
        recommendations = []
        for category in read_categories:
            category_query = db.collection('books').where(
                filter=firestore.FieldFilter('category', '==', category)
            ).where(
                filter=firestore.FieldFilter('available', '==', True)
            ).limit(10)  # Get more books per category for better randomization
            
            for doc in category_query.get():
                book_data = doc.to_dict()
                book_data['id'] = doc.id
                book_doc_id = doc.id
                doc_book_id = book_data.get('book_id', book_doc_id)
                
                # Don't recommend books the student has already read
                if doc_book_id not in read_book_ids and book_doc_id not in read_book_ids:
                    recommendations.append(book_data)
        
        # Randomly select 3 books if we have more
        if len(recommendations) > 3:
            return random.sample(recommendations, 3)
        return recommendations
        
    except Exception as e:
        print(f"Error getting book recommendations: {e}")
        import traceback
        traceback.print_exc()
        return []

# Face Recognition Utilities
def capture_face(camera_index=0, required_encodings=7):
    """
    Capture and encode a face using the device camera
    Returns: A list of face encodings or None if face not detected
    
    Captures multiple angles for better recognition accuracy.
    """
    try:
        # Initialize camera
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return None
            
        face_encodings = []
        attempts = 0
        max_attempts = 60  # Increased max attempts to allow more time for quality captures
        
        # Ask user to move their face into different positions for better coverage
        instructions = [
            "Look straight at the camera (frontal view)",
            "Turn slightly to the left",
            "Turn slightly to the right",
            "Tilt your head up slightly",
            "Tilt your head down slightly",
            "Move slightly closer to the camera",
            "Move slightly further from the camera"
        ]
        
        current_instruction = 0
        instruction_attempts = 0
        max_instruction_attempts = 10
        delay_between_captures = 800  # ms between successful captures - increased for better positioning
        
        while len(face_encodings) < required_encodings and attempts < max_attempts:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture image.")
                break
                
            # Display the instruction
            instruction_text = instructions[current_instruction]
            cv2.putText(frame, instruction_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Add progress text
            progress_text = f"Position {current_instruction + 1}/{len(instructions)}"
            cv2.putText(frame, progress_text, (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Convert from BGR to RGB (face_recognition uses RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find faces in current frame using HOG model for better precision
            face_locations = face_recognition.face_locations(rgb_frame, model="hog")
            
            if len(face_locations) == 1:  # Exactly one face detected
                # Get the encoding for the face with higher quality (more jitters = more processing)
                new_encodings = face_recognition.face_encodings(rgb_frame, face_locations, num_jitters=3)
                
                if len(new_encodings) > 0:
                    # Draw rectangle around the face
                    top, right, bottom, left = face_locations[0]
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    
                    # Calculate face size as percentage of frame for quality check
                    face_width = right - left
                    face_height = bottom - top
                    frame_width = frame.shape[1]
                    frame_height = frame.shape[0]
                    face_width_percent = (face_width / frame_width) * 100
                    face_height_percent = (face_height / frame_height) * 100
                    
                    # Check if face is too small
                    if face_width_percent < 15 or face_height_percent < 15:
                        cv2.putText(frame, "Move closer to camera", (left, top - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                        cv2.imshow('Capturing Face...', frame)
                        cv2.waitKey(50)
                        attempts += 1
                        continue
                    
                    # Check if face is too large
                    if face_width_percent > 60 or face_height_percent > 60:
                        cv2.putText(frame, "Move further from camera", (left, top - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                        cv2.imshow('Capturing Face...', frame)
                        cv2.waitKey(50)
                        attempts += 1
                        continue
                    
                    # Check if this encoding is sufficiently different from previous ones
                    is_unique = True
                    if len(face_encodings) > 0:
                        similarity_scores = []
                        for existing_encoding in face_encodings:
                            # Calculate how similar this is to existing encodings
                            distance = face_recognition.face_distance([existing_encoding], new_encodings[0])[0]
                            similarity_scores.append(distance)
                            if distance < 0.35:  # More strict uniqueness threshold
                                is_unique = False
                                break
                        
                        # Calculate average similarity
                        avg_similarity = sum(similarity_scores) / len(similarity_scores)
                        similarity_text = f"Uniqueness: {1.0 - avg_similarity:.2f}"
                        cv2.putText(frame, similarity_text, (left, bottom + 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    if is_unique or instruction_attempts >= max_instruction_attempts:
                        face_encodings.append(new_encodings[0])
                        instruction_attempts = 0
                        current_instruction = min(current_instruction + 1, len(instructions) - 1)
                        
                        # Status text
                        status_text = f"Captured: {len(face_encodings)}/{required_encodings}"
                        cv2.putText(frame, status_text, (10, frame.shape[0] - 20),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        # Wait longer between captures to allow position changes
                        cv2.imshow('Capturing Face...', frame)
                        cv2.waitKey(delay_between_captures)
                    else:
                        # Prompt for more variation
                        cv2.putText(frame, "Need more variation in position", (10, 90),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                
                instruction_attempts += 1
            else:
                # Reset instruction attempts if no face is detected
                instruction_attempts = 0
                
                if len(face_locations) == 0:
                    cv2.putText(frame, "No face detected", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, "Multiple faces detected", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Progress bar
            progress = int((len(face_encodings) / required_encodings) * frame.shape[1])
            cv2.rectangle(frame, (0, frame.shape[0] - 10), (progress, frame.shape[0]), (0, 255, 0), -1)
            
            # Display the frame
            cv2.imshow('Capturing Face...', frame)
            cv2.waitKey(50)  # Small delay
            
            attempts += 1
        
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        
        if len(face_encodings) < 5:  # Require at least 5 encodings for security
            print(f"Not enough face data captured. Got {len(face_encodings)}, need at least 5.")
            return None
            
        return face_encodings
    except Exception as e:
        print(f"Error in capture_face: {e}")
        import traceback
        traceback.print_exc()
        return None

def encode_face_to_base64(face_encodings):
    """Convert face encoding list to base64 string for storage"""
    try:
        if face_encodings is None or len(face_encodings) == 0:
            print("No face encodings provided to encode")
            return None
            
        # Ensure face_encodings is a numpy array
        encodings_array = np.array(face_encodings)
        
        # Print debug info about the shape
        print(f"Encoding shape before conversion: {encodings_array.shape}")
        
        # Ensure it's a 2D array (n_encodings, 128)
        if len(encodings_array.shape) == 1 and encodings_array.shape[0] == 128:
            # Single encoding, reshape to (1, 128)
            encodings_array = encodings_array.reshape(1, 128)
            print("Reshaped single encoding to 2D array")
            
        # Convert numpy array to bytes
        face_bytes = encodings_array.tobytes()
        
        # Encode bytes to base64
        face_base64 = base64.b64encode(face_bytes)
        encoded_string = face_base64.decode('utf-8')
        
        print(f"Successfully encoded {len(encodings_array)} face(s)")
        return encoded_string
    except Exception as e:
        print(f"Error encoding face: {e}")
        import traceback
        traceback.print_exc()
        return None

def decode_base64_to_face(base64_string):
    """Convert base64 string back to face encoding list"""
    try:
        if not base64_string:
            print("No base64 string provided to decode")
            return None
            
        # Decode base64 to bytes
        face_bytes = base64.b64decode(base64_string)
        
        # Convert bytes back to numpy array of face encodings
        face_encodings = np.frombuffer(face_bytes, dtype=np.float64)
        
        # Calculate how many encodings we have (each is 128 elements)
        num_encodings = len(face_encodings) // 128
        print(f"Decoded data contains {num_encodings} face encodings")
        
        if num_encodings < 1:
            print("Error: Invalid face encoding format - not enough data")
            return None
            
        # Reshape to the correct shape for multiple encodings
        reshaped_encodings = face_encodings.reshape(num_encodings, 128)
        print(f"Decoded face shape: {reshaped_encodings.shape}")
        
        return reshaped_encodings
    except Exception as e:
        print(f"Error decoding face: {e}")
        import traceback
        traceback.print_exc()
        return None

def verify_face(known_face_encodings, camera_index=0, tolerance=0.45):
    """
    Verify a face against stored encoding
    Returns: True if face matches, False otherwise
    
    Note: Lower tolerance values make matching more strict
    Typical values: 0.6 (lenient), 0.5 (moderate), 0.4-0.45 (strict)
    We use 0.45 by default for high security.
    """
    try:
        if known_face_encodings is None or len(known_face_encodings) == 0:
            print("No face data available for comparison")
            return False
            
        # Initialize camera
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return False
            
        verification_result = False
        attempts = 0
        max_attempts = 40  # Increased max attempts
        
        # For extra security, require multiple successful matches with consistent low distances
        successful_matches = 0
        required_matches = 5  # Increased from 3 to 5
        
        # Store distance measurements for consistency check
        distance_history = []
        distance_consistency_threshold = 0.03  # Maximum allowed variance in distances
        
        while (not verification_result) and attempts < max_attempts:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture image.")
                break
                
            # Convert from BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find faces in current frame
            face_locations = face_recognition.face_locations(rgb_frame, model="hog")  # Use HOG model for better accuracy
            
            # If exactly one face is detected, try to match it
            if len(face_locations) == 1:
                # Get the encoding for the face
                current_face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, num_jitters=2)
                
                if len(current_face_encodings) == 0:
                    cv2.putText(frame, "Could not encode face", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.imshow('Face Verification', frame)
                    cv2.waitKey(100)
                    attempts += 1
                    continue
                
                current_face_encoding = current_face_encodings[0]
                
                # Calculate all distances to all known encodings
                all_distances = []
                min_distance = float('inf')
                total_distance = 0
                
                for i, known_encoding in enumerate(known_face_encodings):
                    # Calculate face distance (lower is more similar)
                    face_distance = face_recognition.face_distance([known_encoding], current_face_encoding)[0]
                    all_distances.append(face_distance)
                    total_distance += face_distance
                    
                    if face_distance < min_distance:
                        min_distance = face_distance
                
                # Calculate average distance across all encodings
                avg_distance = total_distance / len(known_face_encodings) if len(known_face_encodings) > 0 else float('inf')
                
                print(f"Min distance: {min_distance:.4f}, Avg distance: {avg_distance:.4f}, Tolerance: {tolerance}")
                
                # Add to distance history for consistency check
                distance_history.append(min_distance)
                if len(distance_history) > 5:  # Keep last 5 measurements
                    distance_history.pop(0)
                
                # Calculate distance variance (consistency check)
                distance_variance = max(distance_history) - min(distance_history) if distance_history else float('inf')
                
                # Check if the frame has a match below tolerance
                if min_distance <= tolerance:
                    # Only count as match if average distance is also reasonably low
                    if avg_distance < tolerance * 1.3:
                        # Only increment if distances are consistent (not fluctuating wildly)
                        if distance_variance < distance_consistency_threshold or successful_matches < 2:
                            successful_matches += 1
                        match_status = f"Match! ({successful_matches}/{required_matches})"
                        match_color = (0, 255, 0)  # Green
                    else:
                        match_status = "Inconsistent match"
                        match_color = (0, 165, 255)  # Orange
                else:
                    # Reset successful matches counter if we get a non-match
                    successful_matches = 0
                    match_status = "No match"
                    match_color = (0, 0, 255)  # Red
                
                # Check if we've achieved enough successful matches
                if successful_matches >= required_matches:
                    verification_result = True
                
                # Draw rectangle around the face
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(frame, (left, top), (right, bottom), match_color, 2)
                
                # Add match status text
                cv2.putText(frame, match_status, (left, top - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, match_color, 2)
                
                # Add distance information at the bottom of the frame
                distance_text = f"Min dist: {min_distance:.4f} | Avg: {avg_distance:.4f} | Var: {distance_variance:.4f}"
                cv2.putText(frame, distance_text, (10, frame.shape[0] - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Add guidance on threshold
                threshold_text = f"Threshold: {tolerance:.4f} (Lower is stricter)"
                cv2.putText(frame, threshold_text, (10, frame.shape[0] - 45),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
            else:
                if len(face_locations) == 0:
                    cv2.putText(frame, "No face detected", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, "Multiple faces detected", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Reset successful matches counter if face detection fails
                successful_matches = 0
                # Clear distance history
                distance_history = []
            
            # Display the frame
            cv2.imshow('Face Verification', frame)
            cv2.waitKey(100)  # Small delay
            
            attempts += 1
        
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        
        return verification_result
    except Exception as e:
        print(f"Error in verify_face: {e}")
        import traceback
        traceback.print_exc()
        return False 