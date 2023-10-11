import cv2
from pyzbar import pyzbar
import numpy as np
from cryptography.fernet import Fernet
import pandas as pd
#import RPi.GPIO as GPIO
import time
import mysql.connector

# GPIO pin configuration
qqrelay_pin = 17  # GPIO pin for the relay
green_led_pin = 18  # GPIO pin for the green LED
red_led_pin = 23  # GPIO pin for the red LED

# Set up GPIO
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(relay_pin, GPIO.OUT)
#GPIO.setup(green_led_pin, GPIO.OUT)
#GPIO.setup(red_led_pin, GPIO.OUT)

db_config = {
    'host': 'localhost',
    'user': 'smartlock',
    'password': 'project',
    'database': 'projectQR',
    "port": 3306
}

#stay
def decryption(encrypted_data, encryption_key):
    cipher = Fernet(encryption_key)
    decryption = cipher.decrypt(encrypted_data.encode())
    return decryption.decode()

#change the unlock to gpio to push the solenoid lock and lit up the green LED for 10 secs and when locked red LED is always on
def check_data(GuestName):
    #GPIO.setmode(GPIO.BCM)
    red_led_pin = 17
    green_led_pin = 18
    relay_pin = 23
    
    # Connect to the MySQL database
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Execute the SQL query to fetch data
        query = f"SELECT * FROM GuestList WHERE GuestName = '{GuestName}'"
        cursor.execute(query)
        result = cursor.fetchall()
        
        #GPIO.setup(red_led_pin, GPIO.OUT)
        #GPIO.setup(green_led_pin, GPIO.OUT)
        #GPIO.setup(relay_pin, GPIO.OUT)
        
        if len(result) == 1:
            #GPIO.output(green_led_pin, GPIO.HIGH)  # Turn on the green LED
            #GPIO.output(red_led_pin, GPIO.LOW)
            #GPIO.output(relay_pin, GPIO.HIGH)  # Activate the solenoid diode via the relay
            time.sleep(5)  # Wait for 5 seconds
            #GPIO.output(relay_pin, GPIO.LOW)  # Deactivate the solenoid diode
            #GPIO.output(green_led_pin, GPIO.LOW)
            print("Unlock")
            return True
        else:
            #GPIO.output(red_led_pin, GPIO.HIGH)  # Turn on the red LED
            print("Access denied")
            return False
    except mysql.connector.Error as error:
        print("Error:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            #GPIO.cleanup()

#stay
def read_encryption_key(file_path): #this will take the encryption key
    with open(file_path, "rb") as key_file:
        encryption_key = key_file.read()
    return encryption_key

#stay
def scan_qr_code():
    # Initialize the webcam
    cap = cv2.VideoCapture(0)  # Use 0 for the default webcam
    
    # Set desired camera resolution
    camera_width = 640  # Set your desired width
    camera_height = 480  # Set your desired height
    cap.set(3, camera_width)  # Set width
    cap.set(4, camera_height)  # Set height
    
    # Check if the webcam is opened successfully
    if not cap.isOpened():
        print("Error: Webcam not accessible.")
        return

    # Read the encryption key from the file
    encryption_key_file_path = r"C:\Users\Terrence Serrano\OneDrive\Desktop\ETEC326\main project\key.txt"
    encryption_key = read_encryption_key(encryption_key_file_path)

    # Flag to track if QR code has been detected
    qr_code_detected = False

    while True:
    # Read frames from the webcam
        _, frame = cap.read()

        # Find and decode QR codes
        decoded_objs = pyzbar.decode(frame)

        # Display the result
        for obj in decoded_objs:
            # Extract the QR code's data and type
            data = obj.data.decode('utf-8')
            obj_type = obj.type

            # Set QR code detected flag to True
            qr_code_detected = True

            # Get the QR code's boundary points
            obj_points = obj.polygon

            # Draw a blue line around the QR code
            if len(obj_points) >= 4:
                pts = np.array(obj_points, np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (255, 0, 0), 2)
                
                # Decrypt the QR code data
                decrypted_data = decryption(data, encryption_key)

                # Check if the data exists in the database
                if decrypted_data:
                    GuestName = decrypted_data
                    check_data(GuestName)

        # Display the frame
        cv2.imshow("QR Code Scanner", frame)

        # Exit the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close windows
    cap.release()
    cv2.destroyAllWindows()

# Call the function to start scanning QR codes
scan_qr_code()

# Clean up GPIO
#GPIO.cleanup()

