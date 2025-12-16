import customtkinter as ctk
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import csv
import os
import sys
from datetime import datetime
from config import get_db_connection as connect_to_cloud

ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")

class AttendanceViewer(ctk.CTkToplevel):
    def __init__(self, user_role="super_admin", user_id="1", current_user="Admin"):
        super().__init__()

        self.user_role = user_role
        self.user_id = user_id
        self.current_user = current_user

        self.title(f"Attendance Report - {self.user_role.upper()}")
        self.geometry("1350x750")
        self.after(10, lambda: self.state('zoomed'))
        
        try:
            self.iconbitmap("images/app_icon.ico")
        except: pass
        
        self.COLOR_PRIMARY = "#0A2647"
        
        # --- Variables for filters ---
        self.var_filter_year = ctk.StringVar(value="All")
        self.var_filter_sec = ctk.StringVar(value="All")
        self.var_filter_sem = ctk.StringVar(value="All")
        self.var_filter_dept = ctk.StringVar(value="All")
        self.var_filter_teacher = ctk.StringVar(value="All")
        self.var_filter_subject = ctk.StringVar(value="All")

        self.teacher_username = None
        if self.user_role == 'admin': 
            self.teacher_username = self.get_teacher_username_by_id(self.user_id)

        self.create_widgets()
        self.fetch_data()

    def get_db_connection(self):
        return connect_to_cloud()

    def get_teacher_username_by_id(self, t_id):
        """Fetch Teacher Username from ID for filtering"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Username FROM teacher WHERE Teacher_ID=%s", (t_id,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except: return None

    def create_widgets(self):
        # --- Header ---
        header = ctk.CTkFrame(self, fg_color=self.COLOR_PRIMARY, height=70, corner_radius=0)
        header.pack(fill="x")
        
        btn_back = ctk.CTkButton(header, text="← Back", command=self.destroy, width=80, height=30, fg_color="#E74C3C", hover_color="#C0392B")
        btn_back.place(relx=0.02, rely=0.5, anchor="w")

        title_text = "CLASSROOM ATTENDANCE RECORD"
        if self.user_role == 'student':
            title_text = f"MY ATTENDANCE RECORD (Roll: {self.user_id})"
        
        ctk.CTkLabel(header, text=title_text, font=("Roboto", 24, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        # --- Student Stats Panel 
        if self.user_role == 'student':
            self.stats_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
            self.stats_frame.pack(fill="x", padx=20, pady=15)
            self.card_total = self.create_stat_card(self.stats_frame, "Total Lectures", "0", "#3498db", 0)
            self.card_present = self.create_stat_card(self.stats_frame, "Attended", "0", "#2ecc71", 1)
            self.card_percent = self.create_stat_card(self.stats_frame, "Percentage", "0%", "#9b59b6", 2)

        # --- Filter Area ---
        filter_frame = ctk.CTkFrame(self, fg_color="white", height=80)
        filter_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(filter_frame, text="Filter By:", font=("Arial", 12, "bold"), text_color="gray").pack(side="left", padx=15)

        # 1. SUPER ADMIN (Sees Everything)
        if self.user_role == 'super_admin':
            # Dept
            ctk.CTkLabel(filter_frame, text="Dept:").pack(side="left", padx=2)
            self.combo_dept = ctk.CTkComboBox(filter_frame, variable=self.var_filter_dept, values=["All", "CSE","Arts", "IT", "Civil", "Mechanical", "CE","Commerce"], width=80)
            self.combo_dept.pack(side="left", padx=5)

            # Teacher
            ctk.CTkLabel(filter_frame, text="Teacher:").pack(side="left", padx=2)
            self.combo_teacher = ctk.CTkComboBox(filter_frame, variable=self.var_filter_teacher, values=["All"], width=110)
            self.combo_teacher.pack(side="left", padx=5)
            self.load_teacher_list() # Populate teacher list

            # Standard Filters
            self.add_standard_filters(filter_frame)

        # 2. TEACHER (Admin)
        elif self.user_role == 'admin':
            # Dept
            ctk.CTkLabel(filter_frame, text="Dept:").pack(side="left", padx=2)
            self.combo_dept = ctk.CTkComboBox(filter_frame, variable=self.var_filter_dept, values=["All", "CSE", "IT", "ECE", "ME", "CE"], width=80)
            self.combo_dept.pack(side="left", padx=5)

            # No Teacher Filter (Because they ARE the teacher)
            
            # Standard Filters
            self.add_standard_filters(filter_frame)

        # 3. STUDENT (Sees ONLY Subject and Teacher Filters)
        elif self.user_role == 'student':
            # Subject
            ctk.CTkLabel(filter_frame, text="Subject:").pack(side="left", padx=2)
            self.combo_sub = ctk.CTkComboBox(filter_frame, variable=self.var_filter_subject, values=["All", "Java", "Python", "DSA", "DBMS", "OS"], width=100)
            self.combo_sub.pack(side="left", padx=5)

            # Teacher 
            ctk.CTkLabel(filter_frame, text="Marked By:").pack(side="left", padx=2)
            self.combo_teacher = ctk.CTkComboBox(filter_frame, variable=self.var_filter_teacher, values=["All"], width=110)
            self.combo_teacher.pack(side="left", padx=5)
            self.load_teacher_list()

        # Buttons (Common for all)
        ctk.CTkButton(filter_frame, text="Apply", command=self.fetch_data, width=80, fg_color="#0A2647").pack(side="left", padx=10)
        ctk.CTkButton(filter_frame, text="Reset", command=self.reset_filters, width=70, fg_color="gray").pack(side="left", padx=5)
        ctk.CTkButton(filter_frame, text="Export CSV", command=self.export_csv, fg_color="green", width=110).pack(side="right", padx=15, pady=10)

        # --- Table ---
        table_frame = ctk.CTkFrame(self, fg_color="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        scroll_y = ttk.Scrollbar(table_frame, orient=VERTICAL)
        scroll_x = ttk.Scrollbar(table_frame, orient=HORIZONTAL)

        cols = ("roll", "name", "year", "sec", "subject", "time", "date", "teacher", "status")
        self.table = ttk.Treeview(table_frame, columns=cols, show="headings", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.config(command=self.table.yview); scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.table.xview); scroll_x.pack(side=BOTTOM, fill=X)
        self.table.pack(fill=BOTH, expand=1)

        headers = ["Roll No", "Name", "Year", "Sec", "Subject", "Time", "Date", "Marked By", "Status"]
        widths = [80, 150, 60, 50, 120, 80, 90, 120, 80]
        
        for col, text, w in zip(cols, headers, widths):
            self.table.heading(col, text=text)
            self.table.column(col, width=w, anchor="center")
            
        self.table.tag_configure("Present", foreground="green")
        self.table.tag_configure("Absent", foreground="red")

    def add_standard_filters(self, parent):
        """Helper to add Year, Sem, Sec, Subject filters (Used by Admin/SuperAdmin)"""
        # Year
        ctk.CTkLabel(parent, text="Year:").pack(side="left", padx=2)
        self.combo_year = ctk.CTkComboBox(parent, variable=self.var_filter_year, values=["All", "2023-24", "2024-25", "2025-26"], width=90)
        self.combo_year.pack(side="left", padx=5)
        
        # Sem
        ctk.CTkLabel(parent, text="Sem:").pack(side="left", padx=2)
        sems = ["All"] + [str(i) for i in range(1, 9)]
        self.combo_sem = ctk.CTkComboBox(parent, variable=self.var_filter_sem, values=sems, width=70)
        self.combo_sem.pack(side="left", padx=5)

        # Section
        ctk.CTkLabel(parent, text="Sec:").pack(side="left", padx=2)
        self.combo_sec = ctk.CTkComboBox(parent, variable=self.var_filter_sec, values=["All", "A", "B", "C", "D"], width=70)
        self.combo_sec.pack(side="left", padx=5)

        # Subject
        ctk.CTkLabel(parent, text="Sub:").pack(side="left", padx=2)
        self.combo_sub = ctk.CTkComboBox(parent, variable=self.var_filter_subject, values=["All", "Java", "Python", "DSA", "DBMS", "OS"], width=100)
        self.combo_sub.pack(side="left", padx=5)

    def load_teacher_list(self):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT Marked_By FROM attendance")
            teachers = [row[0] for row in cursor.fetchall()]
            conn.close()
            self.combo_teacher.configure(values=["All"] + teachers)
        except: pass

    def create_stat_card(self, parent, title, value, color, col_idx):
        frame = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
        frame.grid(row=0, column=col_idx, padx=10, pady=10, sticky="ew")
        parent.columnconfigure(col_idx, weight=1)
        ctk.CTkLabel(frame, text=title, font=("Arial", 14), text_color="white").pack(pady=(10,0))
        lbl_value = ctk.CTkLabel(frame, text=value, font=("Arial", 28, "bold"), text_color="white")
        lbl_value.pack(pady=(0,10))
        return lbl_value

    def reset_filters(self):
        self.var_filter_year.set("All")
        self.var_filter_sec.set("All")
        self.var_filter_sem.set("All")
        self.var_filter_dept.set("All")
        self.var_filter_teacher.set("All")
        self.var_filter_subject.set("All")
        self.fetch_data()

    def fetch_data(self):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            sql = """
                SELECT a.Roll_No, a.Name, s.Year, s.Section, a.Subject, a.Time, a.Date, a.Marked_By, a.Status 
                FROM attendance a
                JOIN student s ON a.Roll_No = s.Roll_No
                WHERE 1=1
            """
            params = []

            # 1. STUDENT
            if self.user_role == 'student':
                sql += " AND a.Roll_No = %s"
                params.append(self.user_id)

            # 2. TEACHER: 
            elif self.user_role == 'admin':
                if self.teacher_username:
                    sql += " AND a.Marked_By = %s"
                    params.append(self.teacher_username)

            # ================= FILTER LOGIC =================

            # Subject Filter (Common to all who see it)
            if self.var_filter_subject.get() != "All":
                sql += " AND a.Subject = %s"
                params.append(self.var_filter_subject.get())

            # Teacher Filter (Visible to Student & Super Admin)
            if self.user_role != 'admin' and self.var_filter_teacher.get() != "All":
                sql += " AND a.Marked_By = %s"
                params.append(self.var_filter_teacher.get())

            # Filters NOT for Students (Year, Sec, Sem, Dept)
            if self.user_role != 'student':
                if self.var_filter_dept.get() != "All":
                    sql += " AND s.Department = %s"
                    params.append(self.var_filter_dept.get())

                if self.var_filter_year.get() != "All":
                    sql += " AND s.Year = %s"
                    params.append(self.var_filter_year.get())
                
                if self.var_filter_sec.get() != "All":
                    sql += " AND s.Section = %s"
                    params.append(self.var_filter_sec.get())

                if self.var_filter_sem.get() != "All":
                    sql += " AND s.Semester = %s"
                    params.append(self.var_filter_sem.get())

            sql += " ORDER BY a.Date DESC, a.Time DESC"

            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            
            self.table.delete(*self.table.get_children())
            for row in rows:
                status = row[8]
                self.table.insert("", END, values=row, tags=(status,))

            # Calculate Stats ONLY for Student
            if self.user_role == 'student':
                self.calculate_student_stats(cursor)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Fetch Error: {e}")

    def calculate_student_stats(self, cursor):
        """Student Dashboard Stats"""
        try:
            # Step 1: Get Student's Class Info
            cursor.execute("SELECT Department, Year, Section, Semester FROM student WHERE Roll_No = %s", (self.user_id,))
            info = cursor.fetchone()
            if not info: return
            dept, year, sec, sem = info

            # Step 2: Count Total Distinct Lectures
            sql_total = """
                SELECT COUNT(DISTINCT CONCAT(a.Date, a.Time, a.Subject)) 
                FROM attendance a
                JOIN student s ON a.Roll_No = s.Roll_No
                WHERE s.Department=%s AND s.Year=%s AND s.Section=%s AND s.Semester=%s
            """
            cursor.execute(sql_total, (dept, year, sec, sem))
            total_lectures = cursor.fetchone()[0]

            # Step 3: Count Attended
            sql_present = "SELECT COUNT(*) FROM attendance WHERE Roll_No = %s AND Status = 'Present'"
            cursor.execute(sql_present, (self.user_id,))
            attended_lectures = cursor.fetchone()[0]

            # Step 4: Calculate Percentage
            if total_lectures > 0:
                percent = (attended_lectures / total_lectures) * 100
            else:
                percent = 0.0

            # Update UI
            self.card_total.configure(text=str(total_lectures))
            self.card_present.configure(text=str(attended_lectures))
            self.card_percent.configure(text=f"{percent:.1f}%")

            # Color Coding
            if percent < 75:
                self.stats_frame.configure(fg_color="#FFEBEE") 
                self.card_percent.configure(text_color="#FF5252") 
            else:
                self.stats_frame.configure(fg_color="#E8F5E9") 
                self.card_percent.configure(text_color="#2ecc71")

        except Exception as e:
            print(f"Stats Error: {e}")

    def export_csv(self):
        try:
            if len(self.table.get_children()) < 1: 
                messagebox.showerror("No Data", "No records to export.")
                return
            
            current_date = datetime.now().strftime("%Y-%m-%d")
            default_name = f"Attendance_{self.user_role}_{current_date}.csv"

            filename = filedialog.asksaveasfilename(
                initialdir=os.getcwd(), title="Save CSV", initialfile=default_name,  
                filetypes=(("CSV File", "*.csv"), ("All Files", "*.*")), defaultextension=".csv"
            )
            
            if not filename: return

            with open(filename, mode='w', newline='') as myfile:
                exp_writer = csv.writer(myfile, delimiter=',')
                exp_writer.writerow(["Roll No", "Name", "Year", "Section", "Subject", "Time", "Date", "Marked By", "Status"])
                for row_id in self.table.get_children():
                    row = self.table.item(row_id)['values']
                    exp_writer.writerow(row)
            
            messagebox.showinfo("Success", f"Data exported successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
if __name__ == "__main__":
    app = ctk.CTk()
    app.withdraw()
    AttendanceViewer()
    app.mainloop()