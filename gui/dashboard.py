import tkinter as tk
from tkinter import ttk
import psycopg2
from tkcalendar import DateEntry

conn = psycopg2.connect(
    host="localhost",
    database="hospital",
    user="postgres",
    password="rootzenBL"
)
cur = conn.cursor()


def create_dashboard(staff_member):
    dashboard = tk.Tk()
    # dashboard.attributes("-fullscreen", True)
    dashboard.geometry("1024x768")
    dashboard.title("Menú Principal")

    # Calculate the width of the left sidebar as 25% of the window width

    # Create a frame for the left sidebar
    left_frame = tk.Frame(dashboard, width=256, bg="lightgrey")
    left_frame.place(x=0, y=0, relwidth=0.25, relheight=1)

    # Create a frame for the right content area
    right_frame = tk.Frame(dashboard)
    right_frame.place(x=257, y=0, relwidth=0.75, relheight=1)

    # Add some content to the left sidebar
    sidebar_label = tk.Label(left_frame, text="{} - {}".format(staff_member.first_name, staff_member.role),
                             font=("Arial", 16), bg="lightgrey")
    sidebar_label.pack()

    # Create a function to display data from the patients table
    def show_patients():
        # Clear the right content area
        for widget in right_frame.winfo_children():
            widget.destroy()

        # Add a label to the right content area
        content_label = tk.Label(right_frame, text="Pacientes", font=("Arial", 16))
        content_label.pack()

        # Add a treeview to display data from the patients table
        tree = ttk.Treeview(right_frame)
        tree["columns"] = ("id", "first_name", "last_name", "date_of_birth")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("id", anchor=tk.W, width=120)
        tree.column("first_name", anchor=tk.W, width=120)
        tree.column("last_name", anchor=tk.W, width=120)
        tree.column("date_of_birth", anchor=tk.CENTER, width=80)

        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("id", text="ID", anchor=tk.W)
        tree.heading("first_name", text="Nombre", anchor=tk.W)
        tree.heading("last_name", text="Apellidos", anchor=tk.W)
        tree.heading("date_of_birth", text="Fecha de Nacimiento", anchor=tk.CENTER)

        cur.execute("SELECT * FROM patients")
        rows = cur.fetchall()
        for row in rows:
            tree.insert(parent="", index="end", values=(row[0], row[1], row[2], row[3]))

        tree.pack(fill=tk.BOTH, expand=True)

        def insert_data():
            # Create a form to collect data from the user
            form = tk.Toplevel(dashboard)
            form.title("Nuevo Paciente")
            form.geometry("1024x768")

            first_name_label = tk.Label(form, text="Nombre")
            first_name_entry = tk.Entry(form)
            last_name_label = tk.Label(form, text="Apellidos")
            last_name_entry = tk.Entry(form)
            dob_label = tk.Label(form, text="Fecha de Nacimiento")
            dob_entry = DateEntry(form)
            medical_history_label = tk.Label(form, text="Historial Médico")
            medical_history_entry = tk.Text(form)

            # Pack the widgets
            first_name_label.pack()
            first_name_entry.pack()
            last_name_label.pack()
            last_name_entry.pack()
            dob_label.pack()
            dob_entry.pack()
            medical_history_label.pack()
            medical_history_entry.pack()

            # Function to insert data into the database
            def insert():
                first_name = first_name_entry.get()
                last_name = last_name_entry.get()
                dob = dob_entry.get()
                medical_history = medical_history_entry.get("1.0", "end-1c")

                # Insert data into the database
                cur.execute(
                    "INSERT INTO patients (first_name, last_name, date_of_birth, medical_history) VALUES (%s, %s, %s, %s)",
                    (first_name, last_name, dob, medical_history))

                # Commit changes to the database
                conn.commit()

                # Close the form
                form.destroy()
                show_patients()

            # Create a button to submit the data
            submit_button = tk.Button(form, text="Guardar", command=insert)
            submit_button.pack()

        # Create a function to update data in the patients table
        def update_data():
            # Get the selected item from the treeview
            selected_item = tree.selection()[0]
            patient_id = tree.item(selected_item)["values"][0]

            # Query the database for the patient's data
            cur.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
            patient = cur.fetchone()

            # Create a form to collect data from the user
            form = tk.Toplevel(dashboard)
            form.title("{} {}".format(patient[1], patient[2]))
            form.geometry("1024x768")

            first_name_label = tk.Label(form, text="Nombre")
            first_name_entry = tk.Entry(form)
            first_name_entry.insert(0, patient[1])
            last_name_label = tk.Label(form, text="Apellidos")
            last_name_entry = tk.Entry(form)
            last_name_entry.insert(0, patient[2])
            dob_label = tk.Label(form, text="Fecha de Nacimiento")
            dob_entry = DateEntry(form)
            dob_entry.set_date(patient[3])
            medical_history_label = tk.Label(form, text="Historial Médico")
            medical_history_entry = tk.Text(form)
            medical_history_entry.insert("1.0", patient[4])

            # Pack the widgets
            first_name_label.pack()
            first_name_entry.pack()
            last_name_label.pack()
            last_name_entry.pack()
            dob_label.pack()
            dob_entry.pack()
            medical_history_label.pack()
            medical_history_entry.pack()

            # Function to update data in the database
            def update():
                first_name = first_name_entry.get()
                last_name = last_name_entry.get()
                dob = dob_entry.get_date()
                medical_history = medical_history_entry.get("1.0", "end-1c")

                # Update data in the database
                cur.execute(
                    "UPDATE patients SET first_name = %s, last_name = %s, date_of_birth = %s, medical_history = %s WHERE patient_id = %s",
                    (first_name, last_name, dob, medical_history, patient_id))
                conn.commit()

                # Update the treeview
                tree.item(selected_item, values=(patient_id, first_name, last_name, dob))

                # Close the form
                form.destroy()

            # Create a button to submit the data
            submit_button = tk.Button(form, text="Guardar", command=update)
            submit_button.pack()

        # Create a function to delete data from the patients table
        def delete_data():
            # Get the selected item from the treeview
            selected_item = tree.selection()[0]
            patient_id = tree.item(selected_item)["values"][0]

            # Delete the selected patient from the database
            cur.execute("DELETE FROM patients WHERE patient_id = %s", (patient_id,))
            conn.commit()

            # Remove the selected item from the treeview
            tree.delete(selected_item)

        # Add buttons to insert, edit, and delete data from the patients table
        insert_button = tk.Button(right_frame, text="Insertar", font=("Arial", 16), command=insert_data)
        insert_button.pack(side=tk.LEFT)
        edit_button = tk.Button(right_frame, text="Editar", font=("Arial", 16), command=update_data)
        edit_button.pack(side=tk.LEFT)
        delete_button = tk.Button(right_frame, text="Eliminar", font=("Arial", 16), command=delete_data)
        delete_button.pack(side=tk.LEFT)

    def show_staff():
        # Clear the right content area
        for widget in right_frame.winfo_children():
            widget.destroy()
        # Add a label to the right content area
        content_label = tk.Label(right_frame, text="Personal", font=("Arial", 16))
        content_label.pack()

        # Add a treeview to display data from the patients table
        tree = ttk.Treeview(right_frame)
        tree["columns"] = ("id", "first_name", "last_name", "role")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("id", anchor=tk.W, width=120)
        tree.column("first_name", anchor=tk.W, width=120)
        tree.column("last_name", anchor=tk.W, width=120)
        tree.column("role", anchor=tk.CENTER, width=80)

        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("id", text="ID", anchor=tk.W)
        tree.heading("first_name", text="Nombre", anchor=tk.W)
        tree.heading("last_name", text="Apellidos", anchor=tk.W)
        tree.heading("role", text="Rol", anchor=tk.CENTER)

        cur.execute("SELECT * FROM staff")
        rows = cur.fetchall()
        for row in rows:
            tree.insert(parent="", index="end", values=(row[0], row[1], row[2], row[3]))

        tree.pack(fill=tk.BOTH, expand=True)

        def insert_data():
            # Create a form to collect data from the user
            form = tk.Toplevel(dashboard)
            form.title("Nuevo Trabajador")
            form.geometry("1024x768")

            first_name_label = tk.Label(form, text="Nombre")
            first_name_entry = tk.Entry(form)
            last_name_label = tk.Label(form, text="Apellidos")
            last_name_entry = tk.Entry(form)
            dob_label = tk.Label(form, text="Rol")
            dob_entry = tk.Entry(form)
            medical_history_label = tk.Label(form, text="Contraseña")
            medical_history_entry = tk.Entry(form)

            # Pack the widgets
            first_name_label.pack()
            first_name_entry.pack()
            last_name_label.pack()
            last_name_entry.pack()
            dob_label.pack()
            dob_entry.pack()
            medical_history_label.pack()
            medical_history_entry.pack()

            # Function to insert data into the database
            def insert():
                first_name = first_name_entry.get()
                last_name = last_name_entry.get()
                dob = dob_entry.get()
                medical_history = medical_history_entry.get()

                # Insert data into the database
                cur.execute(
                    "INSERT INTO staff (first_name, last_name, role, password) VALUES (%s, %s, %s, %s)",
                    (first_name, last_name, dob, medical_history))

                # Commit changes to the database
                conn.commit()

                # Close the form
                form.destroy()
                show_staff()

            # Create a button to submit the data
            submit_button = tk.Button(form, text="Guardar", command=insert)
            submit_button.pack()

        # Create a function to update data in the patients table
        def update_data():
            # Get the selected item from the treeview
            selected_item = tree.selection()[0]
            patient_id = tree.item(selected_item)["values"][0]

            # Query the database for the patient's data
            cur.execute("SELECT * FROM staff WHERE staff_id = %s", (patient_id,))
            patient = cur.fetchone()

            # Create a form to collect data from the user
            form = tk.Toplevel(dashboard)
            form.title("{} {}".format(patient[1], patient[3]))
            form.geometry("1024x768")

            first_name_label = tk.Label(form, text="Nombre")
            first_name_entry = tk.Entry(form)
            first_name_entry.insert(0, patient[1])
            last_name_label = tk.Label(form, text="Apellidos")
            last_name_entry = tk.Entry(form)
            last_name_entry.insert(0, patient[2])
            dob_label = tk.Label(form, text="Rol")
            dob_entry = tk.Entry(form)
            dob_entry.insert(0, patient[3])
            medical_history_label = tk.Label(form, text="Contraseña")
            medical_history_entry = tk.Entry(form)
            medical_history_entry.insert(0, patient[4])

            # Pack the widgets
            first_name_label.pack()
            first_name_entry.pack()
            last_name_label.pack()
            last_name_entry.pack()
            dob_label.pack()
            dob_entry.pack()
            medical_history_label.pack()
            medical_history_entry.pack()

            # Function to update data in the database
            def update():
                first_name = first_name_entry.get()
                last_name = last_name_entry.get()
                dob = dob_entry.get()
                medical_history = medical_history_entry.get()

                # Update data in the database
                cur.execute(
                    "UPDATE staff SET first_name = %s, last_name = %s, role = %s, password = %s WHERE staff_id = %s",
                    (first_name, last_name, dob, medical_history, patient_id))
                conn.commit()

                # Update the treeview
                tree.item(selected_item, values=(patient_id, first_name, last_name, dob))

                # Close the form
                form.destroy()

            # Create a button to submit the data
            submit_button = tk.Button(form, text="Guardar", command=update)
            submit_button.pack()

        # Create a function to delete data from the patients table
        def delete_data():
            # Get the selected item from the treeview
            selected_item = tree.selection()[0]
            patient_id = tree.item(selected_item)["values"][0]

            # Delete the selected staff member from the database
            cur.execute("DELETE FROM staff WHERE staff_id = %s", (patient_id,))
            conn.commit()

            # Remove the selected item from the treeview
            tree.delete(selected_item)

        # Add buttons to insert, edit, and delete data from the patients table
        insert_button = tk.Button(right_frame, text="Insertar", font=("Arial", 16), command=insert_data)
        insert_button.pack(side=tk.LEFT)
        edit_button = tk.Button(right_frame, text="Editar", font=("Arial", 16), command=update_data)
        edit_button.pack(side=tk.LEFT)
        delete_button = tk.Button(right_frame, text="Eliminar", font=("Arial", 16), command=delete_data)
        delete_button.pack(side=tk.LEFT)

    def show_appointments():
        # Clear the right content area
        for widget in right_frame.winfo_children():
            widget.destroy()

        # Add a label to the right content area
        content_label = tk.Label(right_frame, text="Citas", font=("Arial", 16))
        content_label.pack()

        # Add a treeview to display data from the patients table
        tree = ttk.Treeview(right_frame)
        tree["columns"] = ("id", "patient", "staff", "date", "type")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("id", anchor=tk.W, width=120)
        tree.column("patient", anchor=tk.W, width=120)
        tree.column("staff", anchor=tk.W, width=120)
        tree.column("date", anchor=tk.W, width=120)
        tree.column("type", anchor=tk.CENTER, width=120)

        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("id", text="ID", anchor=tk.W)
        tree.heading("patient", text="Paciente", anchor=tk.W)
        tree.heading("staff", text="Personal Médico", anchor=tk.W)
        tree.heading("date", text="Fecha", anchor=tk.W)
        tree.heading("type", text="Tipo", anchor=tk.CENTER)

        cur.execute("SELECT * FROM appointments")
        rows = cur.fetchall()
        for row in rows:
            tree.insert(parent="", index="end", values=(row[0], row[1], row[2], row[3], row[4]))

        tree.pack(fill=tk.BOTH, expand=True)

        def insert_data():
            # Create a form to collect data from the user
            form = tk.Toplevel(dashboard)
            form.title("Nueva Cita")
            form.geometry("400x400")

            # Query the database for the list of patients and staff members
            cur.execute("SELECT patient_id, first_name, last_name FROM patients")
            patients = cur.fetchall()
            cur.execute("SELECT staff_id, first_name, last_name FROM staff WHERE role='Médico' OR role='Enfermero'")
            staff = cur.fetchall()

            patient_label = tk.Label(form, text="Paciente")
            patient_entry = ttk.Combobox(form,
                                         values=[f"{patient[0]}: {patient[1]} {patient[2]}" for patient in patients])
            staff_label = tk.Label(form, text="Personal")
            staff_entry = ttk.Combobox(form, values=[f"{staff_member[0]}: {staff_member[1]} {staff_member[2]}" for
                                                     staff_member in staff])
            date_label = tk.Label(form, text="Fecha")
            date_entry = DateEntry(form)
            type_label = tk.Label(form, text="Tipo")
            type_entry = tk.Entry(form)

            # Pack the widgets
            patient_label.pack()
            patient_entry.pack()
            staff_label.pack()
            staff_entry.pack()
            date_label.pack()
            date_entry.pack()
            type_label.pack()
            type_entry.pack()

            # Function to insert data into the database
            def insert():
                patient_id = patient_entry.get().split(":")[0]
                staff_id = staff_entry.get().split(":")[0]
                appointment_date = date_entry.get_date()
                appointment_type = type_entry.get()

                # Insert data into the database
                cur.execute(
                    "INSERT INTO appointments (patient_id, staff_id, appointment_date, appointment_type) VALUES (%s, %s, %s, %s)",
                    (patient_id, staff_id, appointment_date, appointment_type))
                conn.commit()

                # Close the form
                form.destroy()

            # Create a button to submit the data
            submit_button = tk.Button(form, text="Guardar", command=insert)
            submit_button.pack()
            show_appointments()

        def update_data():
            # Get the selected item from the treeview
            selected_item = tree.selection()[0]
            appointment_id = tree.item(selected_item)["values"][0]

            # Query the database for the appointment's data
            cur.execute("SELECT * FROM appointments WHERE appointment_id = %s", (appointment_id,))
            appointment = cur.fetchone()

            # Query the database for the list of patients and staff members
            cur.execute("SELECT patient_id, first_name, last_name FROM patients")
            patients = cur.fetchall()
            cur.execute("SELECT staff_id, first_name, last_name FROM staff WHERE role='Médico' OR role='Enfermero'")
            staff = cur.fetchall()

            # Create a form to collect data from the user
            form = tk.Toplevel(dashboard)
            form.title("Editar Cita")
            form.geometry("400x400")

            patient_label = tk.Label(form, text="paciente")
            patient_entry = ttk.Combobox(form,
                                         values=[f"{patient[0]}: {patient[1]} {patient[2]}" for patient in patients])
            patient_entry.set(
                f"{appointment[1]}: {[f'{patient[1]} {patient[2]}' for patient in patients if patient[0] == appointment[1]][0]}")
            staff_label = tk.Label(form, text="Personal Médico")
            staff_entry = ttk.Combobox(form, values=[f"{staff_member[0]}: {staff_member[1]} {staff_member[2]}" for
                                                     staff_member in staff])
            staff_entry.set(
                f"{appointment[2]}: {[f'{staff_member[1]} {staff_member[2]}' for staff_member in staff if staff_member[0] == appointment[2]][0]}")
            date_label = tk.Label(form, text="Fecha")
            date_entry = DateEntry(form)
            date_entry.set_date(appointment[3])
            type_label = tk.Label(form, text="Tipo")
            type_entry = tk.Entry(form)
            type_entry.insert(0, appointment[4])

            # Pack the widgets
            patient_label.pack()
            patient_entry.pack()
            staff_label.pack()
            staff_entry.pack()
            date_label.pack()
            date_entry.pack()
            type_label.pack()
            type_entry.pack()

            # Function to update data in the database
            def update():
                patient_id = patient_entry.get().split(":")[0]
                staff_id = staff_entry.get().split(":")[0]
                appointment_date = date_entry.get_date()
                appointment_type = type_entry.get()

                # Update data in the database
                cur.execute(
                    "UPDATE appointments SET patient_id = %s, staff_id = %s, appointment_date = %s, appointment_type = %s WHERE appointment_id = %s",
                    (patient_id, staff_id, appointment_date, appointment_type, appointment_id))
                conn.commit()

                # Update the treeview
                tree.item(selected_item, values=(
                    appointment_id, patient_id, staff_id, appointment_date.strftime("%Y-%m-%d"), appointment_type))

                # Close the form
                form.destroy()

            # Create a button to submit the data
            submit_button = tk.Button(form, text="Guardar", command=update)
            submit_button.pack()

        def delete_data():
            # Get the selected item from the treeview
            selected_item = tree.selection()[0]
            patient_id = tree.item(selected_item)["values"][0]

            # Delete the selected appointment from the database
            cur.execute("DELETE FROM appointments WHERE appointment_id = %s", (patient_id,))
            conn.commit()

            # Remove the selected item from the treeview
            tree.delete(selected_item)

        # Add buttons to insert, edit, and delete data from the patients table
        insert_button = tk.Button(right_frame, text="Insertar", font=("Arial", 16), command=insert_data)
        insert_button.pack(side=tk.LEFT)
        edit_button = tk.Button(right_frame, text="Editar", font=("Arial", 16), command=update_data)
        edit_button.pack(side=tk.LEFT)
        delete_button = tk.Button(right_frame, text="Eliminar", font=("Arial", 16), command=delete_data)
        delete_button.pack(side=tk.LEFT)

    def show_tests():
        # Clear the right content area
        for widget in right_frame.winfo_children():
            widget.destroy()

        # Add a label to the right content area
        content_label = tk.Label(right_frame, text="Pruebas", font=("Arial", 16))
        content_label.pack()

        # Add a treeview to display data from the patients table
        tree = ttk.Treeview(right_frame)
        tree["columns"] = ("id", "patient", "type", "date", "results")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("id", anchor=tk.W, width=120)
        tree.column("patient", anchor=tk.W, width=120)
        tree.column("type", anchor=tk.W, width=120)
        tree.column("date", anchor=tk.W, width=120)
        tree.column("results", anchor=tk.CENTER, width=120)

        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("id", text="ID", anchor=tk.W)
        tree.heading("patient", text="Paciente", anchor=tk.W)
        tree.heading("type", text="Tipo", anchor=tk.W)
        tree.heading("date", text="Fecha", anchor=tk.W)
        tree.heading("results", text="Resultados", anchor=tk.CENTER)

        cur.execute("SELECT * FROM tests")
        rows = cur.fetchall()
        for row in rows:
            tree.insert(parent="", index="end", values=(row[0], row[1], row[2], row[3], row[4]))

        tree.pack(fill=tk.BOTH, expand=True)

        def insert_data():
            # Create a form to collect data from the user
            form = tk.Toplevel(dashboard)
            form.title("Nueva Prueba")
            form.geometry("1024x768")

            # Query the database for the list of patients
            cur.execute("SELECT patient_id, first_name, last_name FROM patients")
            patients = cur.fetchall()

            patient_label = tk.Label(form, text="Paciente")
            patient_entry = ttk.Combobox(form,
                                         values=[f"{patient[0]}: {patient[1]} {patient[2]}" for patient in patients])
            type_label = tk.Label(form, text="Tipo")
            type_entry = tk.Entry(form)
            date_label = tk.Label(form, text="Fecha")
            date_entry = DateEntry(form)
            results_label = tk.Label(form, text="Resultados")
            results_entry = tk.Text(form)

            # Pack the widgets
            patient_label.pack()
            patient_entry.pack()
            type_label.pack()
            type_entry.pack()
            date_label.pack()
            date_entry.pack()
            results_label.pack()
            results_entry.pack()

            # Function to insert data into the database
            def insert():
                patient_id = patient_entry.get().split(":")[0]
                test_type = type_entry.get()
                test_date = date_entry.get_date()
                test_results = results_entry.get("1.0", "end-1c")

                # Insert data into the database
                cur.execute(
                    "INSERT INTO tests (patient_id, test_type, test_date, test_results) VALUES (%s, %s, %s, %s)",
                    (patient_id, test_type, test_date, test_results))
                conn.commit()

                # Close the form
                form.destroy()
                show_tests()

            # Create a button to submit the data
            submit_button = tk.Button(form, text="Guardar", command=insert)
            submit_button.pack()

        def update_data():
            # Get the selected item from the treeview
            selected_item = tree.selection()[0]
            test_id = tree.item(selected_item)["values"][0]

            # Query the database for the test's data
            cur.execute("SELECT * FROM tests WHERE test_id = %s", (test_id,))
            test = cur.fetchone()

            # Query the database for the list of patients
            cur.execute("SELECT patient_id, first_name, last_name FROM patients")
            patients = cur.fetchall()

            # Create a form to collect data from the user
            form = tk.Toplevel(dashboard)
            form.title("Editar Prueba")
            form.geometry("1024x768")

            patient_label = tk.Label(form, text="Paciente")
            patient_entry = ttk.Combobox(form,
                                         values=[f"{patient[0]}: {patient[1]} {patient[2]}" for patient in patients])
            patient_entry.set(
                f"{test[1]}: {[f'{patient[1]} {patient[2]}' for patient in patients if patient[0] == test[1]][0]}")
            type_label = tk.Label(form, text="Tipo")
            type_entry = tk.Entry(form)
            type_entry.insert(0, test[2])
            date_label = tk.Label(form, text="Fecha")
            date_entry = DateEntry(form)
            date_entry.set_date(test[3])
            results_label = tk.Label(form, text="Resultados")
            results_entry = tk.Text(form)
            results_entry.insert("1.0", test[4])

            # Pack the widgets
            patient_label.pack()
            patient_entry.pack()
            type_label.pack()
            type_entry.pack()
            date_label.pack()
            date_entry.pack()
            results_label.pack()
            results_entry.pack()

            # Function to update data in the database
            def update():
                patient_id = patient_entry.get().split(":")[0]
                test_type = type_entry.get()
                test_date = date_entry.get_date()
                test_results = results_entry.get("1.0", "end-1c")

                # Update data in the database
                cur.execute(
                    "UPDATE tests SET patient_id = %s, test_type = %s, test_date = %s, test_results = %s WHERE test_id = %s",
                    (patient_id, test_type, test_date, test_results, test_id))
                conn.commit()

                # Update the treeview
                tree.item(selected_item,
                          values=(test_id, patient_id, test_type, test_date.strftime("%Y-%m-%d"), test_results))

                # Close the form
                form.destroy()

            # Create a button to submit the data
            submit_button = tk.Button(form, text="Guardar", command=update)
            submit_button.pack()

        def delete_data():
            # Get the selected item from the treeview
            selected_item = tree.selection()[0]
            patient_id = tree.item(selected_item)["values"][0]

            # Delete the selected test from the database
            cur.execute("DELETE FROM tests WHERE test_id = %s", (patient_id,))
            conn.commit()

            # Remove the selected item from the treeview
            tree.delete(selected_item)

        # Add buttons to insert, edit, and delete data from the patients table
        insert_button = tk.Button(right_frame, text="Insertar", font=("Arial", 16), command=insert_data)
        insert_button.pack(side=tk.LEFT)
        edit_button = tk.Button(right_frame, text="Editar", font=("Arial", 16), command=update_data)
        edit_button.pack(side=tk.LEFT)
        delete_button = tk.Button(right_frame, text="Eliminar", font=("Arial", 16), command=delete_data)
        delete_button.pack(side=tk.LEFT)

    def show_treatments():
        # Clear the right content area
        for widget in right_frame.winfo_children():
            widget.destroy()

        # Add a label to the right content area
        content_label = tk.Label(right_frame, text="Tratamientos", font=("Arial", 16))
        content_label.pack()

        # Add a treeview to display data from the patients table
        tree = ttk.Treeview(right_frame)
        tree["columns"] = ("id", "patient", "type", "date")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("id", anchor=tk.W, width=120)
        tree.column("patient", anchor=tk.W, width=120)
        tree.column("type", anchor=tk.W, width=120)
        tree.column("date", anchor=tk.CENTER, width=120)

        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("id", text="ID", anchor=tk.W)
        tree.heading("patient", text="Paciente", anchor=tk.W)
        tree.heading("type", text="Personal Médico", anchor=tk.W)
        tree.heading("date", text="Tipo", anchor=tk.CENTER)

        cur.execute("SELECT * FROM treatments")
        rows = cur.fetchall()
        for row in rows:
            tree.insert(parent="", index="end", values=(row[0], row[1], row[2], row[3]))

        tree.pack(fill=tk.BOTH, expand=True)

        def insert_data():
            # Create a form to collect data from the user
            form = tk.Toplevel(dashboard)
            form.title("Nuevo Tratamiento")
            form.geometry("800x400")

            # Query the database for the list of patients
            cur.execute("SELECT patient_id, first_name, last_name FROM patients")
            patients = cur.fetchall()

            patient_label = tk.Label(form, text="Paciente")
            patient_entry = ttk.Combobox(form,
                                         values=[f"{patient[0]}: {patient[1]} {patient[2]}" for patient in patients])
            type_label = tk.Label(form, text="Tipo")
            type_entry = tk.Entry(form)
            date_label = tk.Label(form, text="Fecha")
            date_entry = DateEntry(form)

            # Pack the widgets
            patient_label.pack()
            patient_entry.pack()
            type_label.pack()
            type_entry.pack()
            date_label.pack()
            date_entry.pack()

            # Function to insert data into the database
            def insert():
                patient_id = patient_entry.get().split(":")[0]
                treatment_type = type_entry.get()
                treatment_date = date_entry.get_date()

                # Insert data into the database
                cur.execute("INSERT INTO treatments (patient_id, treatment_type, treatment_date) VALUES (%s, %s, %s)",
                            (patient_id, treatment_type, treatment_date))
                conn.commit()

                # Close the form
                form.destroy()
                show_treatments()

            # Create a button to submit the data
            submit_button = tk.Button(form, text="Guardar", command=insert)
            submit_button.pack()

        def update_data():
            # Get the selected item from the treeview
            selected_item = tree.selection()[0]
            treatment_id = tree.item(selected_item)["values"][0]

            # Query the database for the treatment's data
            cur.execute("SELECT * FROM treatments WHERE treatment_id = %s", (treatment_id,))
            treatment = cur.fetchone()

            # Query the database for the list of patients
            cur.execute("SELECT patient_id, first_name, last_name FROM patients")
            patients = cur.fetchall()

            # Create a form to collect data from the user
            form = tk.Toplevel(dashboard)
            form.title("Editar Tratamiento")
            form.geometry("800x400")

            patient_label = tk.Label(form, text="Paciente")
            patient_entry = ttk.Combobox(form,
                                         values=[f"{patient[0]}: {patient[1]} {patient[2]}" for patient in patients])
            patient_entry.set(
                f"{treatment[1]}: {[f'{patient[1]} {patient[2]}' for patient in patients if patient[0] == treatment[1]][0]}")
            type_label = tk.Label(form, text="Tipo")
            type_entry = tk.Entry(form)
            type_entry.insert(0, treatment[2])
            date_label = tk.Label(form, text="Fecha")
            date_entry = DateEntry(form)
            date_entry.set_date(treatment[3])

            # Pack the widgets
            patient_label.pack()
            patient_entry.pack()
            type_label.pack()
            type_entry.pack()
            date_label.pack()
            date_entry.pack()

            # Function to update data in the database
            def update():
                patient_id = patient_entry.get().split(":")[0]
                treatment_type = type_entry.get()
                treatment_date = date_entry.get_date()

                # Update data in the database
                cur.execute(
                    "UPDATE treatments SET patient_id = %s, treatment_type = %s, treatment_date = %s WHERE treatment_id = %s",
                    (patient_id, treatment_type, treatment_date, treatment_id))
                conn.commit()

                # Update the treeview
                tree.item(selected_item,
                          values=(treatment_id, patient_id, treatment_type, treatment_date.strftime("%Y-%m-%d")))

                # Close the form
                form.destroy()

            # Create a button to submit the data
            submit_button = tk.Button(form, text="Guardar", command=update)
            submit_button.pack()

        def delete_data():
            # Get the selected item from the treeview
            selected_item = tree.selection()[0]
            patient_id = tree.item(selected_item)["values"][0]

            # Delete the selected treatment from the database
            cur.execute("DELETE FROM treatments WHERE treatment_id = %s", (patient_id,))
            conn.commit()

            # Remove the selected item from the treeview
            tree.delete(selected_item)

        # Add buttons to insert, edit, and delete data from the patients table
        insert_button = tk.Button(right_frame, text="Insertar", font=("Arial", 16), command=insert_data)
        insert_button.pack(side=tk.LEFT)
        edit_button = tk.Button(right_frame, text="Editar", font=("Arial", 16), command=update_data)
        edit_button.pack(side=tk.LEFT)
        delete_button = tk.Button(right_frame, text="Eliminar", font=("Arial", 16), command=delete_data)
        delete_button.pack(side=tk.LEFT)

    def show_resources():
        # Clear the right content area
        for widget in right_frame.winfo_children():
            widget.destroy()

        # Add a label to the right content area
        content_label = tk.Label(right_frame, text="Recursos del Hospital", font=("Arial", 16))
        content_label.pack()

        # Add a treeview to display data from the patients table
        tree = ttk.Treeview(right_frame)
        tree["columns"] = ("id", "type", "name")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("id", anchor=tk.W, width=120)
        tree.column("type", anchor=tk.W, width=120)
        tree.column("name", anchor=tk.CENTER, width=120)

        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("id", text="ID", anchor=tk.W)
        tree.heading("type", text="Tipo", anchor=tk.W)
        tree.heading("name", text="Nombre", anchor=tk.CENTER)

        cur.execute("SELECT * FROM resources")
        rows = cur.fetchall()
        for row in rows:
            tree.insert(parent="", index="end", values=(row[0], row[1], row[2]))

        tree.pack(fill=tk.BOTH, expand=True)

        def insert_data():
            # Create a form to collect data from the user
            form = tk.Toplevel(dashboard)
            form.title("Nuevo Recurso")
            form.geometry("600x400")

            type_label = tk.Label(form, text="Tipo")
            type_entry = tk.Entry(form)
            name_label = tk.Label(form, text="Nombre")
            name_entry = tk.Entry(form)

            # Pack the widgets
            type_label.pack()
            type_entry.pack()
            name_label.pack()
            name_entry.pack()

            # Function to insert data into the database
            def insert():
                resource_type = type_entry.get()
                resource_name = name_entry.get()

                # Insert data into the database
                cur.execute("INSERT INTO resources (resource_type, resource_name) VALUES (%s, %s)",
                            (resource_type, resource_name))
                conn.commit()

                # Close the form
                form.destroy()
                show_resources()

            # Create a button to submit the data
            submit_button = tk.Button(form, text="Submit", command=insert)
            submit_button.pack()

        def update_data():
            # Get the selected item from the treeview
            selected_item = tree.selection()[0]
            resource_id = tree.item(selected_item)["values"][0]

            # Query the database for the resource's data
            cur.execute("SELECT * FROM resources WHERE resource_id = %s", (resource_id,))
            resource = cur.fetchone()

            # Create a form to collect data from the user
            form = tk.Toplevel(dashboard)
            form.title("Editar Recurso")
            form.geometry("600x400")

            type_label = tk.Label(form, text="Tipo")
            type_entry = tk.Entry(form)
            type_entry.insert(0, resource[1])
            name_label = tk.Label(form, text="Nombre")
            name_entry = tk.Entry(form)
            name_entry.insert(0, resource[2])

            # Pack the widgets
            type_label.pack()
            type_entry.pack()
            name_label.pack()
            name_entry.pack()

            # Function to update data in the database
            def update():
                resource_type = type_entry.get()
                resource_name = name_entry.get()

                # Update data in the database
                cur.execute("UPDATE resources SET resource_type = %s, resource_name = %s WHERE resource_id = %s",
                            (resource_type, resource_name, resource_id))
                conn.commit()

                # Update the treeview
                tree.item(selected_item, values=(resource_id, resource_type, resource_name))

                # Close the form
                form.destroy()

            # Create a button to submit the data
            submit_button = tk.Button(form, text="Guardar", command=update)
            submit_button.pack()

        def delete_data():
            # Get the selected item from the treeview
            selected_item = tree.selection()[0]
            patient_id = tree.item(selected_item)["values"][0]

            # Delete the selected resource from the database
            cur.execute("DELETE FROM resources WHERE resource_id = %s", (patient_id,))
            conn.commit()

            # Remove the selected item from the treeview
            tree.delete(selected_item)

        # Add buttons to insert, edit, and delete data from the patients table
        insert_button = tk.Button(right_frame, text="Insertar", font=("Arial", 16), command=insert_data)
        insert_button.pack(side=tk.LEFT)
        edit_button = tk.Button(right_frame, text="Editar", font=("Arial", 16), command=update_data)
        edit_button.pack(side=tk.LEFT)
        delete_button = tk.Button(right_frame, text="Eliminar", font=("Arial", 16), command=delete_data)
        delete_button.pack(side=tk.LEFT)

    # Add a button to manage the patients table
    if staff_member.role == "Médico" or staff_member.role == "Enfermero":
        patients_button = tk.Button(left_frame, text="Pacientes", font=("Arial", 16), command=show_patients)
        patients_button.pack(fill=tk.X)
        tests_button = tk.Button(left_frame, text="Pruebas Médicas", font=("Arial", 16), command=show_tests)
        tests_button.pack(fill=tk.X)
        treatments_button = tk.Button(left_frame, text="Tratamientos", font=("Arial", 16), command=show_treatments)
        treatments_button.pack(fill=tk.X)
    elif staff_member.role == "Administrador":
        appointments_button = tk.Button(left_frame, text="Citas", font=("Arial", 16), command=show_appointments)
        appointments_button.pack(fill=tk.X)
        resources_button = tk.Button(left_frame, text="Recursos del Hospital", font=("Arial", 16),
                                     command=show_resources)
        resources_button.pack(fill=tk.X)
    elif staff_member.role == "SuperUser":
        staff_button = tk.Button(left_frame, text="Personal", font=("Arial", 16), command=show_staff)
        staff_button.pack(fill=tk.X)
    dashboard.mainloop()
    cur.close()
    conn.close()
