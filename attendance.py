import customtkinter as ctk
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import csv
import os
import sys
from datetime import datetime

ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")

#  Command Line Args for Role, ID, DB_NAME, DB_PASS
if len(sys.argv) > 4:
    USER_ROLE = sys.argv[1]
    USER_ID = sys.argv[2]
    DB_NAME = sys.argv[3]
    DB_PASS = sys.argv[4]
else:
    # Testing defaults
    USER_ROLE = "super_admin"  
    USER_ID = "1"            
    DB_NAME = "attendance_db_final"
    DB_PASS = "Kaurgill@4343#1"

class AttendanceViewer(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.title("Master Attendance Report")
        self.geometry("1350x750")
        
        self.after(10, lambda: self.state('zoomed'))
        
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, "images", "app_icon.ico")
            
            self.iconbitmap(icon_path)
            
            self.after(200, lambda: self.iconbitmap(icon_path))
            
        except Exception as e:
            print(f"Icon Error: {e}") 
        
        self.COLOR_PRIMARY = "#0A2647"
        
        self.db_config = {
            "host": "localhost", "user": "root",
            "password": DB_PASS, "database": DB_NAME
        }
        
        # variables for filters
        self.var_filter_year = ctk.StringVar(value="All")
        self.var_filter_sec = ctk.StringVar(value="All")
        self.var_filter_sem = ctk.StringVar(value="All")
        self.var_filter_dept = ctk.StringVar(value="All")
        self.var_filter_teacher = ctk.StringVar(value="All")
        self.var_filter_subject = ctk.StringVar(value="All")

        
        self.current_teacher_name = None
        if USER_ROLE == 'admin':
            self.current_teacher_name = self.get_teacher_name(USER_ID)

        self.create_widgets()
        self.fetch_data()

    def get_db_connection(self):
        return mysql.connector.connect(**self.db_config)

    def get_teacher_name(self, t_id):
        """Fetch Teacher Username based on Login ID"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Username FROM teacher WHERE Teacher_ID = %s", (t_id,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception as e:
            print(f"Teacher Name Error: {e}")
            return None

    def create_widgets(self):
        # --- Header ---
        try:
            icon_path = os.path.abspath("images/app_icon.ico")
            self.iconbitmap(icon_path)
        except Exception:
            pass 
        header = ctk.CTkFrame(self, fg_color=self.COLOR_PRIMARY, height=70, corner_radius=0)
        header.pack(fill="x")
        
        btn_back = ctk.CTkButton(header, text="← Back", command=self.destroy, width=80, height=30, fg_color="#E74C3C", hover_color="#C0392B")
        btn_back.place(relx=0.02, rely=0.5, anchor="w")


        title_text = f"MY ATTENDANCE (Roll: {USER_ID})" if USER_ROLE == 'student' else "CLASSROOM ATTENDANCE RECORD"
        ctk.CTkLabel(header, text=title_text, font=("Roboto", 24, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        #    Stats Cards (For Students) 
        if USER_ROLE == 'student':
            self.stats_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
            self.stats_frame.pack(fill="x", padx=20, pady=15)
            self.card_total = self.create_stat_card(self.stats_frame, "Total Lectures", "0", "#3498db", 0)
            self.card_present = self.create_stat_card(self.stats_frame, "Attended", "0", "#2ecc71", 1)
            self.card_percent = self.create_stat_card(self.stats_frame, "Percentage", "0%", "#9b59b6", 2)

        # Filter Area   
        if USER_ROLE in ['super_admin', 'admin', 'teacher']:
            filter_frame = ctk.CTkFrame(self, fg_color="white", height=80)
            filter_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(filter_frame, text="Filter By:", font=("Arial", 12, "bold"), text_color="gray").pack(side="left", padx=15)
            
            # super admin view
            if USER_ROLE == 'super_admin':
                # Department Filter
                ctk.CTkLabel(filter_frame, text="Dept:").pack(side="left", padx=2)
                self.combo_dept = ctk.CTkComboBox(filter_frame, variable=self.var_filter_dept, values=["All", "CSE", "IT", "ECE", "ME", "CE"], width=90, command=self.on_dept_change)
                self.combo_dept.pack(side="left", padx=5)

                # Teacher Filter 
                ctk.CTkLabel(filter_frame, text="Teacher:").pack(side="left", padx=2)
                self.combo_teacher = ctk.CTkComboBox(filter_frame, variable=self.var_filter_teacher, values=["All"], width=120)
                self.combo_teacher.pack(side="left", padx=5)

            # teacher view
            if USER_ROLE == 'admin':
                ctk.CTkLabel(filter_frame, text="Sub:").pack(side="left", padx=2)
                self.combo_sub = ctk.CTkComboBox(filter_frame, variable=self.var_filter_subject, values=["All", "Java", "Python", "DSA", "DBMS"], width=100)
                self.combo_sub.pack(side="left", padx=5)

            # Semester
            ctk.CTkLabel(filter_frame, text="Sem:").pack(side="left", padx=2)
            sems = ["All"] + [str(i) for i in range(1, 9)]
            self.combo_sem = ctk.CTkComboBox(filter_frame, variable=self.var_filter_sem, values=sems, width=70)
            self.combo_sem.pack(side="left", padx=5)

            # Year
            ctk.CTkLabel(filter_frame, text="Year:").pack(side="left", padx=2)
            self.combo_year = ctk.CTkComboBox(filter_frame, variable=self.var_filter_year, values=["All", "2024-25", "2025-26"], width=100)
            self.combo_year.pack(side="left", padx=5)
            
            # Section
            ctk.CTkLabel(filter_frame, text="Sec:").pack(side="left", padx=2)
            self.combo_sec = ctk.CTkComboBox(filter_frame, variable=self.var_filter_sec, values=["All", "A", "B", "C", "D"], width=70)
            self.combo_sec.pack(side="left", padx=5)
            
            # Buttons
            ctk.CTkButton(filter_frame, text="Apply", command=self.fetch_data, width=80, fg_color="#0A2647").pack(side="left", padx=10)
            ctk.CTkButton(filter_frame, text="Reset", command=self.reset_filters, width=70, fg_color="gray").pack(side="left", padx=5)
            ctk.CTkButton(filter_frame, text="Export CSV", command=self.export_csv, fg_color="green", width=110).pack(side="right", padx=15, pady=10)

        # table 
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
        widths = [100, 150, 80, 50, 150, 80, 90, 120, 80]
        
        for col, text, w in zip(cols, headers, widths):
            self.table.heading(col, text=text)
            self.table.column(col, width=w, anchor="center")
            
        self.table.tag_configure("Present", foreground="green")
        self.table.tag_configure("Absent", foreground="red")

    def create_stat_card(self, parent, title, value, color, col_idx):
        frame = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
        frame.grid(row=0, column=col_idx, padx=10, pady=10, sticky="ew")
        parent.columnconfigure(col_idx, weight=1)
        ctk.CTkLabel(frame, text=title, font=("Arial", 14), text_color="white").pack(pady=(10,0))
        lbl_value = ctk.CTkLabel(frame, text=value, font=("Arial", 28, "bold"), text_color="white")
        lbl_value.pack(pady=(0,10))
        return lbl_value

    def on_dept_change(self, choice):
        """Logic: Jab Dept change ho, tab uss Dept ke Teachers (Usernames) load karo"""
        if choice == "All":
            self.combo_teacher.configure(values=["All"])
            self.var_filter_teacher.set("All")
            return

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Username FROM teacher WHERE Department = %s", (choice,))
            teachers = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            self.combo_teacher.configure(values=["All"] + teachers)
            self.var_filter_teacher.set("All")
        except Exception as e:
            print(f"Error loading teachers: {e}")

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

            # ROLE BASED FILTERS 
            if USER_ROLE == 'student':
                sql += " AND a.Roll_No = %s"
                params.append(USER_ID)
            
            elif USER_ROLE == 'admin': # Teacher
                if self.current_teacher_name:
                    sql += " AND a.Marked_By = %s"
                    params.append(self.current_teacher_name)
                
                if self.var_filter_subject.get() != "All":
                    sql += " AND a.Subject = %s"
                    params.append(self.var_filter_subject.get())

            elif USER_ROLE == 'super_admin':#students
                if self.var_filter_dept.get() != "All":
                    sql += " AND s.Department = %s"
                    params.append(self.var_filter_dept.get())
                
                if self.var_filter_teacher.get() != "All":
                    sql += " AND a.Marked_By = %s"
                    params.append(self.var_filter_teacher.get())

            if USER_ROLE != 'student':
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

            if USER_ROLE == 'student': 
                self.calculate_stats_correctly(cursor)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Fetch Error: {e}")

    def calculate_stats_correctly(self, cursor):
        try:
            cursor.execute("SELECT Year, Department, Section, Semester FROM student WHERE Roll_No = %s", (USER_ID,))
            student_info = cursor.fetchone()
            
            if not student_info: return 
            stu_year, stu_dept, stu_sec, stu_sem = student_info

            sql_total = """
                SELECT COUNT(DISTINCT CONCAT(a.Date, a.Time, a.Subject)) 
                FROM attendance a
                JOIN student s ON a.Roll_No = s.Roll_No
                WHERE s.Year = %s AND s.Department = %s AND s.Section = %s AND s.Semester = %s
            """
            cursor.execute(sql_total, (stu_year, stu_dept, stu_sec, stu_sem))
            total_lectures = cursor.fetchone()[0]

            sql_present = "SELECT COUNT(*) FROM attendance WHERE Roll_No = %s AND Status = 'Present'"
            cursor.execute(sql_present, (USER_ID,))
            attended_lectures = cursor.fetchone()[0]

            percentage = (attended_lectures / total_lectures) * 100 if total_lectures > 0 else 0.0
            
            self.card_total.configure(text=str(total_lectures))
            self.card_present.configure(text=str(attended_lectures))
            self.card_percent.configure(text=f"{percentage:.1f}%")
            
            if percentage < 75:
                self.card_percent.configure(text_color="#FF5252")
                self.stats_frame.configure(fg_color="#FFEBEE")
            else:
                self.card_percent.configure(text_color="white")
                self.stats_frame.configure(fg_color="#2ecc71")
                
        except Exception as e:
            print(f"Stats Error: {e}")

    def export_csv(self):
        try:
            if len(self.table.get_children()) < 1: 
                messagebox.showerror("No Data", "No records to export.")
                return
            
            current_date = datetime.now().strftime("%Y-%m-%d")
            default_name = f"Attendance_Report_{current_date}.csv"

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
            
            messagebox.showinfo("Success", f"Data exported to {os.path.basename(filename)}")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
if __name__ == "__main__":
    app = ctk.CTk()
    app.withdraw()
    AttendanceViewer()
    app.mainloop()