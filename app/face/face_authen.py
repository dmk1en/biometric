import numpy  as np
from PIL import Image
import os
import cv2
import cv2
import numpy as np
import os
from PIL import Image


# def train_classifier():
#     data_dir = os.path.join(os.path.dirname(__file__), "data")
#     # Find all user folders in the data directory
#     user_folders = [os.path.join(data_dir, folder) for folder in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, folder))]
#     faces = []
#     ids = []

#     for user_folder in user_folders:
#         # Look for all image files in each user's folder
#         for image_path in os.listdir(user_folder):
#             if image_path.endswith(".jpg"):  # Only process .jpg files
#                 img_path = os.path.join(user_folder, image_path)
#                 img = Image.open(img_path).convert('L')  # Convert image to grayscale
#                 imageNp = np.array(img, 'uint8')

#                 # Extract user_id from the filename (e.g., user.1.1.jpg -> user_id=1)
#                 user_id = int(image_path.split(".")[1])

#                 faces.append(imageNp)
#                 ids.append(user_id)
    
#     ids = np.array(ids)

#     # Create and train the classifier
#     clf = cv2.face.LBPHFaceRecognizer_create()
#     clf.train(faces, ids)

#     # Save the trained classifier
#     clf.write("classifier.xml")
#     print("Training complete. Classifier saved as 'classifier.xml'.")

def add_new_user_data(user_id, data_dir="data"):
    user_folder = os.path.join(os.path.dirname(__file__), os.path.join(data_dir, f"user_{user_id}"))
    print(user_folder)
    
    if not os.path.exists(user_folder):
        print(f"No data found for user {user_id}. Please ensure the user's images are in '{user_folder}'.")
        return

    # Load existing classifier if it exists
    clf_path = "classifier.xml"
    if os.path.exists(clf_path):
        clf = cv2.face.LBPHFaceRecognizer_create()
        clf.read(clf_path)
        print("Existing classifier loaded.")
    else:
        print("No existing classifier found. Creating a new classifier.")
        clf = cv2.face.LBPHFaceRecognizer_create()

    # Collect new user data
    faces = []
    ids = []

    for image_path in os.listdir(user_folder):
        if image_path.endswith(".jpg"):  # Only process .jpg files
            img_path = os.path.join(user_folder, image_path)
            img = Image.open(img_path).convert('L')  # Convert image to grayscale
            imageNp = np.array(img, 'uint8')

            faces.append(imageNp)
            ids.append(user_id)  # Use the new user_id for all their images

    if not faces:
        print(f"No valid images found for user {user_id}.")
        return

    # Train with the new user data
    print(f"Adding data for user {user_id}.")
    clf.update(faces, np.array(ids))

    # Save the updated classifier
    clf.write(clf_path)
    print(f"Classifier updated with data for user {user_id} and saved as '{clf_path}'.")


from facenet_pytorch import MTCNN
import torch
import time
device =  torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(thresholds= [0.7, 0.7, 0.8] ,keep_all=True, device = device)


# Function to detect motion
def detect_motion(previous_landmarks, smoothing_factor, motion_threshold, 
                  movement_history, frame_buffer,frame):
    motion_detected = False
    current_landmarks = None
    if frame is None:
        return motion_detected, previous_landmarks, movement_history, frame
    
    
    boxes, _, points = mtcnn.detect(frame, landmarks=True)

    if boxes is not None:
        
        # for box in boxes:
        #         bbox = list(map(int,box.tolist()))
        #         frame = cv2.rectangle(frame,(bbox[0],bbox[1]),(bbox[2],bbox[3]),(0,0,255),6)
        # for point_set in points:
        #     for point in point_set:
        #         frame = cv2.circle(frame,(int(point[0]),int(point[1])),5,(0,255),5)
        print("face detected")
        bbox = boxes[0]  # Assuming one face, take the first box
        points_normalized = [(point - bbox[:2]) / (bbox[2:] - bbox[:2]) for point in points[0]]
        current_landmarks = np.array(points_normalized, dtype=np.float64).reshape(1, 5, 2)

        if previous_landmarks.size == 0:
            previous_landmarks = current_landmarks
        else:
            smoothed_landmarks = smoothing_factor * previous_landmarks + (1 - smoothing_factor) * current_landmarks
            movement = np.linalg.norm(smoothed_landmarks - previous_landmarks, axis=2)
            avg_movement = np.median(movement)
            movement_history.append(avg_movement)

            if len(movement_history) > frame_buffer:
                movement_history.pop(0)

            smoothed_movement = np.mean(movement_history)

            if smoothed_movement > motion_threshold:
                motion_detected = True
            previous_landmarks = smoothed_landmarks
    return motion_detected, previous_landmarks, movement_history, frame
    
    

def update_motion_timer(motion_start_time, motion_time, motion_duration_threshold):
    if motion_start_time is None:
        motion_start_time = time.time()  # Record the start time of motion
    else:
        elapsed_time = time.time() - motion_start_time
        if elapsed_time <= 1:  # Check if motion is within the allowed duration
            motion_time += 1
        else:
            motion_start_time = None
            motion_time = 0

    return motion_start_time, motion_time


def authen(img):
    print("authen started")
    
    face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.read("classifier.xml")
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    features = face_classifier.detectMultiScale(gray_image, 1.1, 10)
    for (x, y, w, h) in features:
        id, pred = clf.predict(gray_image[y:y+h, x:x+w])
        confidence = int(100 * (1 - pred / 300))
        print(confidence, id)
        if confidence >= 70:
            return id
        return None
