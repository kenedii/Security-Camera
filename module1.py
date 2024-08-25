from cv2 import VideoCapture, imshow, waitKey, destroyAllWindows, imwrite
import cv2
import face_recognition
import os
import numpy as np
import time

# Directory to save snapshots
BASE_DIR = 'snapshots'

def get_next_person_id():
    """Get the next available person folder ID."""
    existing_ids = [int(d) for d in os.listdir(BASE_DIR) if d.isdigit()]
    next_id = max(existing_ids, default=0) + 1
    return next_id
    
def get_face_encoding_from_image(image_path):
    """Extract face encoding from a given image path."""
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)
    return face_encodings[0] if face_encodings else None

def get_all_face_encodings():
    """Load face encodings from all face.png files in the snapshots directory."""
    encodings = {}
    for folder in os.listdir(BASE_DIR):
        folder_path = os.path.join(BASE_DIR, folder)
        if os.path.isdir(folder_path):
            face_file = os.path.join(folder_path, 'face.png')
            if os.path.isfile(face_file):
                encoding = get_face_encoding_from_image(face_file)
                if encoding is not None:
                    encodings[folder] = encoding
    return encodings

def ensure_directory(person_id):
    """Ensure the directory for the person exists."""
    person_dir = os.path.join(BASE_DIR, str(person_id))
    if not os.path.exists(person_dir):
        os.makedirs(person_dir)
    return person_dir

def save_face_image(face_image, person_id):
    """Save the cropped face image as face.png."""
    person_dir = ensure_directory(person_id)
    face_file = os.path.join(person_dir, 'face.png')
    cv2.imwrite(face_file, face_image)
    print(f"Saved main face image to {face_file}")

def save_full_image(img, person_id):
    """Save the full image in the person's folder."""
    person_dir = ensure_directory(person_id)
    full_image_file = os.path.join(person_dir, f'full_image_{int(time.time())}.png')
    cv2.imwrite(full_image_file, img)
    print(f"Saved full image to {full_image_file}")

def takeSnapshot():
    try:
        # Initialize the camera
        cam = VideoCapture(0)  # 0 -> index of camera
        s, img = cam.read()
        if s:  # Frame captured without any errors
            rgb_frame = img[:, :, ::-1]
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            # Get face encodings from existing snapshots
            known_encodings = get_all_face_encodings()

            imshow("cam-test", img)
            key = waitKey(5000)  # Display the image for 5 seconds
            if key == 27:  # If ESC is pressed, exit
                destroyAllWindows()
                return None
            
            # Process each detected face
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                face_image = img[top:bottom, left:right]
                matched = False
                
                for person_id, known_encoding in known_encodings.items():
                    match = face_recognition.compare_faces([known_encoding], face_encoding)
                    if match[0]:
                        save_full_image(img, person_id)
                        matched = True
                        break

                if not matched:
                    # No match found, save the new face
                    new_person_id = get_next_person_id()
                    save_face_image(face_image, new_person_id)
                    save_full_image(img, new_person_id)
        else:
            print("Failed to capture image")
    except Exception as e:
        print("An error occurred:", e)
    finally:
        # Release camera and close any open windows
        cam.release()
        destroyAllWindows()

takeSnapshot()
