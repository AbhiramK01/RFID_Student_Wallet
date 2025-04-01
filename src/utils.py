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

def get_similar_books(db, book_id, max_recommendations=3):
    """Get similar books based on lending history ("users who read this also read") or category"""
    try:
        # Use a cache to store similar book recommendations - check if we have it in memory
        if hasattr(get_similar_books, 'cache') and book_id in get_similar_books.cache:
            # Return cached results if they're less than 1 hour old
            cache_time, cached_results = get_similar_books.cache[book_id]
            if (datetime.datetime.now() - cache_time).seconds < 3600:  # 1 hour cache
                return cached_results
        
        # First get the current book's details - look up directly by ID first (most efficient)
        book_ref = db.collection('books').document(book_id)
        book_doc = book_ref.get()
        
        # If not found by document ID, try the book_id field
        if not book_doc.exists:
            # Use a more restrictive query to improve performance
            books_query = db.collection('books').where(
                filter=firestore.FieldFilter('book_id', '==', book_id)
            ).limit(1)
            
            books_results = list(books_query.get())
            if not books_results:
                # If we can't find the book, return empty recommendations
                return []
            book_doc = books_results[0]
        
        current_book = book_doc.to_dict()
        current_category = current_book.get('category')
        category_recommendations = []
        
        # Track all book IDs to avoid duplicates
        all_book_ids = set([book_id, book_doc.id])
        if 'book_id' in current_book:
            all_book_ids.add(current_book['book_id'])
        
        # Get category recommendations first - we'll use these as fallback
        if current_category:
            # Get books in the same category - limit to 10 for performance
            category_query = db.collection('books').where(
                filter=firestore.FieldFilter('category', '==', current_category)
            ).where(
                filter=firestore.FieldFilter('available', '==', True)
            ).limit(10)
            
            category_books = []
            for doc in category_query.get():
                book_data = doc.to_dict()
                doc_id = doc.id
                
                # Skip the current book
                if doc_id in all_book_ids or book_data.get('book_id') in all_book_ids:
                    continue
                
                book_data['id'] = doc_id
                category_books.append(book_data)
            
            # Randomly select up to max_recommendations books from the same category
            if category_books:
                if len(category_books) > max_recommendations:
                    category_recommendations = random.sample(category_books, max_recommendations)
                else:
                    category_recommendations = category_books
        
        # Get based on lending history - BUT limit queries to improve performance
        # Use a single query instead of multiple queries
        lending_query = db.collection('lendings').where(
            filter=firestore.FieldFilter('book_id', '==', book_id)
        ).where(
            filter=firestore.FieldFilter('status', '==', 'returned')
        ).limit(5)  # Limit to 5 most recent
        
        lending_results = list(lending_query.get())
        
        # If no results found by book_id, try the document ID
        if not lending_results and book_doc.id != book_id:
            lending_query = db.collection('lendings').where(
                filter=firestore.FieldFilter('book_id', '==', book_doc.id)
            ).where(
                filter=firestore.FieldFilter('status', '==', 'returned')
            ).limit(5)
            lending_results = list(lending_query.get())
        
        # If we have lending history
        if lending_results:
            student_ids = set()
            
            # Collect student IDs who have borrowed this book
            for doc in lending_results:
                student_id = doc.to_dict().get('student_id')
                if student_id:
                    student_ids.add(student_id)
            
            # If we have students who borrowed this book
            if student_ids:
                book_counts = {}  # book_id -> count
                book_data_map = {}  # book_id -> book_data
                
                # Only query for a few students to improve performance
                sample_students = list(student_ids)
                if len(sample_students) > 3:
                    sample_students = random.sample(sample_students, 3)
                
                # Get books borrowed by these students in a single batch
                for student_id in sample_students:
                    # Only get returned books (completed reading)
                    student_query = db.collection('lendings').where(
                        filter=firestore.FieldFilter('student_id', '==', student_id)
                    ).where(
                        filter=firestore.FieldFilter('status', '==', 'returned')
                    ).limit(10)  # Limit to 10 most recent books
                    
                    for doc in student_query.get():
                        lending_data = doc.to_dict()
                        other_book_id = lending_data.get('book_id')
                        
                        # Skip current book and already processed IDs
                        if not other_book_id or other_book_id in all_book_ids:
                            continue
                        
                        # Count occurrences
                        if other_book_id not in book_counts:
                            book_counts[other_book_id] = 0
                        book_counts[other_book_id] += 1
                
                # If we found books borrowed by similar users
                if book_counts:
                    # Sort books by popularity
                    sorted_books = sorted(book_counts.items(), key=lambda x: x[1], reverse=True)
                    
                    # Check availability and get details for top books
                    similar_books = []
                    checked_books = 0
                    
                    # Only check up to 10 books for performance
                    for other_book_id, _ in sorted_books[:10]:
                        if checked_books >= 10:  # Performance limit
                            break
                        checked_books += 1
                        
                        other_book_ref = db.collection('books').document(other_book_id)
                        other_book_doc = other_book_ref.get()
                        
                        if other_book_doc.exists:
                            other_book = other_book_doc.to_dict()
                            other_book['id'] = other_book_doc.id
                            
                            # Only include available books
                            if other_book.get('available', True):
                                similar_books.append(other_book)
                                
                                # Stop once we have enough recommendations
                                if len(similar_books) >= max_recommendations:
                                    break
                    
                    # If we found recommendations based on lending history
                    if similar_books:
                        # Cache the results
                        if not hasattr(get_similar_books, 'cache'):
                            get_similar_books.cache = {}
                        get_similar_books.cache[book_id] = (datetime.datetime.now(), similar_books)
                        return similar_books
        
        # If we get here, use category recommendations as fallback
        if category_recommendations:
            # Cache the results
            if not hasattr(get_similar_books, 'cache'):
                get_similar_books.cache = {}
            get_similar_books.cache[book_id] = (datetime.datetime.now(), category_recommendations)
            return category_recommendations
        
        # Last resort: get random books
        try:
            books_ref = db.collection('books').where(
                filter=firestore.FieldFilter('available', '==', True)
            ).limit(max_recommendations * 2)
            
            random_books = []
            for doc in books_ref.get():
                book_data = doc.to_dict()
                doc_id = doc.id
                
                # Skip the current book
                if doc_id in all_book_ids or book_data.get('book_id') in all_book_ids:
                    continue
                
                book_data['id'] = doc_id
                random_books.append(book_data)
            
            # Randomly select a few recommendations
            if random_books:
                if len(random_books) > max_recommendations:
                    random_books = random.sample(random_books, max_recommendations)
                
                # Cache the results
                if not hasattr(get_similar_books, 'cache'):
                    get_similar_books.cache = {}
                get_similar_books.cache[book_id] = (datetime.datetime.now(), random_books)
                return random_books
        except Exception as e:
            print(f"Error getting random books: {e}")
        
        # If all else fails, return empty list
        return []
        
    except Exception as e:
        print(f"Error getting similar books: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_book_recommendations(db, student_id, max_recommendations=3):
    """Get personalized book recommendations based on student's reading history"""
    try:
        # Use a cache to store user recommendations
        if hasattr(get_book_recommendations, 'cache') and student_id in get_book_recommendations.cache:
            # Return cached results if they're less than 1 hour old
            cache_time, cached_results = get_book_recommendations.cache[student_id]
            if (datetime.datetime.now() - cache_time).seconds < 3600:  # 1 hour cache
                return cached_results
        
        # Get student's lending history - limit to 10 most recent for performance
        lending_query = db.collection('lendings').where(
            filter=firestore.FieldFilter('student_id', '==', student_id)
        ).where(
            filter=firestore.FieldFilter('status', '==', 'returned')
        ).limit(10)  # Only get 10 most recent books
        
        lending_results = list(lending_query.get())
        if not lending_results:
            return []
        
        # Collect categories of books the student has read and the book IDs they've read
        read_categories = set()
        read_book_ids = set()
        category_counts = {}  # Track which categories the student reads most
        
        for doc in lending_results:
            lending_data = doc.to_dict()
            book_id = lending_data.get('book_id')
            if book_id:
                read_book_ids.add(book_id)
                
                # Get book details
                book_ref = db.collection('books').document(book_id)
                book_doc = book_ref.get()
                
                if book_doc.exists:
                    book_data = book_doc.to_dict()
                    category = book_data.get('category')
                    
                    if category:
                        read_categories.add(category)
                        
                        # Count category occurrences to prioritize favorite categories
                        if category not in category_counts:
                            category_counts[category] = 0
                        category_counts[category] += 1
        
        if not read_categories:
            return []
        
        # Prioritize categories by frequency
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        prioritized_categories = [cat for cat, _ in sorted_categories]
        
        # Get recommendations from the student's preferred categories
        recommendations = []
        books_per_category = max(1, max_recommendations // len(prioritized_categories))
        
        for category in prioritized_categories:
            # Limit to a small number per category for performance
            category_query = db.collection('books').where(
                filter=firestore.FieldFilter('category', '==', category)
            ).where(
                filter=firestore.FieldFilter('available', '==', True)
            ).limit(5)
            
            category_books = []
            for doc in category_query.get():
                book_data = doc.to_dict()
                book_id = doc.id
                
                # Don't recommend books the student has already read
                if book_id in read_book_ids or book_data.get('book_id') in read_book_ids:
                    continue
                
                book_data['id'] = book_id
                category_books.append(book_data)
            
            # Add some books from this category
            if category_books:
                if len(category_books) > books_per_category:
                    selected_books = random.sample(category_books, books_per_category)
                else:
                    selected_books = category_books
                
                recommendations.extend(selected_books)
            
            # Stop once we have enough recommendations
            if len(recommendations) >= max_recommendations:
                break
        
        # If we still need more recommendations, add random books
        if len(recommendations) < max_recommendations:
            available_query = db.collection('books').where(
                filter=firestore.FieldFilter('available', '==', True)
            ).limit(10)
            
            for doc in available_query.get():
                book_data = doc.to_dict()
                book_id = doc.id
                
                # Skip books that are already in recommendations or read by student
                if book_id in read_book_ids or book_data.get('book_id') in read_book_ids:
                    continue
                
                if not any(r.get('id') == book_id for r in recommendations):
                    book_data['id'] = book_id
                    recommendations.append(book_data)
                    
                    if len(recommendations) >= max_recommendations:
                        break
        
        # Limit to max_recommendations
        if len(recommendations) > max_recommendations:
            recommendations = recommendations[:max_recommendations]
        
        # Cache the results
        if not hasattr(get_book_recommendations, 'cache'):
            get_book_recommendations.cache = {}
        get_book_recommendations.cache[student_id] = (datetime.datetime.now(), recommendations)
            
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