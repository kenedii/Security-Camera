from cv2 import VideoCapture, imshow, waitKey, destroyAllWindows, imwrite
import cv2
import face_recognition
import os
import time
import pickle

# Directory to save snapshots
BASE_DIR = 'snapshots'
ENCODINGS_FILE = 'face_encodings.pkl'
TIMESTAMPS_FILE = 'face_timestamps.pkl'

def rw_encodings(operation='load', encodings=None): # Read/Write Encodings
    if operation == 'load':
        """Load face encodings from the pkl file."""
        if os.path.exists(ENCODINGS_FILE):
            with open(ENCODINGS_FILE, 'rb') as f:
                return pickle.load(f)
        return {}
    elif operation == 'save':
        """Save face encodings to the pkl file."""
        with open(ENCODINGS_FILE, 'wb') as f:
            pickle.dump(encodings, f)

def rw_timestamps(operation = 'load', timestamps=None): # Read/Write Timestamps
    if operation == 'load':
        """Load face timestamps from the pkl file."""
        if os.path.exists(TIMESTAMPS_FILE):
            with open(TIMESTAMPS_FILE, 'rb') as f:
                return pickle.load(f)
        return {}
    elif operation == 'save':
        """Save face timestamps to the pkl file."""
        with open(TIMESTAMPS_FILE, 'wb') as f:
            pickle.dump(timestamps, f)

def get_next_person_id(face_encodings):
    """Get the next available person folder ID."""
    existing_ids = list(face_encodings.keys())
    next_id = max(existing_ids) + 1
    return next_id

def ensure_directory(person_id):
    """Ensure the directory for the person exists."""
    person_dir = os.path.join(BASE_DIR, str(person_id))
    if not os.path.exists(person_dir):
        os.makedirs(person_dir)
    return person_dir

def save_full_image(img, person_id):
    """Save the full image in the person's folder."""
    person_dir = ensure_directory(person_id)
    full_image_file = os.path.join(person_dir, f'full_image_{int(time.time())}.png')
    cv2.imwrite(full_image_file, full_image_file)
    print(f"Saved full image to {full_image_file}")

def was_recently_seen(person_id, timestamps, cooldown=10):
    """Check if the person was seen within the last 'cooldown' seconds."""
    if person_id in timestamps and timestamps[person_id]:
        last_seen = timestamps[person_id][0]
        return (time.time() - last_seen) < cooldown
    return False

def update_timestamp(person_id, timestamps):
    """Update the timestamps for a person ID."""
    if person_id not in timestamps:
        timestamps[person_id] = []
    timestamps[person_id].insert(0, time.time())  # Add the current time to the front of the list

def takeSnapshot(face_timestamps, known_encodings, cooldown=10):
    try:
        # Initialize the camera
        cam = VideoCapture(0)  # 0 -> index of camera
        s, img = cam.read()
        if s:  # Frame captured without any errors
            rgb_frame = img[:, :, ::-1]
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            # Load face encodings and timestamps from the pkl files
            known_encodings = rw_encodings(operation='load')            
            face_timestamps = rw_timestamps(operation='load')

            imshow("cam-test", img)
            key = waitKey(5000)  # Display the image for 5 seconds
            if key == 27:  # If ESC is pressed, exit
                destroyAllWindows()
                return None
            
            # Process each detected face
            for face_encoding in zip(face_locations, face_encodings):
                #face_image = img[top:bottom, left:right]           # Crop the face, might not be necessary
                matched = False
                
                for person_id, known_encoding in known_encodings.items():
                    match = face_recognition.compare_faces([known_encoding], face_encoding)
                    if match[0]:
                        # Check if the person was recently seen
                        if not was_recently_seen(person_id, face_timestamps, cooldown):
                            save_full_image(img, person_id)
                            update_timestamp(person_id, face_timestamps)
                        matched = True
                        break

                if not matched:
                    # No match found, save the new face
                    new_person_id = get_next_person_id(face_encodings)
                    save_full_image(img, new_person_id)
                    known_encodings[new_person_id] = face_encoding
                    update_timestamp(new_person_id, face_timestamps)
        else:
            print("Failed to capture image")

    except Exception as e:
        print("An error occurred:", e)
    finally:
        # Release camera and close any open windows
        cam.release()
        destroyAllWindows()
        return known_encodings, face_timestamps

def scanCamera(delay=0.6, save_data_interval=10):
    # Continuously take snapshots from the camera
    # with a delay of 'delay' seconds between each snapshot
    # and save the face encodings and timestamps to the pkl files every 'save_data_interval' screenshots.

    # Load face encodings and timestamps from the pkl files
    known_encodings = rw_encodings(operation='load')
    face_timestamps = rw_timestamps(operation='load')
    snapshots_taken = 0 # Initialize the counter for snapshots taken

    while True: # Start scanning, run indefinitely.
        known_encodings, face_timestamps = takeSnapshot(known_encodings=known_encodings, face_timestamps=face_timestamps)
        if snapshots_taken % save_data_interval == 0:
            # Save the face encodings and timestamps to the pkl files
            rw_encodings(operation='save', encodings=known_encodings)
            rw_timestamps(operation='save', timestamps=face_timestamps)
        time.sleep(delay)

scanCamera()
