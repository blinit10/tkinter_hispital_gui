import tkinter as tk
import psycopg2
from tkinter import messagebox

from gui.dashboard import create_dashboard
from models.user import Staff

# Connect to the hospital management database
conn = psycopg2.connect(
    host="localhost",
    database="hospital",
    user="postgres",
    password="rootzenBL"
)
cur = conn.cursor()


# Create the main window
root = tk.Tk()
root.title("Hospital Hermanos Ameijeiras")
root.geometry("400x400")

# Create a frame for the username label and entry
username_frame = tk.Frame(root)
username_frame.pack(pady=10)

# Create a label and entry for the username
username_label = tk.Label(username_frame, text="Nombre", font=("Arial", 16))
username_label.pack(side=tk.LEFT, padx=10)
username_entry = tk.Entry(username_frame, font=("Arial", 16))
username_entry.pack(side=tk.LEFT, padx=10)

# Create a frame for the password label and entry
password_frame = tk.Frame(root)
password_frame.pack(pady=10)

# Create a label and entry for the password
password_label = tk.Label(password_frame, text="Contraseña", font=("Arial", 16))
password_label.pack(side=tk.LEFT, padx=10)
password_entry = tk.Entry(password_frame, show="*", font=("Arial", 16))
password_entry.pack(side=tk.LEFT, padx=10)

# Create a function to check the username and password
def login():
    cur.execute(
        "SELECT * FROM staff WHERE first_name = %s AND password = %s",
        (username_entry.get(), password_entry.get())
    )
    staff_member_row = cur.fetchone()
    if staff_member_row is not None:
        # If the username and password are correct, close the login window and display the dashboard
        staff_member = Staff(staff_member_row[0], staff_member_row[1], staff_member_row[2], staff_member_row[3], staff_member_row[4])
        cur.close()
        conn.close()
        root.destroy()
        create_dashboard(staff_member)
    else:
        # If the username or password is incorrect, display an error message
        messagebox.showerror("Error", "Credenciales Incorrectas")

# Create a button to log in
login_button = tk.Button(root, text="Autenticar", command=login, font=("Arial", 16))
login_button.pack(pady=10)
# Close the database connection


# Run the main loop
root.mainloop()


