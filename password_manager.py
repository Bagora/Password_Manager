import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from cryptography.fernet import Fernet
import json
import os

# Hidden folder for storing files
HIDDEN_FOLDER = ".password_manager"
PASSWORD_FILE = os.path.join(HIDDEN_FOLDER, "passwords.json")
MASTER_PASSWORD_FILE = os.path.join(HIDDEN_FOLDER, "master_password.txt")
KEY_FILE = os.path.join(HIDDEN_FOLDER, "key.key")

# Ensure the hidden folder exists
if not os.path.exists(HIDDEN_FOLDER):
    os.makedirs(HIDDEN_FOLDER)
    # Hide folder on Windows
    if os.name == "nt":
        os.system(f'attrib +h "{HIDDEN_FOLDER}"')

# Generate encryption key if it doesn't exist
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(Fernet.generate_key())

# Load the encryption key
with open(KEY_FILE, "rb") as key_file:
    key = key_file.read()
cipher = Fernet(key)

# Load or set the master password
def load_master_password():
    global MASTER_PASSWORD, SECURITY_ANSWER
    if os.path.exists(MASTER_PASSWORD_FILE):
        with open(MASTER_PASSWORD_FILE, "r") as file:
            data = json.load(file)
            MASTER_PASSWORD = cipher.decrypt(data["password"].encode()).decode()
            SECURITY_ANSWER = cipher.decrypt(data["security_answer"].encode()).decode()
    else:
        MASTER_PASSWORD = None
        SECURITY_ANSWER = None

load_master_password()  # Load master password at start

# Encrypt and decrypt functions
def encrypt_password(password):
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    return cipher.decrypt(encrypted_password.encode()).decode()

# Save master password with security answer
def set_master_password():
    global MASTER_PASSWORD, SECURITY_ANSWER
    MASTER_PASSWORD = simpledialog.askstring("Set Master Password", "Enter a new master password:", show="*")
    security_answer = simpledialog.askstring("Security Phrase", "Enter Your Security Phrase")
    
    if MASTER_PASSWORD and security_answer:
        encrypted_password = encrypt_password(MASTER_PASSWORD)
        encrypted_answer = encrypt_password(security_answer)
        
        with open(MASTER_PASSWORD_FILE, "w") as file:
            json.dump({"password": encrypted_password, "security_answer": encrypted_answer}, file)
        messagebox.showinfo("Success", "Master password set successfully.")
        restart_app()
    else:
        messagebox.showerror("Error", "Master password and security phrase cannot be empty!")

# Save and load password functions
def save_password_to_file(domain, link, password):
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "r") as file:
            passwords = json.load(file)
    else:
        passwords = {}
    
    encrypted_password = encrypt_password(password)
    passwords[domain] = {"link": link, "password": encrypted_password}
    
    try:
        with open(PASSWORD_FILE, "w") as file:
            json.dump(passwords, file, indent=4)
        messagebox.showinfo("Success", "Password saved successfully.")
    except PermissionError:
        messagebox.showerror("Error", "Permission denied: Unable to write to the passwords file.")
    
    clear_entries()

def load_passwords_from_file():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "r") as file:
            passwords = json.load(file)
            decrypted_passwords = {
                domain: {
                    "link": data["link"],
                    "password": decrypt_password(data["password"]),
                } for domain, data in passwords.items()
            }
            return decrypted_passwords
    else:
        return {}

def change_master_password():
    security_answer = simpledialog.askstring("Enter Password Reset Phrase", "Enter Your Security Phrase")
    
    # Compare the entered phrase with the decrypted stored security phrase
    if security_answer and security_answer == SECURITY_ANSWER:
        new_password = simpledialog.askstring("New Password", "Enter new master password:", show="*")
        
        if new_password:
            encrypted_password = encrypt_password(new_password)
            encrypted_answer = encrypt_password(SECURITY_ANSWER)  # Re-encrypt the security phrase
            with open(MASTER_PASSWORD_FILE, "w") as file:
                json.dump({"password": encrypted_password, "security_answer": encrypted_answer}, file)
            messagebox.showinfo("Success", "Master password changed successfully.")
            restart_app()
        else:
            messagebox.showerror("Error", "New password cannot be empty!")
    else:
        messagebox.showerror("Error", "Incorrect security phrase!")

