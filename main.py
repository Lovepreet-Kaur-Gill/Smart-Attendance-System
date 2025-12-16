import customtkinter as ctk
from tkinter import messagebox
import os
import sys
import time
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import get_db_connection as connect_to_cloud

# importing all modules 
try:
    from student import Student
    from attendance import AttendanceViewer
    from train import TrainWindow
    from facerec import FaceRecognitionSystem
    from defaulter import DefaulterSystem
    from timetable import TimeTableWindow 
    from teacher import TeacherManagement
    from manage_timetable import ManageTimetable
except ImportError as e:
    print(f"Critical Error: Could not import modules. {e}")


ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")

class MainDashboard(ctk.CTk):
    def __init__(self, user_role="admin", user_id="0", db_name="", db_pass="", current_user="Unknown"):
        super().__init__()
        
        # . INITIALIZE VARIABLES 
        self.loader_frame = None 
        self.user_role = user_role.lower()
        self.user_id = user_id        
        self.db_name = db_name
        self.db_pass = db_pass
      
        # --- FIX: Standardized variable name here ---
        self.current_user = current_user 
        
        self.current_user_logic = "root" 

        if self.user_role in ["admin", "super_admin", "teacher"]:
            try:
                conn = connect_to_cloud() 
                cursor = conn.cursor()
                
                if self.user_role == "super_admin":
                    cursor.execute("SELECT username FROM user_credentials WHERE id=%s", (self.user_id,))
                    data = cursor.fetchone()
                    if data: self.current_user_logic = data[0]

                elif self.user_role == "admin": # Teacher
                    cursor.execute("SELECT Username FROM teacher WHERE Teacher_ID=%s", (self.user_id,))
                    data = cursor.fetchone()
                    if data: self.current_user_logic = data[0] 

                conn.close()
            except Exception as e: 
                print(f"User Fetch Error: {e}")
                pass

        # window configuration
        self.title(f"Smart Attendance System - {self.user_role.upper()}")
        self.geometry("1200x720")
        self.after(0, lambda: self.state('zoomed')) 
        
        try:
            icon_path = os.path.abspath("images/app_icon.ico")
            self.iconbitmap(icon_path)
            self.after(200, lambda: self.iconbitmap(icon_path))
        except: pass
        
        self.c_navy = "#0A2647"    
        self.c_bg = "#F5F7F9"      
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_area()

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=self.c_navy)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1) 

        ctk.CTkLabel(self.sidebar_frame, text="Smart\nAttendance", font=("Roboto Medium", 22), text_color="white").pack(pady=(30, 20))

        self.btn_attendance = self.create_nav_btn("Attendance Report", self.open_attendance)
        self.btn_attendance.pack(fill="x", pady=5)
        
        if self.user_role == "super_admin":
            self.create_nav_btn("Student Details", self.open_student_details).pack(fill="x", pady=5)
            self.create_nav_btn("Face Detector", self.open_face_recognition).pack(fill="x", pady=5)
            self.create_nav_btn("Train Data", self.open_train_data).pack(fill="x", pady=5)
            self.create_nav_btn("Photo Gallery", self.open_photos_folder).pack(fill="x", pady=5)
            self.create_nav_btn("Defaulter List", self.open_defaulter).pack(fill="x", pady=5)
            self.create_nav_btn("Employee Reg.", self.open_teacher_reg).pack(fill="x", pady=5)
            self.create_nav_btn("Timetable", self.open_manage_timetable).pack(fill="x", pady=5)

        elif self.user_role == "admin" or self.user_role == "teacher":
            self.create_nav_btn("Face Detector", self.open_face_recognition).pack(fill="x", pady=5)
            self.create_nav_btn("Defaulter List", self.open_defaulter).pack(fill="x", pady=5)
            
        else:
            self.create_nav_btn("Time Table", self.open_timetable).pack(fill="x", pady=5)
        
        self.create_nav_btn("About/Help", self.open_developer_help).pack(fill="x", pady=5)
        ctk.CTkButton(self.sidebar_frame, text="Logout", fg_color="#E94560", command=self.logout).pack(side="bottom", pady=30, padx=20, fill="x")

    def setup_main_area(self):
        self.main_view = ctk.CTkFrame(self, fg_color=self.c_bg, corner_radius=0)
        self.main_view.grid(row=0, column=1, sticky="nsew")
        
        header = ctk.CTkFrame(self.main_view, height=70, fg_color="white", corner_radius=0)
        header.pack(fill="x")
        
        # --- FIX: Using self.current_user here ---
        title_text = f"Welcome, {self.current_user}" if self.user_role != "student" else f"Student Dashboard (Roll: {self.user_id})"
        ctk.CTkLabel(header, text=title_text, font=("Roboto", 24, "bold"), text_color="#333").pack(side="left", padx=30)
        self.time_label = ctk.CTkLabel(header, text="00:00", font=("Roboto Mono", 16), text_color=self.c_navy)
        self.time_label.pack(side="right", padx=30)
        self.update_time()

        self.content_container = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.show_dashboard_view()

    def create_nav_btn(self, text, cmd):
        return ctk.CTkButton(self.sidebar_frame, text=text, fg_color="transparent", hover_color="#144272", anchor="w", command=cmd, height=40)

    def create_dash_card(self, row, col, title, sub, color, cmd, parent=None):
        if parent is None: parent = self.cards_frame
        btn = ctk.CTkButton(parent, text=f"\n{title}\n\n{sub}", font=("Arial", 18, "bold"), fg_color=color, hover_color=color, height=140, command=cmd)
        btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def update_time(self):
        self.time_label.configure(text=time.strftime('%I:%M:%S %p'))
        self.after(1000, self.update_time)

    def clear_content(self):
        for widget in self.content_container.winfo_children(): widget.destroy()

    def show_dashboard_view(self):
        self.clear_content()
        self.cards_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=10)
        self.cards_frame.columnconfigure((0, 1, 2), weight=1) 
        
        if self.user_role == "super_admin":
            self.create_dash_card(0, 0, "Student Details", "Manage", "#2980b9", self.open_student_details)
            self.create_dash_card(0, 1, "Face Detector", "Mark", "#e67e22", self.open_face_recognition)
            self.create_dash_card(0, 2, "Attendance", "View", "#27ae60", self.open_attendance)
            self.create_dash_card(1, 0, "Train Data", "Update", "#8e44ad", self.open_train_data)
            self.create_dash_card(1, 1, "Photos", "View", "#16a085", self.open_photos_folder)
            self.create_dash_card(1, 2, "Defaulter List", "Email", "#c0392b", self.open_defaulter)
            self.create_dash_card(2, 0, "Employee Reg.", "Add Teachers", "#D35400", self.open_teacher_reg)
            self.create_dash_card(2, 1, "Timetable", "Assign Classes", "#8E44AD", self.open_manage_timetable)

        elif self.user_role == "admin" or self.user_role == "teacher":
            self.create_dash_card(0, 0, "Start Class", "Face Detector", "#e67e22", self.open_face_recognition)
            self.create_dash_card(0, 1, "View Reports", "Check Logs", "#27ae60", self.open_attendance)
            self.create_dash_card(0, 2, "Defaulters", "Check Low Attendance", "#c0392b", self.open_defaulter)
            
            footer = ctk.CTkFrame(self.content_container, fg_color="white", corner_radius=15)
            footer.pack(fill="both", expand=True, pady=20, padx=10)
            

        else:
            self.create_dash_card(0, 0, "My Attendance", "Check Report", "#2ecc71", self.open_attendance, self.cards_frame)
            self.create_dash_card(0, 1, "Time Table", "Weekly Schedule", "#3498db", self.open_timetable, self.cards_frame)
            self.create_dash_card(0, 2, "Help Desk", "Contact Admin", "#f39c12", self.open_developer_help, self.cards_frame)
            
            chart_container = ctk.CTkFrame(self.content_container, fg_color="white", corner_radius=15)
            chart_container.pack(fill="both", expand=True, pady=20)
            ctk.CTkLabel(chart_container, text="Subject-wise Attendance Analytics", font=("Arial", 16, "bold"), text_color="#555").pack(pady=(15, 5))
            self.load_student_chart(chart_container)

    def load_student_chart(self, parent):
        try:
            # --- UPDATE 2: Cloud Connection for Charts ---
            conn = connect_to_cloud()
            cursor = conn.cursor()
            query = "SELECT Subject, COUNT(*) FROM attendance WHERE Roll_No=%s AND Status='Present' GROUP BY Subject"
            cursor.execute(query, (self.user_id,))
            data = cursor.fetchall() 
            conn.close()

            if not data:
                ctk.CTkLabel(parent, text="No Attendance Data Available yet.", font=("Arial", 14), text_color="gray").pack(expand=True)
                return
            
            subjects = [row[0] for row in data]
            counts = [row[1] for row in data]
            colors = ['#0A2647', '#2ECC71', '#3498DB', '#9B59B6', '#F39C12', '#E74C3C']
            
            fig = Figure(figsize=(6, 4), dpi=100)
            fig.patch.set_facecolor('white') 
            ax = fig.add_subplot(111)
            wedges, texts, autotexts = ax.pie(counts, labels=None, autopct='%1.1f%%', startangle=90, colors=colors, pctdistance=0.80, wedgeprops={'width': 0.4, 'edgecolor': 'white', 'linewidth': 2})
            for autotext in autotexts: autotext.set_color('white'); autotext.set_fontsize(9); autotext.set_fontweight('bold')
            ax.legend(wedges, subjects, title="Subjects", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            total_present = sum(counts)
            ax.text(0, 0, f"Total\n{total_present}", ha='center', va='center', fontsize=12, fontweight='bold', color='#333')
            
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, pady=10, padx=20)
        except Exception as e:
            print(f"Chart Error: {e}")
            pass

    def show_loading_screen(self, text="Loading Module..."):
        if self.loader_frame: 
            try: self.loader_frame.destroy()
            except: pass
            
        self.loader_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.loader_frame.place(relwidth=1, relheight=1)
        container = ctk.CTkFrame(self.loader_frame, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(container, text="Please Wait", font=("Roboto", 24, "bold"), text_color="#0A2647").pack(pady=10)
        ctk.CTkLabel(container, text=text, font=("Arial", 14), text_color="gray").pack(pady=(0, 20))
        progress = ctk.CTkProgressBar(container, width=400, height=15, progress_color="#0A2647", orientation="horizontal")
        progress.pack(); progress.configure(mode="indeterminate"); progress.start()
        self.update()

    def remove_loading_screen(self):
        if self.loader_frame: 
            try: self.loader_frame.destroy()
            except: pass
            self.loader_frame = None

    def open_window(self, WindowClass, *args):
        self.show_loading_screen(f"Opening {WindowClass.__name__}...")
        self.after(50, lambda: self._launch_real(WindowClass, *args))

    def _launch_real(self, WindowClass, *args):
        if args: window = WindowClass(*args)
        else: window = WindowClass()
        self.after(500, self.withdraw)
        self.wait_window(window)
        
        self.show_loading_screen("Returning to Dashboard...")
        self.deiconify(); self.state('zoomed'); self.after(800, self.remove_loading_screen)

    def open_student_details(self): self.open_window(Student)
    
    def open_face_recognition(self): self.open_window(FaceRecognitionSystem, self.current_user_logic)
    
    def open_attendance(self):
        try:
            # --- FIX: This will now work because self.current_user exists ---
            app = AttendanceViewer(
                user_role=self.user_role, 
                user_id=self.user_id, 
                current_user=self.current_user
            )
            app.mainloop()
        except Exception as e: messagebox.showerror("Error", str(e))
    def open_train_data(self): self.open_window(TrainWindow)
    def open_defaulter(self): self.open_window(DefaulterSystem)
    def open_timetable(self):
        try:
            app = TimeTableWindow(
                user_role=self.user_role, 
                user_id=self.user_id
            )
            app.mainloop()
        except Exception as e: messagebox.showerror("Error", str(e))
    def open_teacher_reg(self): self.open_window(TeacherManagement)
    def open_manage_timetable(self): self.open_window(ManageTimetable)
    
    def open_photos_folder(self): 
        if not os.path.exists("student_images"): os.makedirs("student_images")
        os.startfile("student_images")
    
    def open_developer_help(self): 
        info = """
        SMART ATTENDANCE SYSTEM v2.0
        ------------------------------------
        Developed by:
        1. Lovepreet Kaur (Roll: 2301301130)
        2. Diya Gupta (Roll: 2301301171)
        3. Khushi Rana (Roll: 2301301126)
        
        Tech Stack: Python, SQL, OpenCV
        Contact: 2301301130.lovepreet@geetauniversity.edu
        """
        messagebox.showinfo("Project Info", info)
    def logout(self):
        self.show_loading_screen("Logging Out...")
        self.after(1000, self._perform_logout)

    def _perform_logout(self):
        try:
            self.destroy()

            from login import LoginWindow

            app = LoginWindow()
            app.mainloop()
                
        except Exception as e:
            messagebox.showerror("Error", f"Logout Failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 5:
        role, uid, db_n, db_p, uname = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    elif len(sys.argv) > 4:
        role, uid, db_n, db_p = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
        uname = "Unknown"
    else:
        role, uid, db_n, db_p, uname = "admin", "0", "", "", "Admin"
    
    app = MainDashboard(user_role=role, user_id=uid, db_name=db_n, db_pass=db_p, current_user=uname)
    app.mainloop()