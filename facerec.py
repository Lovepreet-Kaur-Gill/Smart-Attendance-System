import customtkinter as ctk
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import face_recognition # type: ignore
import mysql.connector
import os
import sys
import pickle
from datetime import datetime
import numpy as np
import math


ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")

#global configurations
if len(sys.argv) > 5:
    USER_ROLE = sys.argv[1]
    USER_ID = sys.argv[2]
    DB_NAME = sys.argv[3]
    DB_PASS = sys.argv[4]
    TEACHER_NAME = sys.argv[5]
else:
    USER_ROLE = "admin"
    USER_ID = "1"
    DB_NAME = "attendance_db_final"
    DB_PASS = "Kaurgill@4343#1"
    TEACHER_NAME = "Admin"

class FaceRecognitionSystem(ctk.CTkToplevel):
    def __init__(self, teacher_name="Admin"):
        super().__init__()
        self.teacher_name = teacher_name

        self.title(f"Liveness Attendance Monitor - {TEACHER_NAME}")
        self.geometry("1000x700") 
        self.after(0, lambda: self.state('zoomed')) 


        try:
            icon_path = os.path.abspath("images/app_icon.ico")
            self.iconbitmap(icon_path)
            self.after(200, lambda: self.iconbitmap(icon_path))
        except: pass
       
        self.COLOR_PRIMARY = "#0A2647" 
        self.COLOR_BG = "#F5F7F9"
        self.COLOR_CARD = "white"
        self.COLOR_ACCENT = "#2ecc71"
        
        self.configure(fg_color=self.COLOR_BG)

        self.db_config = {
            "host": "localhost",
            "user": "root",
            "password": DB_PASS,
            "database": DB_NAME
        }

        self.is_running = False
        self.cap = None
        self.known_encodings = []
        self.known_ids = []
        self.student_map = {} 
        self.current_subject = None
        self.current_dept = None
        
        self.blink_counter = 0
        self.eye_closed = False
        self.EAR_THRESHOLD = 0.22 
        
        self.load_encodings()
        self.load_student_data() 
        self.create_ui()

    def load_student_data(self):
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            # Fetch all students
            cursor.execute("SELECT Roll_No, Name, Section, Department FROM student")
            rows = cursor.fetchall()
            # Storing as dictionary
            for r in rows: 
                self.student_map[r[0]] = {"name": r[1], "section": r[2], "dept": r[3]}
            conn.close()
        except Exception as e:
            print(f"Error loading student data: {e}")

    def close_window(self):
        self.stop_camera()
        self.destroy()

    def create_ui(self):
        # header
        header = ctk.CTkFrame(self, fg_color=self.COLOR_PRIMARY, height=80, corner_radius=0)
        header.pack(fill="x")
        
        btn_back = ctk.CTkButton(header, text="← Back", command=self.close_window, 
                                 width=80, height=30, fg_color="#E74C3C", hover_color="#C0392B")
        btn_back.place(relx=0.02, rely=0.5, anchor="w")

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(title_box, text=f"ATTENDANCE MONITOR ({TEACHER_NAME})", 
                     font=("Roboto", 24, "bold"), text_color="white").pack()

        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.controls_frame = ctk.CTkFrame(self.main_frame, fg_color="#F1F5F9")
        self.controls_frame.pack(fill="x", padx=20, pady=10)

        # Dept Dropdown
        ctk.CTkLabel(self.controls_frame, text="Dept:", font=("Arial", 12, "bold"), text_color="#333").pack(side="left", padx=5)
        self.var_dept = ctk.StringVar(value="CSE")
        self.combo_dept = ctk.CTkComboBox(self.controls_frame, variable=self.var_dept, values=["CSE", "IT", "Arts", "Commerce", "Civil"], width=80)
        self.combo_dept.pack(side="left", padx=5)

        # Year Dropdown
        ctk.CTkLabel(self.controls_frame, text="Year:", font=("Arial", 12, "bold"), text_color="#333").pack(side="left", padx=5)
        self.var_year = ctk.StringVar(value="2024-25")
        self.combo_year = ctk.CTkComboBox(self.controls_frame, variable=self.var_year, values=["2023-24","2024-25", "2025-26"], width=100)
        self.combo_year.pack(side="left", padx=5)

        # Section Dropdown
        ctk.CTkLabel(self.controls_frame, text="Sec:", font=("Arial", 12, "bold"), text_color="#333").pack(side="left", padx=5)
        self.var_sec = ctk.StringVar(value="A")
        self.combo_sec = ctk.CTkComboBox(self.controls_frame, variable=self.var_sec, values=["A", "B", "C", "D"], width=60)
        self.combo_sec.pack(side="left", padx=5)

        # Status Labels
        self.lbl_subject_status = ctk.CTkLabel(self.controls_frame, text="Subject: Waiting...", font=("Arial", 12, "bold"), text_color="gray")
        self.lbl_subject_status.pack(side="left", padx=20)

        self.lbl_liveness = ctk.CTkLabel(self.controls_frame, text="Idle", font=("Arial", 12, "bold"), text_color="gray")
        self.lbl_liveness.pack(side="right", padx=20)

        # video display
        self.lbl_video = Label(self.main_frame, text="Select Class & Start Camera", bg="#E0E0E0", font=("Arial", 14))
        self.lbl_video.pack(pady=10)
        self.lbl_video.place(relx=0.5, rely=0.55, anchor="center", width=640, height=480)

        # btns
        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.place(relx=0.5, rely=0.92, anchor="center")

        self.btn_start = ctk.CTkButton(self.btn_frame, text="FETCH & START", command=self.start_camera, 
                                       width=150, height=40, fg_color="green", hover_color="#2ecc71")
        self.btn_start.pack(side="left", padx=10)

        self.btn_stop = ctk.CTkButton(self.btn_frame, text="STOP", command=self.stop_camera, 
                                      width=150, height=40, fg_color="red", hover_color="#e74c3c", state="disabled")
        self.btn_stop.pack(side="left", padx=10)

    def load_encodings(self):
        if not os.path.exists("encodings.pickle"):
            messagebox.showerror("Error", "Model not found! Train data first."); return
        try:
            with open("encodings.pickle", "rb") as f:
                data = pickle.load(f)
            self.known_encodings = data["encodings"]
            self.known_ids = data["ids"]
        except Exception as e: messagebox.showerror("Error", f"Load Error: {e}")

    def calculate_EAR(self, eye_points):
        A = math.hypot(eye_points[1][0] - eye_points[5][0], eye_points[1][1] - eye_points[5][1])
        B = math.hypot(eye_points[2][0] - eye_points[4][0], eye_points[2][1] - eye_points[4][1])
        C = math.hypot(eye_points[0][0] - eye_points[3][0], eye_points[0][1] - eye_points[3][1])
        return (A + B) / (2.0 * C)

    def get_auto_subject(self):
        try:
            conn = mysql.connector.connect(**self.db_config); cursor = conn.cursor()
            now = datetime.now(); day = now.strftime("%A"); ctime = now.strftime("%H:%M:%S")
            
            sql = """SELECT Subject, Department FROM timetable 
                     WHERE Department=%s AND Year=%s AND Section=%s AND Day=%s 
                     AND Time_Start <= %s AND Time_End >= %s AND Teacher_Username=%s"""
            
            cursor.execute(sql, (self.var_dept.get(), self.var_year.get(), self.var_sec.get(), day, ctime, ctime, TEACHER_NAME))
            row = cursor.fetchone()
            conn.close()
            return row
        except: return None

    def mark_attendance(self, roll_no, name):
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            student_name = name 
            now = datetime.now()
            date_today = now.strftime("%Y-%m-%d")
            time_now = now.strftime("%H:%M:%S")
            
            cursor.execute("SELECT * FROM attendance WHERE Roll_No=%s AND Date=%s AND Subject=%s", (roll_no, date_today, self.current_subject))
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO attendance (Roll_No, Name, Time, Date, Status, Subject, Marked_By) VALUES (%s,%s,%s,%s,%s,%s,%s)", 
                               (roll_no, student_name, time_now, date_today, "Present", self.current_subject, TEACHER_NAME))
                conn.commit()
                self.lbl_liveness.configure(text=f"SUCCESS: {student_name} Marked!", text_color="green")
                self.after(2000, lambda: self.lbl_liveness.configure(text="Live: Monitoring...", text_color="gray"))
            
            conn.close()
        except Exception as e: print(f"DB Error: {e}")

    def start_camera(self):
        result = self.get_auto_subject()
        if not result:
            messagebox.showerror("No Class Found", f"No class for {TEACHER_NAME} in {self.var_dept.get()} {self.var_sec.get()}.")
            return
            
        self.current_subject = result[0]
        self.current_dept = result[1]
        self.lbl_subject_status.configure(text=f"Subject: {self.current_subject} (Live)", text_color=self.COLOR_ACCENT)

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Camera 0 failed. Trying Camera 1...")
            self.cap = cv2.VideoCapture(1)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Cannot open camera! Check connection.")
                return

        self.is_running = True
        self.btn_start.configure(state="disabled"); self.btn_stop.configure(state="normal")
        self.combo_dept.configure(state="disabled"); self.combo_year.configure(state="disabled"); self.combo_sec.configure(state="disabled")
        self.lbl_video.config(bg="black", text="") 
        self.lbl_liveness.configure(text="Live: Monitoring...", text_color="blue")
        self.update_frame()

    def stop_camera(self):
        self.is_running = False
        if self.cap: self.cap.release()
        self.lbl_video.config(image="", text="Select Class & Start", bg="#E0E0E0")
        self.btn_start.configure(state="normal"); self.btn_stop.configure(state="disabled")
        self.combo_dept.configure(state="readonly"); self.combo_year.configure(state="readonly"); self.combo_sec.configure(state="readonly")
        self.lbl_liveness.configure(text="Idle", text_color="gray")
        self.lbl_subject_status.configure(text="Subject: Waiting...", text_color="gray")

    def update_frame(self):
        if not self.is_running: return
        try:
            if not self.winfo_exists(): return
        except: return

        ret, frame = self.cap.read()
        if ret:
            small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            locs = face_recognition.face_locations(rgb)
            encs = face_recognition.face_encodings(rgb, locs)
            lms = face_recognition.face_landmarks(rgb, locs)

            for (t, r, b, l), enc, lm in zip(locs, encs, lms):
                matches = face_recognition.compare_faces(self.known_encodings, enc)
                roll, color = "Unknown", (0, 0, 255)
                
                if True in matches:
                    best = np.argmin(face_recognition.face_distance(self.known_encodings, enc))
                    roll = self.known_ids[best]; color = (0, 255, 0)
                    
                    #  for liveness and validation
                    stu_data = self.student_map.get(roll, {})
                    stu_sec = stu_data.get("section", "Unknown")
                    stu_dept = stu_data.get("dept", "Unknown")

                    #  Section Mismatch
                    if stu_sec != self.var_sec.get():
                        self.lbl_liveness.configure(text=f"Wrong Sec ({stu_sec})", text_color="red")
                        color = (0, 0, 255) # Red Box
                        
                    
                    # 2. Dept Mismatch
                    elif stu_dept != self.current_dept:
                        self.lbl_liveness.configure(text=f"Wrong Dept ({stu_dept})", text_color="red")
                        color = (0, 0, 255) # Red Box
                    
                    # 3. Everything Matches 
                    else:
                        le, re = lm['left_eye'], lm['right_eye']
                        ear = (self.calculate_EAR(le) + self.calculate_EAR(re)) / 2.0
                        
                        if ear < self.EAR_THRESHOLD:
                            self.eye_closed = True; self.lbl_liveness.configure(text="Blink Detected!", text_color="orange")
                        else:
                            if self.eye_closed: 
                                self.eye_closed = False; self.mark_attendance(roll, stu_data.get("name", "Student"))
                            else: self.lbl_liveness.configure(text="Please Blink", text_color="blue")

                t*=4; r*=4; b*=4; l*=4
                cv2.rectangle(frame, (l, t), (r, b), color, 2)
                
                name_show = self.student_map.get(roll, {}).get('name', "Unknown") if roll != "Unknown" else "Unknown"
                display_text = f"{name_show} ({roll})" if roll != "Unknown" else "Unknown"
                cv2.putText(frame, display_text, (l, b+25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img_pil.resize((640, 480)))
            
            try:
                self.lbl_video.imgtk = imgtk
                self.lbl_video.configure(image=imgtk)
            except: pass
            
        if self.is_running:
            self.after(10, self.update_frame)

if __name__ == "__main__":
    app = ctk.CTk(); app.withdraw(); window = FaceRecognitionSystem(); app.mainloop()