def restart_app():
    global master_login, app
    
    if 'master_login' in globals() and master_login:
        try:
            master_login.destroy()
        except tk.TclError:
            pass
    
    if 'app' in globals() and app:
        try:
            app.destroy()
        except tk.TclError:
            pass
    
    load_master_password()
    main()

# Main application window functions
def main_window():
    main = tk.Tk()
    main.title("Password Manager")
    main.geometry("600x600")
    return main

def save_password():
    domain = domain_entry.get()
    link = link_entry.get()
    password = password_entry.get()
    
    if not domain or not password:
        messagebox.showerror("Error", "Please fill out all fields.")
        return
    
    save_password_to_file(domain, link, password)

def view_passwords():
    passwords = load_passwords_from_file()
    
    for widget in password_list_frame.winfo_children():
        widget.destroy()
    
    columns = ("Domain", "Link", "Password")
    tree = ttk.Treeview(password_list_frame, columns=columns, show="headings")
    tree.heading("Domain", text="Domain")
    tree.heading("Link", text="Link")
    tree.heading("Password", text="Password")
    tree.column("Domain", width=150)
    tree.column("Link", width=150)
    tree.column("Password", width=150)
    scrollbar = ttk.Scrollbar(password_list_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)
    for domain, data in passwords.items():
        tree.insert("", "end", values=(domain, data["link"], data["password"]))

def clear_entries():
    domain_entry.delete(0, tk.END)
    link_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)

def show_about():
    about_window = tk.Toplevel()
    about_window.title("About")
    about_window.geometry("400x270")

    tk.Label(about_window, text="Password Manager v1.0 Using Tkinter and Cryptography.", font=("Arial", 10, "bold")).pack(pady=10)
    tk.Label(about_window, text="Visit https://github.com/Bagora/Password_Manager for more info.", font=("Arial", 10)).pack(pady=5)
    tk.Label(about_window, text="Secure your data with a master password.", font=("Arial", 10)).pack(pady=5)

    canvas = tk.Canvas(about_window, width=200, height=100)
    canvas.pack(pady=10)
    canvas.create_text(20, 50, text="P", font=("Arial", 18, "bold"), fill="blue")
    canvas.create_text(50, 50, text="Y", font=("Arial", 24, "bold"), fill="black")
    canvas.create_text(80, 50, text="T", font=("Arial", 18, "bold"), fill="blue")
    canvas.create_text(110, 50, text="H", font=("Arial", 24, "bold"), fill="black")
    canvas.create_text(140, 50, text="O", font=("Arial", 18, "bold"), fill="blue")
    canvas.create_text(170, 50, text="N", font=("Arial", 24, "bold"), fill="black")

    tk.Button(about_window, text="Close", command=about_window.destroy).pack(pady=10)

def login():
    if master_password_entry.get() == MASTER_PASSWORD:
        master_login.destroy()
        open_manager()
    else:
        messagebox.showerror("Error", "Invalid master password!")

def open_manager():
    global domain_entry, link_entry, password_entry, password_list_frame, app
    app = main_window()
    tk.Label(app, text="Domain:").pack(pady=20)
    domain_entry = tk.Entry(app)
    domain_entry.pack()
    tk.Label(app, text="Link:").pack(pady=20)
    link_entry = tk.Entry(app)
    link_entry.pack()
    tk.Label(app, text="Password:").pack(pady=20)
    password_entry = tk.Entry(app, show="*")
    password_entry.pack()
    tk.Button(app, text="Save Password", command=save_password).pack(pady=20)
    tk.Button(app, text="View Saved Passwords", command=view_passwords).pack(pady=20)
    tk.Button(app, text="About", command=show_about).pack(pady=10)
    tk.Button(app, text="Logout", command=restart_app).pack(pady=10)
    password_list_frame = tk.Frame(app)
    password_list_frame.pack(fill="both", expand=True)

def main():
    global master_login, master_password_entry
    if not MASTER_PASSWORD:
        set_master_password()
    else:
        master_login = main_window()
        tk.Label(master_login, text="Enter Master Password:").pack(pady=10)
        master_password_entry = tk.Entry(master_login, show="*")
        master_password_entry.pack()
        tk.Button(master_login, text="Login", command=login).pack(pady=10)
        tk.Button(master_login, text="Reset Master Password", command=change_master_password).pack(pady=10)
    master_login.mainloop()

if __name__ == "__main__":
    main()
