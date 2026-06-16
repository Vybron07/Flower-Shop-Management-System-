import customtkinter as ctk
from database import initialize_db, verify_login
from dashboard import DashboardFrame
from flowers import FlowersFrame
from customers import CustomersFrame
from orders import OrdersFrame
from staff import StaffFrame
from alerts import show_startup_alerts
from occasions import OccasionsFrame

initialize_db()

ORANGE       = "#FF6B2B"
ORANGE_DARK  = "#E5521A"
ORANGE_LIGHT = "#FFF0E8"
WHITE        = "#FFFFFF"
CREAM        = "#FFF8F5"
TEXT_DARK    = "#1A1A1A"
TEXT_GRAY    = "#888888"
BORDER       = "#FFD9C4"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Flowerina — Login")
        self.geometry("860x540")
        self.resizable(False, False)
        self.configure(fg_color=WHITE)
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left orange panel
        left = ctk.CTkFrame(self, fg_color=ORANGE, corner_radius=0, width=380)
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_propagate(False)
        left.grid_rowconfigure(0, weight=1)
        left.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(left, fg_color="transparent")
        inner.grid(row=0, column=0)

        ctk.CTkLabel(inner, text="🌸", font=("Arial", 60)).pack(pady=(0, 8))
        ctk.CTkLabel(inner, text="Flowerina",
                     font=("Georgia", 34, "bold"),
                     text_color=WHITE).pack()
        ctk.CTkLabel(inner, text="Your Flower Shop Manager",
                     font=("Arial", 13),
                     text_color="#FFD9C4").pack(pady=(4, 0))

        ctk.CTkFrame(inner, height=2, fg_color="#FFD9C4",
                     width=160, corner_radius=1).pack(pady=18)

        for line in ["🌹  Manage Inventory", "🛒  Track Orders", "👥  Customer Records"]:
            ctk.CTkLabel(inner, text=line, font=("Arial", 12),
                         text_color="#FFF0E8").pack(pady=3)

        # Right login panel
        right = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.grid(row=0, column=0, padx=50)

        ctk.CTkLabel(form, text="Welcome back 👋",
                     font=("Georgia", 22, "bold"),
                     text_color=TEXT_DARK).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(form, text="Sign in to your account",
                     font=("Arial", 13),
                     text_color=TEXT_GRAY).pack(anchor="w", pady=(0, 24))

        ctk.CTkLabel(form, text="Username", font=("Arial", 12, "bold"),
                     text_color=TEXT_DARK).pack(anchor="w")
        self.username = ctk.CTkEntry(
            form, placeholder_text="Enter username",
            width=280, height=44, corner_radius=8,
            border_color=BORDER, border_width=1,
            fg_color=CREAM, text_color=TEXT_DARK)
        self.username.pack(pady=(4, 14))

        ctk.CTkLabel(form, text="Password", font=("Arial", 12, "bold"),
                     text_color=TEXT_DARK).pack(anchor="w")
        self.password = ctk.CTkEntry(
            form, placeholder_text="Enter password",
            show="*", width=280, height=44, corner_radius=8,
            border_color=BORDER, border_width=1,
            fg_color=CREAM, text_color=TEXT_DARK)
        self.password.pack(pady=(4, 6))

        self.error_label = ctk.CTkLabel(form, text="", text_color="red",
                                        font=("Arial", 11))
        self.error_label.pack(pady=(0, 10))

        ctk.CTkButton(
            form, text="Sign In →", width=280, height=44,
            corner_radius=8, fg_color=ORANGE, hover_color=ORANGE_DARK,
            text_color=WHITE, font=("Arial", 14, "bold"),
            command=self.login).pack()

        ctk.CTkLabel(form, text="Flowerina v2.0  •  © 2025",
                     font=("Arial", 10), text_color=TEXT_GRAY).pack(pady=(28, 0))

        self.password.bind("<Return>", lambda e: self.login())

    def login(self):
        user  = self.username.get().strip()
        pwd   = self.password.get().strip()
        staff = verify_login(user, pwd)
        if staff:
            self.destroy()
            app = MainWindow(staff)
            app.mainloop()
        else:
            self.error_label.configure(text="⚠  Invalid username or password.")


