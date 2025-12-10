import os
import customtkinter as ctk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
import sys

ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")

# Database Credentials
if len(sys.argv) > 4:
    DB_NAME, DB_PASS = sys.argv[3], sys.argv[4]
else:
    DB_NAME, DB_PASS = "attendance_db_final", "Kaurgill@4343#1"

class ManageTimetable(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Timetable Management System")
        self.geometry("1200x700")
        self.after(10, lambda: self.state('zoomed'))
        # Icon
        try:
            icon_path = os.path.abspath("images/app_icon.ico")
            self.iconbitmap(icon_path)
            self.after(200, lambda: self.iconbitmap(icon_path))
        except: pass

        
        self.COLOR_PRIMARY = "#0A2647"
        self.COLOR_SOFT = "#F5F7F9"
        
        self.db_config = {
            "host": "localhost", "user": "root",
            "password": DB_PASS, "database": DB_NAME
        }

        # Variables
        self.var_dept = ctk.StringVar(value="CSE")
        self.var_year = ctk.StringVar(value="2024-25")
        self.var_sem = ctk.StringVar(value="Semester-1")
        self.var_sec = ctk.StringVar(value="A")
        self.var_day = ctk.StringVar(value="Monday")
        self.var_time = ctk.StringVar(value="09:00:00")
        self.var_subject = ctk.StringVar()
        self.var_teacher = ctk.StringVar()
        
        self.teacher_list = [] # To store loaded teachers
        
        self.create_widgets()
        self.load_teachers() # Load teachers into dropdown
        self.fetch_data()

    def get_db_connection(self):
        return mysql.connector.connect(**self.db_config)

    def load_teachers(self):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Username FROM teacher")
            rows = cursor.fetchall()
            self.teacher_list = [r[0] for r in rows]
            if self.teacher_list:
                self.combo_teacher.configure(values=self.teacher_list)
                self.var_teacher.set(self.teacher_list[0])
            conn.close()
        except: pass

    def create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=self.COLOR_PRIMARY, height=70, corner_radius=0)
        header.pack(fill="x")
        
        btn_back = ctk.CTkButton(header, text="← Back", command=self.destroy, width=80, height=30, fg_color="#E74C3C", hover_color="#C0392B")
        btn_back.place(relx=0.02, rely=0.5, anchor="w")
        
        ctk.CTkLabel(header, text="MANAGE CLASS SCHEDULES", font=("Roboto", 24, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        main_frame = ctk.CTkFrame(self, fg_color=self.COLOR_SOFT)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # lft form
        left_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=15, width=400)
        left_frame.pack(side="left", fill="y", padx=(0, 20))
        left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="Assign New Class", font=("Arial", 18, "bold"), text_color=self.COLOR_PRIMARY).pack(pady=20)

        # Form Grid
        form = ctk.CTkFrame(left_frame, fg_color="transparent")
        form.pack(fill="x", padx=20)

        # Dept & Year
        ctk.CTkLabel(form, text="Dept:").grid(row=0, column=0, sticky="w", pady=5)
        ctk.CTkComboBox(form, variable=self.var_dept, values=["CSE", "IT", "Civil", "Arts", "Commerce"], width=120).grid(row=0, column=1, pady=5)
        
        ctk.CTkLabel(form, text="Year:").grid(row=0, column=2, sticky="w", pady=5, padx=5)
        ctk.CTkComboBox(form, variable=self.var_year, values=["2023-24","2024-25", "2025-26"], width=120).grid(row=0, column=3, pady=5)

        # Sem & Sec
        ctk.CTkLabel(form, text="Sem:").grid(row=1, column=0, sticky="w", pady=5)
        ctk.CTkComboBox(form, variable=self.var_sem, values=["Semester-1", "Semester-2", "Semester-3", "Semester-4", "Semester-5", "Semester-6", "Semester-7", "Semester-8"], width=120).grid(row=1, column=1, pady=5)

        ctk.CTkLabel(form, text="Sec:").grid(row=1, column=2, sticky="w", pady=5, padx=5)
        ctk.CTkComboBox(form, variable=self.var_sec, values=["A", "B", "C","D"], width=120).grid(row=1, column=3, pady=5)

        # Day & Time
        ctk.CTkLabel(form, text="Day:").grid(row=2, column=0, sticky="w", pady=5)
        ctk.CTkComboBox(form, variable=self.var_day, values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], width=120).grid(row=2, column=1, pady=5)

        ctk.CTkLabel(form, text="Start:").grid(row=2, column=2, sticky="w", pady=5, padx=5)
        ctk.CTkComboBox(form, variable=self.var_time, values=["09:00:00", "10:00:00", "11:00:00", "12:00:00", "14:00:00", "15:00:00"], width=120).grid(row=2, column=3, pady=5)

        # Subject & Teacher
        ctk.CTkLabel(left_frame, text="Subject Name:", font=("Arial", 12, "bold")).pack(anchor="w", padx=25, pady=(15, 0))
        ctk.CTkEntry(left_frame, textvariable=self.var_subject, width=350).pack(pady=5)

        ctk.CTkLabel(left_frame, text="Assign Teacher:", font=("Arial", 12, "bold")).pack(anchor="w", padx=25, pady=(10, 0))
        self.combo_teacher = ctk.CTkComboBox(left_frame, variable=self.var_teacher, values=[], width=350)
        self.combo_teacher.pack(pady=5)

        # Buttons
        ctk.CTkButton(left_frame, text="ASSIGN CLASS", command=self.add_data, fg_color="#2ecc71", width=350, height=40).pack(pady=(30, 10))
        ctk.CTkButton(left_frame, text="DELETE SELECTED", command=self.delete_data, fg_color="#e74c3c", width=350, height=40).pack(pady=10)

        # right tble
        right_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=15)
        right_frame.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(right_frame, text="Current Timetable", font=("Arial", 16, "bold"), text_color="gray").pack(pady=15)

        scroll_y = ttk.Scrollbar(right_frame, orient=VERTICAL)
        cols = ("id", "dept", "year", "sec", "day", "time", "sub", "teacher")
        self.table = ttk.Treeview(right_frame, columns=cols, show="headings", yscrollcommand=scroll_y.set)
        
        scroll_y.config(command=self.table.yview)
        scroll_y.pack(side=RIGHT, fill=Y)
        self.table.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

        headers = ["ID", "Dept", "Year", "Sec", "Day", "Time", "Subject", "Teacher"]
        widths = [40, 60, 80, 50, 80, 80, 120, 100]

        for col, txt, w in zip(cols, headers, widths):
            self.table.heading(col, text=txt)
            self.table.column(col, width=w, anchor="center")
            
        self.table.bind("<ButtonRelease>", self.get_cursor)


    def fetch_data(self):
        try:
            conn = self.get_db_connection(); cursor = conn.cursor()
            cursor.execute("SELECT id, Department, Year, Section, Day, Time_Start, Subject, Teacher_Username FROM timetable ORDER BY Day, Time_Start")
            rows = cursor.fetchall()
            self.table.delete(*self.table.get_children())
            for row in rows: self.table.insert("", END, values=row)
            conn.close()
        except Exception as e: messagebox.showerror("Error", str(e))

    def add_data(self):
        if self.var_subject.get() == "" or self.var_teacher.get() == "":
            messagebox.showerror("Error", "Subject and Teacher are required!")
            return
        
        start_h = int(self.var_time.get().split(":")[0])
        end_h = start_h + 1
        time_end = f"{end_h:02d}:00:00"

        try:
            conn = self.get_db_connection(); cursor = conn.cursor()
            
            sql = """INSERT INTO timetable 
                     (Department, Year, Semester, Section, Day, Time_Start, Time_End, Subject, Teacher_Username) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            val = (self.var_dept.get(), self.var_year.get(), self.var_sem.get(), self.var_sec.get(), 
                   self.var_day.get(), self.var_time.get(), time_end, self.var_subject.get(), self.var_teacher.get())
            
            cursor.execute(sql, val)
            conn.commit()
            conn.close()
            
            self.fetch_data()
            messagebox.showinfo("Success", "Class Assigned Successfully!")

        except mysql.connector.errors.IntegrityError:
            messagebox.showerror("Schedule Conflict", "CLASH DETECTED!\n\nEither:\n1. This Class already has a subject at this time.\n2. This Teacher is busy in another class at this time.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_data(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Select a row first.")
            return
        if messagebox.askyesno("Confirm", "Delete this class schedule?"):
            try:
                conn = self.get_db_connection(); cursor = conn.cursor()
                cursor.execute("DELETE FROM timetable WHERE id=%s", (self.selected_id,))
                conn.commit(); conn.close()
                self.fetch_data()
                self.selected_id = None
            except: pass

    def get_cursor(self, event):
        row = self.table.item(self.table.focus())['values']
        if row: self.selected_id = row[0]

if __name__ == "__main__":
    app = ctk.CTk(); app.withdraw(); ManageTimetable(); app.mainloop()