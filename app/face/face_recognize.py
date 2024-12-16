import cv2
import numpy as np
import base64
import io
import os
from PIL import Image

face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def face_recognize(img, user_id, img_id):
    img = base64_to_image(img)
    return generate_datasets(img, user_id,img_id)
    

def base64_to_image(base64_string):
    imgdata = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(imgdata))
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

def image_to_base64(img):
    _, buffer = cv2.imencode('.jpg', img)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return img_str

def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, text = '', clf = None):
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    features = classifier.detectMultiScale(gray_image, scaleFactor, minNeighbors)
    
    for (x, y, w, h) in features:
        cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)


def generate_datasets(frame, user_id,img_id):
    def face_cropped(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        if len(faces) == 0:
            return None
        for (x, y, w, h) in faces:
            cropped_face = img[y:y+h, x:x+w]
        return cropped_face
    
    current_directory = os.path.dirname(os.path.abspath(__file__))
    user_folder = os.path.join(current_directory, f"data/user_{user_id}")
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    if face_cropped(frame) is not None:
        face = cv2.resize(face_cropped(frame), (200, 200))
        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        file_name_path = f"{user_folder}/user.{user_id}.{img_id}.jpg"
        cv2.imwrite(file_name_path, face)
        return 'good'