class MainWindow(ctk.CTk):
    def __init__(self, staff):
        super().__init__()
        self.staff = staff
        self.title(f"Flowerina — {self.staff['name']}")
        self.geometry("1150x700")
        self.minsize(950, 620)
        self.configure(fg_color=CREAM)
        self._build()

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=WHITE)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        brand = ctk.CTkFrame(sidebar, fg_color=ORANGE, height=72, corner_radius=0)
        brand.pack(fill="x")
        brand.pack_propagate(False)
        ctk.CTkLabel(brand, text="🌸  Flowerina",
                     font=("Georgia", 17, "bold"),
                     text_color=WHITE).place(relx=0.5, rely=0.5, anchor="center")

        badge = ctk.CTkFrame(sidebar, fg_color=ORANGE_LIGHT, height=52, corner_radius=0)
        badge.pack(fill="x")
        badge.pack_propagate(False)
        role_color = {"admin": ORANGE, "manager": "#4CAF50"}.get(
            (self.staff["role"] or "").lower(), TEXT_GRAY)
        ctk.CTkLabel(badge, text=f"  👤  {self.staff['name']}",
                     font=("Arial", 12, "bold"),
                     text_color=TEXT_DARK).place(x=12, y=8)
        ctk.CTkLabel(badge, text=f"  {self.staff['role'].title()}",
                     font=("Arial", 10),
                     text_color=role_color).place(x=12, y=30)

        ctk.CTkFrame(sidebar, height=1, fg_color=BORDER).pack(fill="x", pady=(8, 4))
        ctk.CTkLabel(sidebar, text="  NAVIGATION",
                     font=("Arial", 9, "bold"),
                     text_color=TEXT_GRAY).pack(anchor="w", padx=16, pady=(0, 4))

        nav_items = [
            ("🏠", "Dashboard",  "dashboard"),
            ("🌸", "Flowers",    "flowers"),
            ("🛒", "Orders",     "orders"),
            ("👥", "Customers",  "customers"),
            ("🪪", "Staff",      "staff"),
            ("🎉", "Occasions",  "occasions"),
        ]

        self.nav_buttons = {}
        for icon, label, key in nav_items:
            btn = ctk.CTkButton(
                sidebar,
                text=f"  {icon}   {label}",
                anchor="w", height=42, corner_radius=8,
                fg_color="transparent", text_color=TEXT_DARK,
                hover_color=ORANGE_LIGHT, font=("Arial", 13),
                command=lambda k=key: self.show_frame(k))
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[key] = btn

        ctk.CTkFrame(sidebar, height=1, fg_color=BORDER).pack(
            fill="x", pady=(12, 8), side="bottom")
        ctk.CTkButton(
            sidebar, text="  🚪   Logout", anchor="w", height=40,
            corner_radius=8, fg_color="transparent",
            text_color="#E53935", hover_color="#FFF0F0",
            font=("Arial", 13),
            command=self.logout).pack(fill="x", padx=10, pady=(0, 12), side="bottom")

        # Topbar
        topbar = ctk.CTkFrame(self, height=56, fg_color=WHITE, corner_radius=0)
        topbar.grid(row=0, column=1, sticky="new")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(0, weight=1)

        self.page_title_label = ctk.CTkLabel(
            topbar, text="Dashboard",
            font=("Georgia", 18, "bold"), text_color=TEXT_DARK)
        self.page_title_label.grid(row=0, column=0, padx=24, sticky="w", pady=14)

        self.theme_btn = ctk.CTkButton(
            topbar, text="🌙", width=36, height=36, corner_radius=8,
            fg_color=ORANGE_LIGHT, hover_color=BORDER,
            text_color=ORANGE, font=("Arial", 16),
            command=self.toggle_theme)
        self.theme_btn.grid(row=0, column=1, padx=(0, 16), pady=10)

        ctk.CTkFrame(self, height=2, fg_color=ORANGE,
                     corner_radius=0).grid(row=0, column=1, sticky="new", pady=(56, 0))

        # Content area
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color=CREAM)
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=(76, 20))
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.frames["dashboard"] = DashboardFrame(self.content, self.staff)
        self.frames["flowers"]   = FlowersFrame(self.content, self.staff)
        self.frames["orders"]    = OrdersFrame(self.content, self.staff)
        self.frames["customers"] = CustomersFrame(self.content, self.staff)
        self.frames["staff"]     = StaffFrame(self.content, self.staff)
        self.frames["occasions"] = OccasionsFrame(self.content, self.staff)

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("dashboard")
        self.after(500, lambda: show_startup_alerts(self))

    _PAGE_NAMES = {
        "dashboard": "📊  Dashboard",
        "flowers":   "🌸  Flowers",
        "orders":    "🛒  Orders",
        "customers": "👥  Customers",
        "staff":     "🪪  Staff",
        "occasions": "🎉  Occasions",
    }

    def show_frame(self, key):
        for k, btn in self.nav_buttons.items():
            btn.configure(fg_color="transparent", text_color=TEXT_DARK,
                          font=("Arial", 13))
        self.nav_buttons[key].configure(
            fg_color=ORANGE_LIGHT, text_color=ORANGE,
            font=("Arial", 13, "bold"))
        self.page_title_label.configure(text=self._PAGE_NAMES.get(key, key.title()))
        self.frames[key].tkraise()
        if hasattr(self.frames[key], "refresh"):
            self.frames[key].refresh()

    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="🌙")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="☀️")

    def logout(self):
        self.destroy()
        LoginWindow().mainloop()


if __name__ == "__main__":
    LoginWindow().mainloop()
