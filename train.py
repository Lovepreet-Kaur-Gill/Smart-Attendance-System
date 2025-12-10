import customtkinter as ctk
from tkinter import messagebox
import cv2
import face_recognition # type: ignore
import pickle
import os
import sys
import glob
import time
from datetime import datetime

ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")

# Global Config
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

# constants
DATA_DIR = "student_images"
MODEL_FILE = "encodings.pickle"

class TrainWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)

        # Access Control
        if USER_ROLE != "admin" and USER_ROLE != "super_admin":
            messagebox.showerror("Access Denied", "Only Teachers/Admins can access the Training Module.")
            sys.exit(0)

        self.title("AI Training Center")
        self.geometry("1200x720")
        self.after(10, lambda: self.state('zoomed'))

        try:
            icon_path = os.path.abspath("images/app_icon.ico")
            self.iconbitmap(icon_path)
            self.after(200, lambda: self.iconbitmap(icon_path))
            
        except Exception as e:
            print(f"Icon Error: {e}") 
        
        self.after(0, lambda: self.state('zoomed')) 
        
        self.COLOR_PRIMARY = "#0A2647"
        self.COLOR_ACCENT = "#2ecc71" 
        self.COLOR_BG = "#F5F7F9"
        self.COLOR_CARD = "white"
        
        self.configure(fg_color=self.COLOR_BG)

        self.create_ui()
        self.check_system_status()

    def create_ui(self):
        header = ctk.CTkFrame(self, fg_color=self.COLOR_PRIMARY, height=80, corner_radius=0)
        header.pack(fill="x")
        
        btn_back = ctk.CTkButton(header, text="← Back", command=self.destroy, 
                                 width=80, height=30, fg_color="#E74C3C", hover_color="#C0392B")
        btn_back.place(relx=0.02, rely=0.5, anchor="w") 
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(title_frame, text=" MODEL TRAINING CENTER", font=("Roboto", 28, "bold"), text_color="white").pack()
        
        main_grid = ctk.CTkFrame(self, fg_color="transparent")
        main_grid.pack(fill="both", expand=True, padx=40, pady=40)
        main_grid.columnconfigure(0, weight=1) 
        main_grid.columnconfigure(1, weight=2)

        # left side
        status_card = ctk.CTkFrame(main_grid, fg_color=self.COLOR_CARD, corner_radius=15)
        status_card.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        ctk.CTkLabel(status_card, text="SYSTEM STATUS", font=("Roboto", 18, "bold"), text_color="#555").pack(pady=(30, 20))

        stats_frame = ctk.CTkFrame(status_card, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30)

        self.lbl_total_img = self.create_stat_row(stats_frame, "Total Photos Found:", "0")
        self.lbl_total_students = self.create_stat_row(stats_frame, "Unique Students:", "0")
        self.lbl_model_status = self.create_stat_row(stats_frame, "Model State:", "Checking...", color="orange")
        self.lbl_last_update = self.create_stat_row(stats_frame, "Last Updated:", "Never")

        # divider
        ctk.CTkFrame(status_card, height=2, fg_color="#E0E0E0").pack(fill="x", padx=30, pady=30)

        # btns
        ctk.CTkLabel(status_card, text="ACTIONS", font=("Roboto", 14, "bold"), text_color="#555").pack(anchor="w", padx=30)
        
        self.btn_train = ctk.CTkButton(status_card, text="START TRAINING", command=self.start_training,
                                       font=("Roboto", 16, "bold"), fg_color=self.COLOR_PRIMARY, hover_color="#144272",
                                       height=50)
        self.btn_train.pack(fill="x", padx=30, pady=(15, 10))

        self.btn_delete = ctk.CTkButton(status_card, text="RESET MODEL", command=self.delete_model,
                                        font=("Roboto", 14, "bold"), fg_color="#E74C3C", hover_color="#C0392B",
                                        height=40)
        self.btn_delete.pack(fill="x", padx=30, pady=10)


        # right side 
        console_card = ctk.CTkFrame(main_grid, fg_color=self.COLOR_CARD, corner_radius=15)
        console_card.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(console_card, text="TRAINING LOGS", font=("Roboto", 18, "bold"), text_color="#555").pack(anchor="w", padx=30, pady=(30, 10))

        # Terminal Box
        self.log_box = ctk.CTkTextbox(console_card, font=("Consolas", 12), fg_color="#1e1e1e", text_color="#00ff00", corner_radius=10)
        self.log_box.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        self.log("System Initialized. Ready to train.")

        # progres bar
        progress_frame = ctk.CTkFrame(console_card, fg_color="transparent")
        progress_frame.pack(fill="x", padx=30, pady=(0, 30))
        
        self.lbl_progress = ctk.CTkLabel(progress_frame, text="Progress: 0%", font=("Arial", 12, "bold"), text_color="#555")
        self.lbl_progress.pack(anchor="w")
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=15, corner_radius=8, progress_color=self.COLOR_ACCENT)
        self.progress_bar.pack(fill="x", pady=(5, 0))
        self.progress_bar.set(0)

    def create_stat_row(self, parent, title, value, color="#333"):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=8)
        ctk.CTkLabel(frame, text=title, font=("Arial", 14), text_color="gray").pack(side="left")
        lbl_val = ctk.CTkLabel(frame, text=value, font=("Arial", 14, "bold"), text_color=color)
        lbl_val.pack(side="right")
        return lbl_val

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S]")
        self.log_box.insert("end", f"{timestamp} > {message}\n")
        self.log_box.see("end")
        self.update_idletasks()

    def check_system_status(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            
        images = glob.glob(os.path.join(DATA_DIR, "*.jpg"))
        try:
            student_ids = set([os.path.basename(f).split('.')[0] for f in images])
        except:
            student_ids = []
        
        self.lbl_total_img.configure(text=str(len(images)))
        self.lbl_total_students.configure(text=str(len(student_ids)))

        #chk model file 
        if os.path.exists(MODEL_FILE):
            self.lbl_model_status.configure(text="Ready (Trained)", text_color="green")
            mod_time = os.path.getmtime(MODEL_FILE)
            self.lbl_last_update.configure(text=datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M'))
            self.btn_train.configure(text="RE-TRAIN MODEL")
        else:
            self.lbl_model_status.configure(text="Not Found", text_color="red")
            self.lbl_last_update.configure(text="Never")

    def delete_model(self):
        if not os.path.exists(MODEL_FILE):
            messagebox.showinfo("Info", "No model file found to delete.")
            return
            
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to delete the trained model? You will need to re-train."):
            try:
                os.remove(MODEL_FILE)
                self.log("Model file deleted.")
                self.check_system_status()
                messagebox.showinfo("Deleted", "Model has been reset.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def start_training(self):
        image_paths = glob.glob(os.path.join(DATA_DIR, "*.jpg"))
        
        if len(image_paths) == 0:
            messagebox.showerror("Error", "No images found! Please register students first.")
            return

        self.btn_train.configure(state="disabled", text="TRAINING IN PROGRESS...", fg_color="#F39C12")
        self.btn_delete.configure(state="disabled")
        self.log("----------------------------------------")
        self.log("Starting Dlib Training Process...")
        self.progress_bar.set(0)
        
        known_encodings = []
        known_ids = []
        total = len(image_paths)
        processed_count = 0
        start_time = time.time()

        for index, file_path in enumerate(image_paths):
            try:
                filename = os.path.basename(file_path)
                student_id = os.path.splitext(filename)[0] # Get Roll No
                
                self.log(f"Processing Roll No: {student_id}...")

                # Load Image
                image = cv2.imread(file_path)
                if image is None:
                    self.log(f"FAILED: Could not read {filename}")
                    continue
                # converting to rgb 
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # detecting faces
                boxes = face_recognition.face_locations(rgb_image, model="hog")
                
                # generate encode
                encodings = face_recognition.face_encodings(rgb_image, boxes)

                if len(encodings) > 0:
                    known_encodings.append(encodings[0])
                    known_ids.append(student_id)
                    processed_count += 1
                else:
                    self.log(f"WARNING: No face found in {filename}. Skipping.")

                # updating Progress
                progress_val = (index + 1) / total
                self.progress_bar.set(progress_val)
                self.lbl_progress.configure(text=f"Progress: {int(progress_val * 100)}%")
                self.update_idletasks()

            except Exception as e:
                self.log(f"ERROR: {str(e)}")

        self.log("Saving model file...")
        data = {"encodings": known_encodings, "ids": known_ids}
        
        try:
            with open(MODEL_FILE, "wb") as f:
                pickle.dump(data, f)
            
            duration = round(time.time() - start_time, 2)
            self.log("----------------------------------------")
            self.log(f"TRAINING COMPLETE!")
            self.log(f"Time Taken: {duration} seconds")
            self.log(f"Students Trained: {processed_count} / {total}")
            
            messagebox.showinfo("Success", "Training Completed Successfully!")
            
        except Exception as e:
            self.log(f"CRITICAL ERROR SAVING FILE: {str(e)}")
            messagebox.showerror("Save Error", str(e))

        self.check_system_status()
        self.btn_train.configure(state="normal", text="TRAIN AGAIN", fg_color=self.COLOR_PRIMARY)
        self.btn_delete.configure(state="normal")

if __name__ == "__main__":
    app = TrainWindow()
    app.mainloop()