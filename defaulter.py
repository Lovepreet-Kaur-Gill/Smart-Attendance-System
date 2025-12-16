import os
import sys
import customtkinter as ctk
from tkinter import *
from tkinter import ttk, messagebox
import smtplib
from email.message import EmailMessage
import threading
from config import get_db_connection as connect_to_cloud, EMAIL_CONFIG

ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")

class DefaulterSystem(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.title("Defaulter Management & Alerts")
        self.geometry("1100x650")
        self.after(10, lambda: self.state('zoomed'))

        try:
            icon_path = os.path.abspath("images/app_icon.ico")
            self.iconbitmap(icon_path)
            self.after(200, lambda: self.iconbitmap(icon_path))
        except: pass
        
        self.COLOR_PRIMARY = "#0A2647"
        
        self.all_defaulter_data = [] 
        self.current_displayed_data = []

        self.create_ui()
        self.load_defaulters()

    # --- UPDATE: Cloud Connection ---
    def get_db_connection(self):
        return connect_to_cloud()

    def create_ui(self):
        #  HEADER 
        header = ctk.CTkFrame(self, fg_color=self.COLOR_PRIMARY, height=70, corner_radius=0)
        header.pack(fill="x")
        
        btn_back = ctk.CTkButton(header, text="← Back", command=self.destroy, width=80, height=30, fg_color="#E74C3C", hover_color="#C0392B")
        btn_back.place(relx=0.02, rely=0.5, anchor="w")

        ctk.CTkLabel(header, text="DEFAULTER LIST (< 75%)", font=("Roboto", 24, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        # filter frame
        filter_frame = ctk.CTkFrame(self, fg_color="#F0F0F0")
        filter_frame.pack(fill="x", padx=20, pady=(15, 0))

        ctk.CTkLabel(filter_frame, text="Filter By:", font=("Roboto", 14, "bold")).pack(side=LEFT, padx=15, pady=10)

        self.var_dept = ctk.StringVar(value="All")
        self.combo_dept = ctk.CTkComboBox(filter_frame, values=["All"], variable=self.var_dept, command=self.filter_data, width=150)
        self.combo_dept.pack(side=LEFT, padx=5)

        self.var_year = ctk.StringVar(value="All")
        self.combo_year = ctk.CTkComboBox(filter_frame, values=["All"], variable=self.var_year, command=self.filter_data, width=120)
        self.combo_year.pack(side=LEFT, padx=5)

        self.var_sec = ctk.StringVar(value="All")
        self.combo_sec = ctk.CTkComboBox(filter_frame, values=["All"], variable=self.var_sec, command=self.filter_data, width=100)
        self.combo_sec.pack(side=LEFT, padx=5)

        ctk.CTkButton(filter_frame, text="Reset Filters", command=self.reset_filters, width=100, fg_color="gray").pack(side=LEFT, padx=15)

        # table frame
        main_frame = ctk.CTkFrame(self, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        scroll_y = ttk.Scrollbar(main_frame, orient=VERTICAL)
        cols = ("roll", "name", "dept", "year", "sem", "sec", "email", "lectures", "attended", "perc")
        
        self.table = ttk.Treeview(main_frame, columns=cols, show="headings", yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.table.yview)
        scroll_y.pack(side=RIGHT, fill=Y)
        self.table.pack(fill=BOTH, expand=1)

        headers = ["Roll No", "Name", "Dept", "Year", "Sem", "Sec", "Parent Email", "Total Lec", "Attended", "%"]
        widths = [80, 150, 60, 70, 70, 50, 200, 70, 70, 60]
        
        for col, text, w in zip(cols, headers, widths):
            self.table.heading(col, text=text)
            self.table.column(col, width=w, anchor="center")

        # --- FOOTER ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        self.lbl_count = ctk.CTkLabel(btn_frame, text="Total Defaulters: 0", font=("Roboto", 14))
        self.lbl_count.pack(pady=5)

        self.btn_email = ctk.CTkButton(btn_frame, text="SEND EMAIL TO FILTERED LIST", command=self.confirm_send_emails, 
                                     fg_color=self.COLOR_PRIMARY, font=("Roboto", 14, "bold"), width=300, height=45)
        self.btn_email.pack()
        self.lbl_status = ctk.CTkLabel(btn_frame, text="Ready.", text_color="gray")
        self.lbl_status.pack(pady=5)

    def load_defaulters(self):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            print("-" * 30)
            print("CALCULATING TOTALS (Dept + Year + Sem + Sec)...")

            # CALCULATE TOTAL LECTURES PER CLASS 
            cursor.execute("""
                SELECT 
                    s.Department, 
                    s.Year,
                    s.Semester,
                    s.Section, 
                    COUNT(DISTINCT CONCAT(a.Subject, a.Date, a.Time)) as Total_Lectures
                FROM attendance a
                JOIN student s ON a.Roll_No = s.Roll_No
                GROUP BY s.Department, s.Year, s.Semester, s.Section
            """)
            
            raw_totals = cursor.fetchall()
            
            # Map Key
            class_totals_map = {}
            for row in raw_totals:
                key = (row[0], row[1], row[2], row[3]) 
                count = row[4]
                class_totals_map[key] = count
                print(f" -> Class {key} Total Lectures: {count}")

            # FETCH STUDENT DETAILS
            cursor.execute("SELECT Roll_No, Name, Parent_Email, Department, Year, Semester, Section FROM student")
            students = cursor.fetchall()

            self.all_defaulter_data = [] 
            dept_set, year_set, sec_set = set(), set(), set()

            for stud in students:
                roll, name, email, dept, year, sem, sec = stud
                
                dept_set.add(dept); year_set.add(year); sec_set.add(sec)

                total_lectures = class_totals_map.get((dept, year, sem, sec), 0)

                if total_lectures == 0:
                    continue

                # Count Student Attendance
                cursor.execute("SELECT COUNT(*) FROM attendance WHERE Roll_No=%s AND Status='Present'", (roll,))
                attended = cursor.fetchone()[0]
                
                perc = (attended / total_lectures) * 100
                
                if perc < 75:
                    self.all_defaulter_data.append({
                        "values": (roll, name, dept, year, sem, sec, email, total_lectures, attended, f"{perc:.1f}%"),
                        "raw_perc": perc,
                        "email": email,
                        "name": name,
                        "dept": dept,
                        "year": year,
                        "sec": sec
                    })

            conn.close()
            print("-" * 30)

            self.combo_dept.configure(values=["All"] + sorted(list(dept_set)))
            self.combo_year.configure(values=["All"] + sorted(list(year_set)))
            self.combo_sec.configure(values=["All"] + sorted(list(sec_set)))

            self.filter_data()

        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def filter_data(self, event=None):
        sel_dept = self.var_dept.get()
        sel_year = self.var_year.get()
        sel_sec = self.var_sec.get()

        filtered_list = []

        for item in self.all_defaulter_data:
            match_dept = (sel_dept == "All" or item["dept"] == sel_dept)
            match_year = (sel_year == "All" or item["year"] == sel_year)
            match_sec = (sel_sec == "All" or item["sec"] == sel_sec)

            if match_dept and match_year and match_sec:
                filtered_list.append(item)

        self.update_table(filtered_list)

    def update_table(self, data_list):
        self.table.delete(*self.table.get_children())
        self.current_displayed_data = data_list 

        for item in data_list:
            self.table.insert("", END, values=item["values"])
        
        self.lbl_count.configure(text=f"Total Defaulters: {len(data_list)}")

    def reset_filters(self):
        self.var_dept.set("All")
        self.var_year.set("All")
        self.var_sec.set("All")
        self.filter_data()

    def confirm_send_emails(self):
        count = len(self.current_displayed_data)
        
        if count == 0:
            messagebox.showinfo("Info", "No defaulters in current list.")
            return

        valid_emails = [d for d in self.current_displayed_data if d["email"]]
        
        if not valid_emails:
            messagebox.showwarning("Warning", "None of the listed students have email addresses.")
            return

        if messagebox.askyesno("Confirm", f"Send warning emails to {len(valid_emails)} parents?"):
            threading.Thread(target=self.send_emails_thread, args=(valid_emails,)).start()

    def send_emails_thread(self, target_list):
        self.btn_email.configure(state="disabled", text="SENDING EMAILS...")
        sent_count = 0
        
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
            
            for student in target_list:
                try:
                    msg = EmailMessage()
                    msg['Subject'] = f"Attendance Warning: {student['name']}"
                    msg['From'] = EMAIL_CONFIG["sender_email"]
                    msg['To'] = student['email']
                    
                    body = f"""
                    Dear Parent,
                    
                    This is an automated alert regarding your ward, {student['name']} 
                    (Dept: {student['dept']}, Year: {student['year']}).
                    
                    Current Attendance: {student['values'][9]} (Below 75%)
                    Total Lectures Held: {student['values'][7]}
                    Lectures Attended: {student['values'][8]}
                    
                    Please address this immediately.
                    
                    Regards,
                    College Admin
                    """
                    msg.set_content(body)
                    server.send_message(msg)
                    sent_count += 1
                    self.lbl_status.configure(text=f"Sent to {student['name']}...")
                    
                except Exception as e:
                    print(f"Failed for {student['name']}: {e}")

            server.quit()
            messagebox.showinfo("Success", f"Emails sent successfully to {sent_count} parents.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Email System Error: {e}")
            
        self.btn_email.configure(state="normal", text="SEND EMAIL TO FILTERED LIST")
        self.lbl_status.configure(text="Task Complete.")

if __name__ == "__main__":
    app = ctk.CTk()
    app.withdraw()
    DefaulterSystem()
    app.mainloop()