import customtkinter as ctk
from tkinter import ttk, messagebox
import sys
from config import get_db_connection as connect_to_cloud

# Global Variables passed from main.py
if len(sys.argv) > 4:
    # Role aur ID le rahe hain, DB details ignore kar rahe hain
    USER_ROLE, USER_ID = sys.argv[1], sys.argv[2]
else:
    USER_ROLE, USER_ID = "student", "1"

class TimeTableWindow(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("My Class Schedule")
        self.geometry("1100x500")
        self.after(10, lambda: self.state('zoomed'))
        
        self.COLOR_PRIMARY = "#0A2647"
        self.configure(fg_color="#F5F7F9")
        
        # --- UPDATE: Removed self.db_config (Localhost) ---

        self.create_ui()
        self.load_dynamic_timetable()

    # --- UPDATE: Cloud Connection ---
    def get_db_connection(self):
        return connect_to_cloud()

    def create_ui(self):
        header = ctk.CTkFrame(self, fg_color=self.COLOR_PRIMARY, height=70, corner_radius=0)
        header.pack(fill="x")
        
        btn_back = ctk.CTkButton(header, text="← Back", command=self.destroy, width=80, height=30, fg_color="#E74C3C", hover_color="#C0392B")
        btn_back.place(relx=0.02, rely=0.5, anchor="w")

        ctk.CTkLabel(header, text="WEEKLY TIME TABLE", font=("Roboto", 24, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        frame = ctk.CTkFrame(self, fg_color="white")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=40)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        columns = ("day", "9-10", "10-11", "11-12", "12-1", "1-2", "2-3", "3-4")
        self.table = ttk.Treeview(frame, columns=columns, show="headings")

        headers = ["Day", "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-1:00", "1:00-2:00", "2:00-3:00", "3:00-4:00"]
        
        for col, text in zip(columns, headers):
            self.table.heading(col, text=text)
            self.table.column(col, anchor="center", width=120)

        self.table.pack(fill="both", expand=True)

    def load_dynamic_timetable(self):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Fetch Student Details
            cursor.execute("SELECT Department, Year, Section, Semester FROM student WHERE Roll_No=%s", (USER_ID,))
            student_data = cursor.fetchone()
            
            if not student_data:
                messagebox.showerror("Error", "Student record not found.")
                return
            
            dept, year, sec, sem = student_data
            
            self.title(f"Time Table for {dept} - {year} - Sem {sem} - Section {sec}")
            
            #  Fetch Timetable Data
            sql = """SELECT Day, Time_Start, Subject FROM timetable 
                     WHERE Department=%s AND Year=%s AND Section=%s AND Semester=%s
                     ORDER BY FIELD(Day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')"""
            
            cursor.execute(sql, (dept, year, sec, sem))
            rows = cursor.fetchall()
            
            # 3. Process Data into Grid
            schedule = {day: ["-"] * 7 for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]}
            
            # Helper to normalize time string (handle "9:00" vs "09:00:00")
            def normalize_time(t):
                return str(t)

            time_map = {
                "09:00:00": 0, "9:00:00": 0,
                "10:00:00": 1,
                "11:00:00": 2,
                "12:00:00": 3,
                "14:00:00": 5, "2:00:00": 5,
                "15:00:00": 6, "3:00:00": 6
            }

            for r in rows:
                day, t_start, subj = r
                t_str = str(t_start) 
                
                if t_str in time_map:
                    idx = time_map[t_str]
                    schedule[day][idx] = subj
                else:
                    print(f"Debug: Time {t_str} not in map") 
            
            for day, slots in schedule.items():
                row_data = [day] + slots[:4] + ["LUNCH"] + slots[5:]
                self.table.insert("", "end", values=row_data)

            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load timetable: {e}")

if __name__ == "__main__":
    app = ctk.CTk()
    app.withdraw()
    TimeTableWindow()
    app.mainloop()