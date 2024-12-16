from flask import Blueprint, request, jsonify, Response,session
import sqlite3
import cv2
import numpy as np
import base64
from flask_socketio import emit
from .face.face_recognize import face_recognize
from .socket import socketio
from .face.face_authen import detect_motion, update_motion_timer,authen

Auth = Blueprint('auth', __name__)

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@Auth.route('/recognize', methods=['POST'])
def recognize():
    image_file = request.files['image']
    count = request.form.get('count')
    if not image_file:
        return jsonify({"error": "No image file provided"}), 400
    
    try:
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM users")
        last_user_id = cursor.fetchone()[0]  # Fetch the max user_id
        
        # Handle case where the table is empty
        new_user_id = last_user_id + 1 if last_user_id is not None else 1
        
        # Convert the uploaded file to base64 string
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        # Process the image with face recognition and get the result in base64
        result = face_recognize(image_base64,new_user_id,count)
        
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
# Initialize motion detection variables
previous_landmarks = np.array([], dtype=np.float64)
smoothing_factor = 0.7
motion_threshold = 0.01
movement_history = []
frame_buffer = 5
motion_time = 0
motion_duration_threshold = 10 
motion_start_time = None
spoofing = True




@socketio.on("send_frame")
def handle_frame(data):
    
    global spoofing, previous_landmarks, movement_history, frame_buffer, motion_time, motion_start_time, motion_duration_threshold, smoothing_factor, motion_threshold
    # """ Receive frame from frontend, process it and send back results """
    
    # Decode the base64 frame received from frontend
    img_data = base64.b64decode(data['frame'])
    
    # with open("received_image.jpg", "wb") as f:
    #     f.write(img_data)

    np_img = np.frombuffer(img_data, dtype=np.uint8)
    np_img = np.array(np_img, dtype=np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    
    # Process the frame (e.g., detect motion or perform face recognition)
    if spoofing:
        motion_detected, previous_landmarks, movement_history, frame = detect_motion(
            previous_landmarks, smoothing_factor, motion_threshold, movement_history, frame_buffer, frame
        )
        if motion_detected:
            motion_start_time, motion_time = update_motion_timer(motion_start_time, motion_time, motion_duration_threshold)
            if motion_time >= motion_duration_threshold:
                spoofing = False
                
                print("Authentication complete")
    else:
        
        user_id = authen(frame)
        if user_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            conn.close()

            if user:
                # Set session for the authenticated user
                
                # session['user'] = user['username']
                # session.modified = True
                # print("Session on authen done:", session)
                
                emit("authentication_complete", {"username": user['username'], "status": "authenticated"})
                return


#     # Send feedback to frontend about motion or face recognition
#     emit("motion_detected", {"motion": "motion detected" if spoofing else "authentication complete"})
    
#     # # Optionally, you could send the processed frame back to the frontend
#     # _, buffer = cv2.imencode('.jpg', frame)
#     # frame_base64 = base64.b64encode(buffer).decode('utf-8')
#     # emit("processed_frame", {"frame": frame_base64})
    

@socketio.on("start_face_authen")
def start_face_authentication():
    """ Handle the start of face authentication """
    global spoofing
    spoofing = True  # Reset spoofing state
    emit("motion_detected", {"motion": "Detecting motion..."})
    # Optionally, you could start additional processes or emit other data here
    
    
    