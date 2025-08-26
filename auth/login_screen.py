import tkinter as tk
from tkinter import ttk, messagebox
import threading
from PIL import Image, ImageTk
import os

class LoginScreen:
    def __init__(self, root, login_manager, on_success_callback):
        self.root = root
        self.login_manager = login_manager
        self.on_success_callback = on_success_callback
        self.login_window = None
        self.is_logging_in = False
        
    def show_login(self):
        # Create login window
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login - Sistem Manajemen Muda-Mudi")
        self.login_window.geometry("500x650")
        self.login_window.configure(bg='#1976D2')
        self.login_window.transient(self.root)
        self.login_window.grab_set()
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.login_window.resizable(True, True)
        self.login_window.minsize(450, 600)
        
        # Center the window
        self.login_window.update_idletasks()
        screen_width = self.login_window.winfo_screenwidth()
        screen_height = self.login_window.winfo_screenheight()
        window_width = 500
        window_height = 650
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.login_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        self.create_login_ui()
        
        # Focus on username field
        self.username_entry.focus_set()
        
        # Bind Enter key to login
        self.login_window.bind('<Return>', lambda e: self.perform_login())
        
    def create_login_ui(self):
        # Main container
        main_frame = tk.Frame(self.login_window, bg='#1976D2')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Logo/Icon section
        logo_frame = tk.Frame(main_frame, bg='#1976D2')
        logo_frame.pack(pady=(0, 30))
        
        # App icon
        tk.Label(logo_frame, text="🕌", font=('Arial', 48), bg='#1976D2', fg='white').pack()
        
        # Title
        tk.Label(logo_frame, text="SISTEM MANAJEMEN\nMUDA-MUDI", 
                font=('Arial', 16, 'bold'), bg='#1976D2', fg='white', justify='center').pack(pady=(10, 5))
        
        tk.Label(logo_frame, text="Cengkareng Jakarta Barat", 
                font=('Arial', 10), bg='#1976D2', fg='#BBDEFB').pack()
        
        # Login form container
        form_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        form_frame.pack(fill='x', pady=(20, 0))
        
        # Form content
        form_content = tk.Frame(form_frame, bg='white')
        form_content.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Login title
        tk.Label(form_content, text="Masuk ke Sistem", 
                font=('Arial', 14, 'bold'), bg='white', fg='#1976D2').pack(pady=(0, 20))
        
        # Username field
        tk.Label(form_content, text="Username:", 
                font=('Arial', 10), bg='white', fg='#333').pack(anchor='w', pady=(0, 5))
        
        self.username_entry = tk.Entry(form_content, font=('Arial', 11), relief='solid', bd=1)
        self.username_entry.pack(fill='x', pady=(0, 15), ipady=8)
        
        # Password field
        tk.Label(form_content, text="Password:", 
                font=('Arial', 10), bg='white', fg='#333').pack(anchor='w', pady=(0, 5))
        
        self.password_entry = tk.Entry(form_content, font=('Arial', 11), show='*', relief='solid', bd=1)
        self.password_entry.pack(fill='x', pady=(0, 15), ipady=8)
        
        # Remember me checkbox
        self.remember_var = tk.BooleanVar()
        remember_frame = tk.Frame(form_content, bg='white')
        remember_frame.pack(fill='x', pady=(0, 20))
        
        tk.Checkbutton(remember_frame, text="Ingat saya", variable=self.remember_var,
                      bg='white', fg='#666', font=('Arial', 9)).pack(anchor='w')
        
        # Login button
        self.login_btn = tk.Button(form_content, text="Masuk", 
                                  command=self.perform_login,
                                  bg='#1976D2', fg='white', font=('Arial', 11, 'bold'),
                                  relief='flat', cursor='hand2')
        self.login_btn.pack(fill='x', pady=(0, 15), ipady=10)
        
        # Status label
        self.status_label = tk.Label(form_content, text="", 
                                    font=('Arial', 9), bg='white', fg='red')
        self.status_label.pack(pady=(0, 10))
        
        # Connection status
        self.connection_label = tk.Label(form_content, text="🔗 Memeriksa koneksi...", 
                                        font=('Arial', 8), bg='white', fg='#666')
        self.connection_label.pack()
        
        # Check connection status
        self.check_connection()
        
        # Footer
        footer_frame = tk.Frame(main_frame, bg='#1976D2')
        footer_frame.pack(side='bottom', fill='x', pady=(20, 0))
        
        tk.Label(footer_frame, text="© 2024 Sistem Manajemen Muda-Mudi", 
                font=('Arial', 8), bg='#1976D2', fg='#BBDEFB').pack()
    
    def check_connection(self):
        """Check connection to API server"""
        def check():
            try:
                import requests
                response = requests.get(f"{self.login_manager.api_base_url}/api/auth/verify", timeout=5)
                self.connection_label.config(text="🟢 Terhubung ke server", fg='green')
            except:
                self.connection_label.config(text="🔴 Tidak dapat terhubung ke server", fg='red')
        
        threading.Thread(target=check, daemon=True).start()
    
    def perform_login(self):
        """Perform login process"""
        if self.is_logging_in:
            return
        
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.status_label.config(text="Username dan password harus diisi!", fg='red')
            return
        
        # Disable login button and show loading
        self.is_logging_in = True
        self.login_btn.config(state='disabled', text='Sedang masuk...')
        self.status_label.config(text="🔄 Memverifikasi kredensial...", fg='blue')
        
        # Perform login in separate thread
        def login_thread():
            success, message = self.login_manager.login(username, password)
            
            # Update UI in main thread
            self.root.after(0, lambda: self.handle_login_result(success, message))
        
        threading.Thread(target=login_thread, daemon=True).start()
    
    def handle_login_result(self, success, message):
        """Handle login result in main thread"""
        self.is_logging_in = False
        self.login_btn.config(state='normal', text='Masuk')
        
        if success:
            self.status_label.config(text="✅ Login berhasil!", fg='green')
            
            # Show success message briefly
            self.root.after(1000, self.close_and_continue)
        else:
            self.status_label.config(text=f"❌ {message}", fg='red')
            # Clear password field on error
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus_set()
    
    def close_and_continue(self):
        """Close login window and continue to main app"""
        if self.login_window:
            self.login_window.destroy()
            self.login_window = None
        
        # Call success callback
        if self.on_success_callback:
            self.on_success_callback()
    
    def on_close(self):
        """Handle window close event"""
        if self.is_logging_in:
            if messagebox.askyesno("Konfirmasi", "Login sedang berlangsung. Yakin ingin keluar?"):
                self.root.quit()
        else:
            self.root.quit()
    
    def show_offline_mode_dialog(self):
        """Show dialog for offline mode option"""
        result = messagebox.askyesno(
            "Koneksi Gagal", 
            "Tidak dapat terhubung ke server.\n\nApakah Anda ingin melanjutkan dalam mode offline?\n\n"
            "Catatan: Beberapa fitur mungkin tidak tersedia dalam mode offline."
        )
        
        if result:
            # Continue in offline mode
            self.close_and_continue()
        else:
            # Exit application
            self.root.quit()