import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import io
from database import initialize_db, verify_login 
from dashboard import DashboardFrame
from flowers import FlowerFrame
from customers import CustomersFrame
from staff import StaffFrame
import

initialize_db()

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Flowerina — Login")
        self.geometry("420x500")
        self.resizable(False, False)
        self._build()

     def _build(self):
        ctk.CTkLabel(self, text="📚 Flowerina", font=("Arial", 28, "bold")).pack(pady=(60, 5))
        ctk.CTkLabel(self, text="Sign in to continue", font=("Arial", 14), text_color="gray").pack(pady=(0, 30))

        self.username = ctk.CTkEntry(self, placeholder_text="Username", width=280, height=45)
        self.username.pack(pady=8)

        self.password = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=280, height=45)
        self.password.pack(pady=8)

        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack(pady=4)

        ctk.CTkButton(self, text="Login", width=280, height=45, command=self.login).pack(pady=10)

        self.theme_btn = ctk.CTkButton(self, text="🌙 Dark Mode", width=140, fg_color="transparent",
                                        border_width=1, command=self.toggle_theme)
        self.theme_btn.pack(pady=(20, 0))

    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="🌙 Dark Mode")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="☀️ Light Mode")

    def login(self):
        user = self.username.get().strip()
        pwd = self.password.get().strip()
        staff = verify_login(user, pwd)
        if staff:
            self.destroy()
            app = MainWindow(staff)
            app.mainloop()
        else:
            self.error_label.configure(text="Invalid username or password.")

class MainWindow(ctk.CTk):
    def __init__(self, staff):
        super().__init__()
        self.staff = staff
        self.title(f"Flowerina — {staff['name']} ({staff['role']})")
        self.geometry("1100x680")
        self.minsize(900, 600)
        self._build()

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(sidebar, text="📚 MyLibrary", font=("Arial", 18, "bold")).grid(row=0, column=0, pady=(20,10), padx=20)
        ctk.CTkLabel(sidebar, text=f"Hello, {self.staff['name']}", font=("Arial", 12), text_color="gray").grid(row=1, column=0, pady=(0,20), padx=20)

        self.frames = {}
        nav_items = [
            ("🏠  Dashboard", "dashboard"),
            ("📖  Books", "books"),
            ("👥  Members", "members"),
            ("🪪  Staff", "staff"),
        ]

        self.nav_buttons = {}
        for i, (label, key) in enumerate(nav_items):
            btn = ctk.CTkButton(sidebar, text=label, anchor="w", fg_color="transparent",
                                text_color=("black", "white"), hover_color=("gray85", "gray25"),
                                command=lambda k=key: self.show_frame(k))
            btn.grid(row=i+2, column=0, padx=10, pady=4, sticky="ew")
            self.nav_buttons[key] = btn

        # Theme toggle in sidebar
        self.theme_btn = ctk.CTkButton(sidebar, text="🌙 Dark", fg_color="transparent",
                                        border_width=1, command=self.toggle_theme)
        self.theme_btn.grid(row=7, column=0, padx=10, pady=4, sticky="ew")

        # Logout
        ctk.CTkButton(sidebar, text="🚪 Logout", fg_color="transparent", border_width=1,
                      text_color="red", hover_color=("gray85", "gray25"),
                      command=self.logout).grid(row=8, column=0, padx=10, pady=(4,20), sticky="ew")

        # Main content area
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # Load frames
        self.frames["dashboard"] = DashboardFrame(self.content, self.staff)
        self.frames["books"]     = BooksFrame(self.content, self.staff)
        self.frames["members"]   = MembersFrame(self.content, self.staff)
        self.frames["staff"]     = StaffFrame(self.content, self.staff)

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("dashboard")

    def show_frame(self, key):
        for k, btn in self.nav_buttons.items():
            btn.configure(fg_color="transparent")
        self.nav_buttons[key].configure(fg_color=("gray75", "gray30"))
        self.frames[key].tkraise()
        if hasattr(self.frames[key], "refresh"):
            self.frames[key].refresh()

    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="🌙 Dark")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="☀️ Light")

    def logout(self):
        self.destroy()
        app = LoginWindow()
        app.mainloop()


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()

