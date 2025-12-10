import customtkinter as ctk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import mysql.connector
import os
import sys
import re 

ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")

if len(sys.argv) > 4:
    USER_ROLE = sys.argv[1]
    USER_ID = sys.argv[2]
    DB_NAME = sys.argv[3]
    DB_PASS = sys.argv[4]
else:
    USER_ROLE = "super_admin"
    USER_ID = "1"
    DB_NAME = "attendance_db_final"
    DB_PASS = "Kaurgill@4343#1"

class Student(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        
        self.title("Student Management System")
        self.geometry("1300x750")
        self.after(0, lambda: self.state('zoomed')) 
       
        try:
            icon_path = os.path.abspath("images/app_icon.ico")
            self.iconbitmap(icon_path)
            self.after(200, lambda: self.iconbitmap(icon_path))
        except: pass

        
        self.COLOR_PRIMARY = "#0A2647"
        self.COLOR_SOFT = "#F5F7F9"
        
        self.db_config = {
            "host": "localhost",
            "user": "root",
            "password": DB_PASS,
            "database": DB_NAME
        }

        # capture variables
        self.cap = None  
        self.is_camera_on = False
        self.current_frame_clean = None 
        
        try:
            self.face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        except: pass

        # mapping departments to courses
        self.dept_course_map = {
            "CSE": ["B.Tech", "M.Tech", "BCA", "Diploma"],
            "IT": ["B.Tech", "M.Tech", "BCA"],
            "Civil": ["B.Tech", "Diploma"],
            "Mechanical": ["B.Tech", "Diploma"],
            "Commerce": ["B.Com", "BBA", "MBA"],
            "Arts": ["B.A", "M.A"]
        }
        self.dept_list = list(self.dept_course_map.keys())

        # variables
        self.var_dep = ctk.StringVar(value="CSE")
        self.var_course = ctk.StringVar(value="B.Tech")
        self.var_year = ctk.StringVar(value="2024-25")
        self.var_semester = ctk.StringVar(value="Semester-1")
        self.var_section = ctk.StringVar(value="A") 

        self.var_roll = ctk.StringVar()
        self.var_std_name = ctk.StringVar()
        self.var_gender = ctk.StringVar(value="Male")
        self.var_dob = ctk.StringVar()
        self.var_phone = ctk.StringVar()
        self.var_email = ctk.StringVar()
        self.var_address = ctk.StringVar()
        self.var_radio = ctk.StringVar(value="Take Photo") 
        
        self.var_search_by = ctk.StringVar(value="Roll No")
        self.var_search_txt = ctk.StringVar()
        
        self.selected_roll = None
        
        self.create_widgets()
        self.fetch_data()

    def get_db_connection(self):
        return mysql.connector.connect(**self.db_config)
    
    def update_courses(self, choice):
        valid_courses = self.dept_course_map.get(choice, ["Other"])
        self.combo_course.configure(values=valid_courses)
        self.combo_course.set(valid_courses[0])
        self.var_course.set(valid_courses[0])

    def create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=self.COLOR_PRIMARY, height=60, corner_radius=0)
        header.pack(fill="x")
        
        ctk.CTkButton(header, text="← Back", command=self.close_window, width=80, height=30, fg_color="#E74C3C", hover_color="#C0392B").place(relx=0.02, rely=0.5, anchor="w")
        
        ctk.CTkLabel(header, text="MANAGE STUDENT DETAILS", font=("Roboto", 24, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")
        
        self.tab_view = ctk.CTkTabview(self, fg_color=self.COLOR_SOFT)
        self.tab_view.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tab_view.add("Registration Form")
        self.tab_view.add("Student Database")
        
        self.create_form_tab(self.tab_view.tab("Registration Form"))
        self.create_table_tab(self.tab_view.tab("Student Database"))

    def close_window(self):
        if self.is_camera_on: self.toggle_camera()
        self.destroy()

    # form tab
    def create_form_tab(self, parent):
        parent.columnconfigure(0, weight=1); parent.columnconfigure(1, weight=1); parent.rowconfigure(0, weight=1)
        left_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=15)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        form = ctk.CTkFrame(left_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30, pady=20)
        form.columnconfigure((1, 3), weight=1) 

        # academic info
        ctk.CTkLabel(form, text="ACADEMIC DETAILS", font=("Roboto", 14, "bold"), text_color=self.COLOR_PRIMARY).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 15))
        
        ctk.CTkLabel(form, text="Department:").grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.combo_dep = ctk.CTkComboBox(form, variable=self.var_dep, values=self.dept_list, command=self.update_courses, width=180)
        self.combo_dep.grid(row=1, column=1, padx=15, pady=10, sticky="w")
        
        ctk.CTkLabel(form, text="Course:").grid(row=1, column=2, padx=15, pady=10, sticky="w")
        self.combo_course = ctk.CTkComboBox(form, variable=self.var_course, values=self.dept_course_map["CSE"], width=180)
        self.combo_course.grid(row=1, column=3, padx=15, pady=10, sticky="w")

        ctk.CTkLabel(form, text="Year:").grid(row=2, column=0, padx=15, pady=10, sticky="w")
        self.combo_year = ctk.CTkComboBox(form, variable=self.var_year, values=["2022-23", "2023-24", "2024-25"], width=180).grid(row=2, column=1, padx=15, pady=10, sticky="w")

        ctk.CTkLabel(form, text="Semester:").grid(row=2, column=2, padx=15, pady=10, sticky="w")
        self.combo_sem = ctk.CTkComboBox(form, variable=self.var_semester, values=["Semester-1", "Semester-2", "Semester-3", "Semester-4", "Semester-5", "Semester-6"], width=180).grid(row=2, column=3, padx=15, pady=10, sticky="w")

        ctk.CTkLabel(form, text="Section:").grid(row=3, column=0, padx=15, pady=10, sticky="w")
        self.combo_sec = ctk.CTkComboBox(form, variable=self.var_section, values=["A", "B", "C", "D"], width=180)
        self.combo_sec.grid(row=3, column=1, padx=15, pady=10, sticky="w")

        # personal info
        ctk.CTkFrame(form, height=2, fg_color="#E0E0E0").grid(row=4, column=0, columnspan=4, sticky="ew", pady=15)
        ctk.CTkLabel(form, text="PERSONAL DETAILS", font=("Roboto", 14, "bold"), text_color=self.COLOR_PRIMARY).grid(row=5, column=0, columnspan=4, sticky="w", pady=(0, 15))

        ctk.CTkLabel(form, text="Roll No:").grid(row=6, column=0, padx=15, pady=10, sticky="w")
        ctk.CTkEntry(form, textvariable=self.var_roll, placeholder_text="Unique ID", width=180).grid(row=6, column=1, padx=15, pady=10, sticky="w")
        ctk.CTkLabel(form, text="Name:").grid(row=6, column=2, padx=15, pady=10, sticky="w")
        ctk.CTkEntry(form, textvariable=self.var_std_name, width=180).grid(row=6, column=3, padx=15, pady=10, sticky="w")
        ctk.CTkLabel(form, text="DOB (YYYY-MM-DD):").grid(row=7, column=0, padx=15, pady=10, sticky="w")
        ctk.CTkEntry(form, textvariable=self.var_dob, placeholder_text="2000-01-01", width=180).grid(row=7, column=1, padx=15, pady=10, sticky="w")
        ctk.CTkLabel(form, text="Gender:").grid(row=7, column=2, padx=15, pady=10, sticky="w")
        ctk.CTkComboBox(form, variable=self.var_gender, values=["Male", "Female", "Other"], width=180).grid(row=7, column=3, padx=15, pady=10, sticky="w")

        # contact info
        ctk.CTkFrame(form, height=2, fg_color="#E0E0E0").grid(row=8, column=0, columnspan=4, sticky="ew", pady=15)
        ctk.CTkLabel(form, text="CONTACT DETAILS", font=("Roboto", 14, "bold"), text_color=self.COLOR_PRIMARY).grid(row=9, column=0, columnspan=4, sticky="w", pady=(0, 15))

        ctk.CTkLabel(form, text="Phone No:").grid(row=10, column=0, padx=15, pady=10, sticky="w")
        ctk.CTkEntry(form, textvariable=self.var_phone, width=180).grid(row=10, column=1, padx=15, pady=10, sticky="w")
        ctk.CTkLabel(form, text="Parent Email:").grid(row=10, column=2, padx=15, pady=10, sticky="w")
        ctk.CTkEntry(form, textvariable=self.var_email, width=180).grid(row=10, column=3, padx=15, pady=10, sticky="w")
        ctk.CTkLabel(form, text="Address:").grid(row=11, column=0, padx=15, pady=10, sticky="w")
        ctk.CTkEntry(form, textvariable=self.var_address, width=400).grid(row=11, column=1, columnspan=3, padx=15, pady=10, sticky="w")

        # btns
        action_frame = ctk.CTkFrame(form, fg_color="transparent"); action_frame.grid(row=12, column=0, columnspan=4, pady=(30, 0))
        ctk.CTkRadioButton(action_frame, text="Take Photo (New)", variable=self.var_radio, value="Take Photo", command=self.check_photo_mode).pack(side="left", padx=10)
        ctk.CTkRadioButton(action_frame, text="Update Photo", variable=self.var_radio, value="Update Photo", command=self.check_photo_mode).pack(side="left", padx=10)
        ctk.CTkFrame(action_frame, width=20, height=1, fg_color="transparent").pack(side="left")
        ctk.CTkButton(action_frame, text="SAVE", command=self.add_data, fg_color="#2ecc71", width=100).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="UPDATE", command=self.update_data, fg_color="#3498db", width=100).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="DELETE", command=self.delete_data, fg_color="#e74c3c", width=100).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="RESET", command=self.reset_data, fg_color="#f1c40f", width=100).pack(side="left", padx=5)

        # right frme
        right = ctk.CTkFrame(parent, fg_color="white", corner_radius=15)
        right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(right, text="PHOTO CAPTURE", font=("Roboto", 18, "bold"), text_color="gray").place(relx=0.5, rely=0.1, anchor="center")
        self.cam_lbl = Label(right, text="Camera Inactive", font=("Arial", 14), bg="#E0E0E0", fg="#666")
        self.cam_lbl.place(relx=0.5, rely=0.45, anchor="center", width=400, height=320) 
        self.btn_cam_toggle = ctk.CTkButton(right, text="START CAMERA", command=self.toggle_camera, fg_color="#9C27B0", width=300, height=45)
        self.btn_cam_toggle.place(relx=0.5, rely=0.75, anchor="center")
        self.btn_capture = ctk.CTkButton(right, text="CAPTURE & SAVE", command=self.capture_single_photo, fg_color="#E0E0E0", text_color="gray", state="disabled", width=300, height=45)
        self.btn_capture.place(relx=0.5, rely=0.85, anchor="center")

    # table tab
    def create_table_tab(self, parent):
        search_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10); search_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(search_frame, text="Search By:", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkComboBox(search_frame, variable=self.var_search_by, values=["Roll No", "Phone", "Name"], width=120).pack(side="left", padx=5)
        ctk.CTkEntry(search_frame, textvariable=self.var_search_txt, width=200).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Search", command=self.search_data, width=100, fg_color="#3498db").pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="Show All", command=self.fetch_data, width=100, fg_color="#2ecc71").pack(side="left", padx=5)

        frame = ctk.CTkFrame(parent); frame.pack(fill="both", expand=True, padx=10, pady=10)
        scroll_y = ttk.Scrollbar(frame, orient=VERTICAL); scroll_x = ttk.Scrollbar(frame, orient=HORIZONTAL)
        
        cols = ("name", "roll", "dep", "course", "year", "sem", "sec", "gender", "dob", "phone", "email", "address", "photo")
        self.table = ttk.Treeview(frame, columns=cols, show="headings", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.config(command=self.table.yview); scroll_y.pack(side=RIGHT, fill=Y); scroll_x.config(command=self.table.xview); scroll_x.pack(side=BOTTOM, fill=X)
        self.table.pack(fill=BOTH, expand=1)
        
        headings = ["Name", "Roll No", "Dept", "Course", "Year", "Sem", "Section", "Gender", "DOB", "Phone", "Parent Email", "Address", "Photo"]
        widths = [120, 80, 80, 80, 80, 80, 60, 80, 100, 100, 150, 150, 80]
        for col, text, w in zip(cols, headings, widths): self.table.heading(col, text=text); self.table.column(col, width=w, minwidth=50)
        self.table.bind("<ButtonRelease>", self.get_cursor)

    # functions
    def search_data(self):
        try:
            conn = self.get_db_connection(); cursor = conn.cursor()
            search_col = "Roll_No" if self.var_search_by.get() == "Roll No" else ("Phone" if self.var_search_by.get() == "Phone" else "Name")
            query = f"SELECT Name, Roll_No, Department, Course, Year, Semester, Section, Gender, DOB, Phone, Parent_Email, Address, Photo_Sample FROM student WHERE {search_col} LIKE %s"
            cursor.execute(query, ("%" + self.var_search_txt.get() + "%",))
            rows = cursor.fetchall(); self.table.delete(*self.table.get_children())
            for row in rows: self.table.insert("", END, values=row)
            conn.close()
        except: pass

    def check_photo_mode(self):
        self.btn_capture.configure(text="CAPTURE & SAVE (NEW)" if self.var_radio.get() == "Take Photo" else "OVERWRITE PHOTO (UPDATE)")

    def toggle_camera(self):
        if self.is_camera_on:
            self.is_camera_on = False; self.cap.release()
            self.cam_lbl.config(image="", text="Camera Inactive", bg="#E0E0E0")
            self.btn_cam_toggle.configure(text="START CAMERA", fg_color="#9C27B0")
            self.btn_capture.configure(state="disabled", fg_color="#E0E0E0", text_color="gray")
        else:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.is_camera_on = True; self.cam_lbl.config(bg="black") 
                self.btn_cam_toggle.configure(text="STOP CAMERA", fg_color="#E94560")
                self.btn_capture.configure(state="normal", fg_color="#2ecc71", text_color="white")
                self.update_camera_feed(); self.check_photo_mode()
            else: messagebox.showerror("Error", "Cannot open camera")

    def update_camera_feed(self):
        if not self.is_camera_on: return 
        ret, frame = self.cap.read()
        if ret:
            self.current_frame_clean = frame.copy(); display_frame = frame.copy()
            gray = cv2.cvtColor(display_frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_classifier.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces: cv2.rectangle(display_frame, (x,y), (x+w, y+h), (0,255,0), 2)
            img = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB); img_pil = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img_pil.resize((400, 320)))
            self.cam_lbl.imgtk = imgtk; self.cam_lbl.config(image=imgtk, text="")
        self.after(20, self.update_camera_feed)

    def capture_single_photo(self):
        if self.var_roll.get() == "": messagebox.showerror("Error", "Enter Roll No first!"); return
        conn = self.get_db_connection(); cursor = conn.cursor()
        cursor.execute("SELECT * FROM student WHERE Roll_No=%s", (self.var_roll.get(),))
        if not cursor.fetchone(): messagebox.showerror("Error", "Please click SAVE first."); conn.close(); return
        if self.current_frame_clean is not None:
            if not os.path.exists("student_images"): os.makedirs("student_images")
            cv2.imwrite(f"student_images/{self.var_roll.get().strip()}.jpg", self.current_frame_clean)
            cursor.execute("UPDATE student SET Photo_Sample='Yes' WHERE Roll_No=%s", (self.var_roll.get(),))
            conn.commit(); conn.close(); messagebox.showinfo("Success", "Photo Saved!"); self.fetch_data(); self.toggle_camera(); self.reset_data()

    def add_data(self):
        if self.var_roll.get() == "": return
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", self.var_dob.get()): messagebox.showerror("Invalid Date", "DOB must be YYYY-MM-DD"); return
        try:
            conn = self.get_db_connection(); cursor = conn.cursor()
            query = """INSERT INTO student (Name, Roll_No, Department, Course, Year, Semester, Section, Gender, DOB, Phone, Parent_Email, Address, Photo_Sample) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            vals = (self.var_std_name.get(), self.var_roll.get(), self.var_dep.get(), self.var_course.get(), 
                    self.var_year.get(), self.var_semester.get(), self.var_section.get(), self.var_gender.get(), self.var_dob.get(), 
                    self.var_phone.get(), self.var_email.get(), self.var_address.get(), "No")
            cursor.execute(query, vals); conn.commit(); conn.close(); self.fetch_data(); messagebox.showinfo("Success", "Saved.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def fetch_data(self):
        conn = self.get_db_connection(); cursor = conn.cursor()
        cursor.execute("SELECT Name, Roll_No, Department, Course, Year, Semester, Section, Gender, DOB, Phone, Parent_Email, Address, Photo_Sample FROM student")
        rows = cursor.fetchall(); self.table.delete(*self.table.get_children())
        for row in rows: self.table.insert("", END, values=row)
        conn.close()

    def get_cursor(self, event):
        row = self.table.item(self.table.focus())['values']
        if row:
            self.var_std_name.set(row[0]); self.var_roll.set(row[1]); self.var_dep.set(row[2])
            self.update_courses(row[2]); self.var_course.set(row[3]); self.var_year.set(row[4])
            self.var_semester.set(row[5]); self.var_section.set(row[6]); self.var_gender.set(row[7])
            self.var_dob.set(row[8]); self.var_phone.set(row[9]); 
            self.var_email.set(row[10]); self.var_address.set(row[11])
            self.selected_roll = row[1]; self.var_radio.set("Update Photo" if row[12] == "Yes" else "Take Photo"); self.check_photo_mode()

    def update_data(self):
        try:
            conn = self.get_db_connection(); cursor = conn.cursor()
            query = """UPDATE student SET Name=%s, Department=%s, Course=%s, Year=%s, Semester=%s, Section=%s, Gender=%s, DOB=%s, Phone=%s, Parent_Email=%s, Address=%s WHERE Roll_No=%s"""
            vals = (self.var_std_name.get(), self.var_dep.get(), self.var_course.get(), self.var_year.get(), 
                    self.var_semester.get(), self.var_section.get(), self.var_gender.get(), self.var_dob.get(), self.var_phone.get(), 
                    self.var_email.get(), self.var_address.get(), self.selected_roll)
            cursor.execute(query, vals); conn.commit(); conn.close(); self.fetch_data(); self.reset_data(); messagebox.showinfo("Updated", "Record Updated")
        except Exception as e: messagebox.showerror("Error", str(e))

    def delete_data(self):
        if not self.selected_roll: return
        try:
            conn = self.get_db_connection(); cursor = conn.cursor()
            cursor.execute("DELETE FROM student WHERE Roll_No=%s", (self.selected_roll,))
            conn.commit(); conn.close()
            if os.path.exists(f"student_images/{self.selected_roll}.jpg"): os.remove(f"student_images/{self.selected_roll}.jpg")
            self.fetch_data(); self.reset_data(); messagebox.showinfo("Deleted", "Student Deleted")
        except: pass

    def reset_data(self):
        self.var_roll.set(""); self.var_std_name.set(""); self.var_dob.set(""); 
        self.var_phone.set(""); self.var_email.set(""); self.var_address.set(""); 
        self.selected_roll = None; self.var_radio.set("Take Photo"); self.check_photo_mode()
        if self.is_camera_on: self.toggle_camera()
        self.cam_lbl.config(image="", text="Camera Inactive", bg="#E0E0E0")

if __name__ == "__main__":
    app = Student()
    app.mainloop()