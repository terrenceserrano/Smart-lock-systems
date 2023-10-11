
#this is the software framework for the project hotel

#libraries used
import qrcode #qrcode generation
from cryptography.fernet import Fernet #this is for the encryption
import smtplib #this is for mail transfer
import imghdr
import pandas as pd
import mysql.connector
import time

from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

# Function to insert data into the MySQL database
def insert_data():
    try:
        # Establish a connection to the MySQL server
        db_connection = mysql.connector.connect(
            host="localhost",
            user="smartlock",
            password="project",
            database="projectQR",
            port=3306
        )

        # Create a cursor to execute SQL queries
        cursor = db_connection.cursor()

        # Retrieve guest information from user input
        GuestName = input("Name of Guest: ")
        EmailID = input("Email of guest: ")
        RoomNo = input("Room number: ")

        # Prepare the SQL query to insert data into the table
        query = "INSERT INTO GuestList (GuestName, EmailID, RoomNo) VALUES (%s, %s, %s)"
        params = (GuestName, EmailID, RoomNo)

        # Execute the query to insert data
        cursor.execute(query, params)

        # Commit the changes to the database
        db_connection.commit()

        print("Data inserted successfully into the database.")

    except Exception as e:
        print("Error occurred while inserting data into the database: ", e)
    finally:
        # Close the cursor and database connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            db_connection.close()


def check_data(GuestName, EmailID):
    
    try:
        # Establish a connection to the MySQL server
        db_connection = mysql.connector.connect(
            host="localhost",
            user="smartlock",
            password="project",
            database="projectQR",
            port=3306
        )

        # Create a cursor to execute SQL queries
        cursor = db_connection.cursor()

        # Prepare the SQL query to fetch data from the table
        query = "SELECT * FROM GuestList WHERE GuestName = %s AND EmailID = %s"
        params = (GuestName, EmailID)

        # Execute the query
        cursor.execute(query, params)
        result = cursor.fetchall()

        # Check if the filtered data exists
        if result:
            print("Guest: " + GuestName + " with the email of: " + EmailID)
            return True
        else:
            print("No data found in database")
            return False

    except Exception as e:
        print("Error occurred while checking data in the database: ", e)
    finally:
        # Close the cursor and database connection
        cursor.close()
        db_connection.close()

# Call the function to check data in the database without prompts
#Guest = "John Doe"  # Replace with the actual guest name
#Email = "john.doe@example.com"  # Replace with the actual guest email
#check_data(Guest, Email)
    
def qr(): #generation of the encrypted qr code
    # Define the file path where to save the QR code image
    save_path = r"C:\Users\Terrence Serrano\OneDrive\Desktop\ETEC326\main project\qrcode.png"
    
    
    # Generate the encryption key
    encryption_key = Fernet.generate_key()

    # Data to encrypt and store in the QR code, this will also be the data for the scanning process
    data = GuestName #this will be the argument for the scanner(image)

    # Create a Fernet cipher instance
    cipher = Fernet(encryption_key)

    # Encrypt the data
    encrypted_data = cipher.encrypt(data.encode())

    # Generate the QR code image
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
    qr.add_data(encrypted_data)
    qr.make(fit=True)

    # Create an image from the QR code data
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # Save the QR code image to the specified file path
    qr_image.save(save_path)

    # Store the encryption key for later decryption
    key_file_path = r"C:\Users\Terrence Serrano\OneDrive\Desktop\ETEC326\main project\key.txt"
    with open(key_file_path, "wb") as key_file:
        key_file.write(encryption_key)

    # Print the file paths where the QR code image and encryption key are saved
    print("QR code image saved at:", save_path)
    print("Encryption key saved at:", key_file_path)

    # Establish a connection to the MySQL server
    db_connection = mysql.connector.connect(
        host="localhost",
        user="smartlock",
        password="project",
        database="projectQR"
    )

    # Create a cursor to execute SQL queries
    cursor = db_connection.cursor()

    # Generate or modify the QR code and key files and get their paths
    qr_code_path = r"C:\Users\Terrence Serrano\OneDrive\Desktop\ETEC326\main project\qrcode.png"
    key_path = r"C:\Users\Terrence Serrano\OneDrive\Desktop\ETEC326\main project\key.txt"

    # Insert the file paths into the database
    sql = "INSERT INTO Security (QR_path, Key_path) VALUES (%s, %s)"
    values = (qr_code_path, key_path)
    cursor.execute(sql, values)

    # Commit the changes to the database
    db_connection.commit()

    # Close the database connection
    db_connection.close()
    
def email(): #This is for the sending the qr code to the email
    #this is for the email configuration
    sender = 'projecthoteltrial@gmail.com'
    password = 'iedtzhjlsmiwaxbu' #secure apps password
    receiver = EmailID
    subject = ' Here is your QR card '+ GuestName +' enjoy your stay!' #this is for the simulation of the QR card sent
    message = 'Your room is: '+ Room +' enjoy your stay!'

    #create a multipart email, this is for the structure of the mail
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject

    #attaching the qr code to the email body
    with open(r"C:\Users\Terrence Serrano\OneDrive\Desktop\ETEC326\main project\qrcode.png", 'rb') as f:
        file_data = f.read()
        file_type = imghdr.what(f.name)
        file_name = f.name
    
    image_attachment = MIMEImage(file_data, name = file_name)
    msg.attach(image_attachment)

    #attaching the email to the multipart object, this is a crucial part for the connection
    msg.attach(MIMEText(message, 'plain'))

    #this is for connecting to SMTP servers
    try:
        #creating a secure connection with the SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls() #never forget the () for this is a function

        #checking of gmail account
        app_password = 'iedtzhjlsmiwaxbu'
        server.login(sender,password)

        #sending the mail
        server.sendmail(sender, receiver, msg.as_string())
        print("Email sent successfully")

    except Exception as e:
        print("Something went wrong when sending the email: ")
    finally:
        #closing the connection
        server.quit() 

def resend(): #this is the function that will send another qr code every 5 mins
    while True:
        GuestName = GuestName
        EmailID = EmailID
        
        if check_data(GuestName, EmailID): #this will take the data of the verified user
            Room = Room
            verify = "yes" #this will skip the verification process
            
            if verify.lower() in ['yes', 'y']:
                qr()
                email()
                time.sleep(30)
            else:
                print("Please Verify")
        
        
# Flow for the system to verify and send QR details to email
while True:    
    # Call the function to insert data into the database
    insert_data()
    #this is for the verification of the reception
    GuestName = input("Name of Guest: ")
    EmailID = input("Email of guest: ") 
    
    if check_data(GuestName, EmailID):  # Pass the Guest and Email to check_data function
        Room = input("Room number: ")
        verify = input("Did you verify the guest with ID or passport?: ")
        if verify.lower() in ['yes', 'y']:
            qr()  # This will generate the initial qr code
            email()  # This will send the qr code to the guest               
        else:
            print('Please verify')


