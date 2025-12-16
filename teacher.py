import customtkinter as ctk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import sys
# --- UPDATE: Import Cloud Connection ---
from config import get_db_connection as connect_to_cloud

# --- Theme Settings ---
ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")

# Note: DB Credentials ab config.py se handle honge.
if len(sys.argv) > 4:
    # Just accepting args to prevent errors, but won't use them for connection
    pass

class TeacherManagement(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Teacher Management")
        self.geometry("1000x650")
        self.after(10, lambda: self.state('zoomed'))
        self.COLOR_PRIMARY = "#0A2647"
        
        # --- UPDATE: Removed self.db_config (Localhost) ---
        
        self.var_phone = ctk.StringVar()
        self.var_dept = ctk.StringVar(value="CSE")
        self.var_user = ctk.StringVar()
        self.var_pass = ctk.StringVar()
        self.selected_id = None

        self.create_widgets()
        self.fetch_data()

    # --- UPDATE: Cloud Connection ---
    def get_db_connection(self):
        return connect_to_cloud()

    def create_widgets(self):
        header = ctk.CTkFrame(self, fg_color=self.COLOR_PRIMARY, height=70, corner_radius=0); header.pack(fill="x")
        ctk.CTkButton(header, text="← Back", command=self.destroy, width=80, height=30, fg_color="#E74C3C", hover_color="#C0392B").place(relx=0.02, rely=0.5, anchor="w")
        ctk.CTkLabel(header, text="EMPLOYEE REGISTRATION", font=("Roboto", 24, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        main_frame = ctk.CTkFrame(self, fg_color="#F5F7F9"); main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        left_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=15, width=400); left_frame.pack(side="left", fill="y", padx=(0, 20)); left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="Add New Teacher", font=("Arial", 18, "bold"), text_color=self.COLOR_PRIMARY).pack(pady=20)
        
        ctk.CTkLabel(left_frame, text="Username (Login ID):", font=("Arial", 12)).pack(anchor="w", padx=30)
        ctk.CTkEntry(left_frame, textvariable=self.var_user, width=340).pack(pady=(5, 15), padx=30)

        ctk.CTkLabel(left_frame, text="Password:", font=("Arial", 12)).pack(anchor="w", padx=30)
        ctk.CTkEntry(left_frame, textvariable=self.var_pass, width=340).pack(pady=(5, 15), padx=30)

        ctk.CTkLabel(left_frame, text="Department:", font=("Arial", 12)).pack(anchor="w", padx=30)
        ctk.CTkComboBox(left_frame, variable=self.var_dept, values=["CSE", "IT", "Civil", "Mech", "Science", "Arts"], width=340).pack(pady=(5, 15), padx=30)

        ctk.CTkLabel(left_frame, text="Phone:", font=("Arial", 12)).pack(anchor="w", padx=30)
        ctk.CTkEntry(left_frame, textvariable=self.var_phone, width=340).pack(pady=(5, 25), padx=30)

        ctk.CTkButton(left_frame, text="REGISTER", command=self.add_data, fg_color="#2ecc71", height=40, width=340).pack(pady=5, padx=30)
        ctk.CTkButton(left_frame, text="UPDATE", command=self.update_data, fg_color="#3498db", height=40, width=340).pack(pady=5, padx=30)
        ctk.CTkButton(left_frame, text="DELETE", command=self.delete_data, fg_color="#e74c3c", height=40, width=340).pack(pady=5, padx=30)
        ctk.CTkButton(left_frame, text="CLEAR", command=self.reset_data, fg_color="gray", height=40, width=340).pack(pady=5, padx=30)

        right_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=15); right_frame.pack(side="right", fill="both", expand=True)
        cols = ("id", "user", "dept", "phone", "pass")
        self.table = ttk.Treeview(right_frame, columns=cols, show="headings")
        self.table.heading("id", text="ID"); self.table.column("id", width=40)
        self.table.heading("user", text="Username"); self.table.column("user", width=120)
        self.table.heading("dept", text="Dept"); self.table.column("dept", width=80)
        self.table.heading("phone", text="Phone"); self.table.column("phone", width=100)
        self.table.heading("pass", text="Password"); self.table.column("pass", width=100)
        
        self.table.pack(fill="both", expand=True, padx=20, pady=20); self.table.bind("<ButtonRelease>", self.get_cursor)

    def fetch_data(self):
        try:
            conn = self.get_db_connection(); cursor = conn.cursor()
            cursor.execute("SELECT Teacher_ID, Username, Department, Phone, Password FROM teacher")
            rows = cursor.fetchall()
            self.table.delete(*self.table.get_children())
            for row in rows: self.table.insert("", END, values=row)
            conn.close()
        except Exception as e: messagebox.showerror("Error", str(e))

    def add_data(self):
        if self.var_user.get() == "": messagebox.showerror("Error", "Username required"); return
        try:
            conn = self.get_db_connection(); cursor = conn.cursor()
            cursor.execute("INSERT INTO teacher (Username, Phone, Department, Password) VALUES (%s,%s,%s,%s)", 
                           (self.var_user.get(), self.var_phone.get(), self.var_dept.get(), self.var_pass.get()))
            conn.commit(); conn.close(); self.fetch_data(); self.reset_data(); messagebox.showinfo("Success", "Teacher Registered!")
        except Exception as e: messagebox.showerror("Error", str(e))

    def update_data(self):
        if not self.selected_id: return
        try:
            conn = self.get_db_connection(); cursor = conn.cursor()
            cursor.execute("UPDATE teacher SET Username=%s, Phone=%s, Department=%s, Password=%s WHERE Teacher_ID=%s", 
                           (self.var_user.get(), self.var_phone.get(), self.var_dept.get(), self.var_pass.get(), self.selected_id))
            conn.commit(); conn.close(); self.fetch_data(); messagebox.showinfo("Updated", "Details Updated.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def delete_data(self):
        if not self.selected_id: return
        if messagebox.askyesno("Confirm", "Delete Teacher?"):
            try:
                conn = self.get_db_connection(); cursor = conn.cursor()
                cursor.execute("DELETE FROM teacher WHERE Teacher_ID=%s", (self.selected_id,))
                conn.commit(); conn.close(); self.fetch_data(); self.reset_data()
            except: pass

    def get_cursor(self, event):
        row = self.table.item(self.table.focus())['values']
        if row: self.selected_id = row[0]; self.var_user.set(row[1]); self.var_dept.set(row[2]); self.var_phone.set(row[3]); self.var_pass.set(row[4])

    def reset_data(self):
        self.var_user.set(""); self.var_phone.set(""); self.var_pass.set(""); self.selected_id = None

if __name__ == "__main__":
    app = ctk.CTk(); app.withdraw(); TeacherManagement(); app.mainloop()