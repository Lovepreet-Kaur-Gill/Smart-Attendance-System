import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import sys
import subprocess
import os
import time
from config import get_db_connection as connect_to_cloud

ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Login - Face Recognition System")
        self.geometry("900x600")
        self.resizable(True, True)
        self.after(0, lambda: self.state('zoomed')) 

        try:
            self.iconbitmap("images/app_icon.ico")
            self.after(200, lambda: self.iconbitmap("images/app_icon.ico"))
        except: pass

        # --- UPDATE: Hardcoded Local Credentials Hata Diye ---
        # Ab connection config.py handle karega
        
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        # lft side 
        self.left_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#0A2647")
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        
        img_path = "images/sideimg.svg" 
        try:
            if os.path.exists(img_path) and not img_path.endswith(".svg"):
                img_data = Image.open(img_path)
                side_img = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(300, 300))
                self.img_label = ctk.CTkLabel(self.left_frame, image=side_img, text="")
                self.img_label.place(relx=0.5, rely=0.4, anchor="center")
                
                self.brand_label = ctk.CTkLabel(self.left_frame, text="Smart Attendance",
                                                font=("Roboto Medium", 25), text_color="white")
                self.brand_label.place(relx=0.5, rely=0.7, anchor="center")
            else:
                self.brand_label = ctk.CTkLabel(self.left_frame, text="Face Recognition\nAttendance System",
                                                font=("Roboto Medium", 32), text_color="white", justify="center")
                self.brand_label.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            print(f"Image Load Error: {e}")

        # login form
        self.right_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="white")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        self.login_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # labels
        self.label_title = ctk.CTkLabel(self.login_frame, text="Smart Attendance Portal", 
                                      font=("Roboto", 28, "bold"), text_color="#0A2647")
        self.label_title.pack(pady=(0, 5))

        self.label_subtitle = ctk.CTkLabel(self.login_frame, text="Super Admin | Teacher | Student", 
                                         font=("Roboto", 12), text_color="gray")
        self.label_subtitle.pack(pady=(0, 30))

        # Username
        self.user_entry = ctk.CTkEntry(self.login_frame, width=300, height=45, 
                                     placeholder_text="Username / Roll Number",
                                     corner_radius=10, border_color="#E0E0E0", text_color="black", fg_color="#F9F9F9")
        self.user_entry.pack(pady=10)
        
        # Password
        self.pass_entry = ctk.CTkEntry(self.login_frame, width=300, height=45, 
                                     placeholder_text="Password / DOB (YYYY-MM-DD)",
                                     corner_radius=10, show="*", border_color="#E0E0E0", text_color="black", fg_color="#F9F9F9")
        self.pass_entry.pack(pady=10)

        # Show Password Switch
        self.check_var = ctk.StringVar(value="off")
        self.show_pass_switch = ctk.CTkSwitch(self.login_frame, text="Show Password", command=self.toggle_password, 
                                            variable=self.check_var, onvalue="on", offvalue="off",
                                            text_color="gray", progress_color="#0A2647")
        self.show_pass_switch.pack(pady=10, anchor="w", padx=5)

        # Login Button
        self.btn_login = ctk.CTkButton(self.login_frame, text="LOGIN", width=300, height=45,
                                     corner_radius=10, fg_color="#0A2647", hover_color="#144272",
                                     font=("Roboto", 14, "bold"), command=self.login_function)
        self.btn_login.pack(pady=20)
        
        self.bind('<Return>', lambda event: self.login_function())

    def toggle_password(self):
        if self.check_var.get() == "on":
            self.pass_entry.configure(show="")
        else:
            self.pass_entry.configure(show="*")

    # loading screen
    def show_loading_screen(self, role, user_id, user_name):
        """Creates a white overlay with a loader over the entire window"""
        
        #  Overlay Frame
        self.loader_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.loader_frame.place(relwidth=1, relheight=1) # Covers full screen

    #    Welcome Label
        ctk.CTkLabel(self.loader_frame, text=f"Welcome back, {user_name}", 
                     font=("Roboto", 26, "bold"), text_color="#0A2647").pack(pady=(200, 10))
        
        ctk.CTkLabel(self.loader_frame, text="Setting up your dashboard...", 
                     font=("Arial", 14), text_color="gray").pack(pady=(0, 30))

        # Progress Bar
        self.progress = ctk.CTkProgressBar(self.loader_frame, width=400, height=15, progress_color="#0A2647", orientation="horizontal")
        self.progress.pack()
        self.progress.configure(mode="indeterminate")
        self.progress.start()

        # Simulate loading delay
        self.update()

        # Launch Dashboard 
        self.after(100, lambda: self.launch_dashboard(role, user_id, user_name))

    # def launch_dashboard(self, role, user_id, user_name):
    #     try:
    #         # Note: Hum ab password pass nahi kar rahe hain kyunki main.py Cloud use karega.
    #         # Lekin Argument order maintain karne ke liye dummy strings bhej rahe hain.
            
    #         subprocess.Popen([
    #             sys.executable, "main.py", 
    #             role, 
    #             str(user_id), 
    #             "cloud_db_placeholder",  # Dummy DB Name
    #             "cloud_pass_placeholder", # Dummy Password
    #             str(user_name)
    #         ])
            
    #         self.after(3000, self.destroy)
            
    #     except Exception as e:
    #         messagebox.showerror("Error", f"Could not open Main File: {e}")
    #         self.destroy()
    def launch_dashboard(self, role, user_id, user_name):
        try:
            # 1. Login Window ko band karein
            self.destroy()

            # 2. Main Dashboard ko direct import karein
            from main import MainDashboard

            # 3. Dashboard start karein
            # Hum wahi arguments pass kar rahe hain jo main.py maangta hai
            app = MainDashboard(
                user_role=role, 
                user_id=str(user_id), 
                current_user=str(user_name)
            )
            app.mainloop()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Dashboard: {e}")

    # Login Function
    def login_function(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "All fields are required.")
            return

        conn = None
        try:
            # --- UPDATE: Using Cloud Connection ---
            conn = connect_to_cloud()
            cursor = conn.cursor()
            
            # CHECK SUPER ADMIN
            cursor.execute("SELECT id, username FROM user_credentials WHERE username=%s AND password=%s AND role='super_admin'", (username, password))
            admin_data = cursor.fetchone()

            if admin_data:
                self.show_loading_screen('super_admin', admin_data[0], "Super Admin")
                return
            
            # CHECK TEACHER
            cursor.execute("SELECT Teacher_ID, Username FROM teacher WHERE Username=%s AND Password=%s", (username, password))
            teacher_data = cursor.fetchone()

            if teacher_data:
                self.launch_dashboard('admin', teacher_data[0], teacher_data[1])
                return

            # CHECK STUDENT
            cursor.execute("SELECT Student_ID, Name, Roll_No FROM student WHERE Roll_No=%s AND DOB=%s", (username, password))
            student_data = cursor.fetchone()

            if student_data:
                self.show_loading_screen('student', student_data[2], student_data[1])
                return

            messagebox.showerror("Failed", "Invalid Credentials")

        except Exception as e:
            messagebox.showerror("Database Error", f"Connection failed: {e}")
        finally:
            if conn:
                conn.close()

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()