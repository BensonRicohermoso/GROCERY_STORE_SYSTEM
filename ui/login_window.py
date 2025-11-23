import tkinter as tk
from tkinter import ttk, messagebox
from modules.users import UserManager
from utils.logs import ActivityLogger
from ui.styles import AppStyles
import config


class LoginWindow:
    """Login window class"""
    
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.current_user = None
        
        # Configure window
        self.root.title(f"{config.APP_CONFIG['app_name']} - Login")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Configure styles
        AppStyles.configure_ttk_styles()
        
        # Create UI
        self.create_widgets()
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create and layout all widgets"""
        # Main container
        main_frame = tk.Frame(self.root, bg=AppStyles.BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Logo/Title area
        title_frame = tk.Frame(main_frame, bg=AppStyles.BACKGROUND)
        title_frame.pack(pady=(0, 40))
        
        # App icon/logo (placeholder)
        icon_label = tk.Label(
            title_frame,
            text="🛒",
            font=('Arial', 72),
            bg=AppStyles.BACKGROUND
        )
        icon_label.pack()
        
        # App title
        title_label = tk.Label(
            title_frame,
            text=config.APP_CONFIG['app_name'],
            font=AppStyles.FONT_HEADER,
            bg=AppStyles.BACKGROUND,
            fg=AppStyles.PRIMARY
        )
        title_label.pack(pady=(10, 5))
        
        # Subtitle
        subtitle_label = tk.Label(
            title_frame,
            text="Please login to continue",
            font=AppStyles.FONT_NORMAL,
            bg=AppStyles.BACKGROUND,
            fg=AppStyles.TEXT_LIGHT
        )
        subtitle_label.pack()
        
        # Login form card
        form_frame = AppStyles.create_card_frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Form padding
        form_inner = tk.Frame(form_frame, bg=AppStyles.WHITE)
        form_inner.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Username field
        username_label = tk.Label(
            form_inner,
            text="Username",
            font=AppStyles.FONT_MEDIUM,
            bg=AppStyles.WHITE,
            fg=AppStyles.TEXT
        )
        username_label.pack(anchor='w', pady=(0, 5))
        
        self.username_entry = ttk.Entry(
            form_inner,
            font=AppStyles.FONT_MEDIUM,
            width=30
        )
        self.username_entry.pack(fill=tk.X, pady=(0, 20))
        self.username_entry.focus()
        
        # Password field
        password_label = tk.Label(
            form_inner,
            text="Password",
            font=AppStyles.FONT_MEDIUM,
            bg=AppStyles.WHITE,
            fg=AppStyles.TEXT
        )
        password_label.pack(anchor='w', pady=(0, 5))
        
        self.password_entry = ttk.Entry(
            form_inner,
            font=AppStyles.FONT_MEDIUM,
            show="●",
            width=30
        )
        self.password_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Show password checkbox
        self.show_password_var = tk.BooleanVar()
        show_password_check = tk.Checkbutton(
            form_inner,
            text="Show password",
            variable=self.show_password_var,
            command=self.toggle_password,
            font=AppStyles.FONT_SMALL,
            bg=AppStyles.WHITE,
            fg=AppStyles.TEXT_LIGHT,
            activebackground=AppStyles.WHITE
        )
        show_password_check.pack(anchor='w', pady=(0, 30))
        
        # Login button
        self.login_button = AppStyles.create_button(
            form_inner,
            text="LOGIN",
            command=self.handle_login,
            style='Primary.TButton'
        )
        self.login_button.pack(fill=tk.X, ipady=10)
        
        # Bind Enter key to login
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.handle_login())
        
        # Version info
        version_label = tk.Label(
            main_frame,
            text=f"Version {config.APP_CONFIG['version']}",
            font=AppStyles.FONT_SMALL,
            bg=AppStyles.BACKGROUND,
            fg=AppStyles.TEXT_LIGHT
        )
        version_label.pack(pady=(20, 0))
    
    def toggle_password(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="●")
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Validate input
        if not username:
            messagebox.showerror("Error", "Please enter username")
            self.username_entry.focus()
            return
        
        if not password:
            messagebox.showerror("Error", "Please enter password")
            self.password_entry.focus()
            return
        
        # Disable button during authentication
        self.login_button.config(state='disabled')
        self.root.config(cursor="watch")
        self.root.update()
        
        try:
            # Authenticate user
            user = UserManager.authenticate(username, password)
            
            if user:
                # Log successful login
                ActivityLogger.log_login(user.user_id, user.username, True)
                
                # Store current user
                self.current_user = user
                
                # Show success message
                messagebox.showinfo(
                    "Login Successful",
                    f"Welcome, {user.full_name}!"
                )
                
                # Close login window and open dashboard
                self.root.destroy()
                self.on_login_success(user)
            else:
                # Log failed login attempt
                ActivityLogger.log_activity(
                    None, 
                    'login_failed', 
                    'user', 
                    None, 
                    f"Failed login attempt for username: {username}"
                )
                
                messagebox.showerror(
                    "Login Failed",
                    "Invalid username or password.\nPlease try again."
                )
                self.password_entry.delete(0, tk.END)
                self.username_entry.focus()
        
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"An error occurred during login:\n{str(e)}"
            )
        
        finally:
            # Re-enable button
            self.login_button.config(state='normal')
            self.root.config(cursor="")
    
    def run(self):
        """Start the login window main loop"""
        self.root.mainloop()


def show_login(on_login_success):
    """
    Show login window
    
    Args:
        on_login_success: Callback function called with User object on successful login
    """
    root = tk.Tk()
    app = LoginWindow(root, on_login_success)
    app.run()