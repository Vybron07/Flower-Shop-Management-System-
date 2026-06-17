import customtkinter as ctk
from theme import (APP_NAME, BG_ROOT, BG_SIDEBAR, SIDEBAR_TEXT,
                   FONT_FAMILY, SECTION_THEMES, NAV_ITEMS)
import database as db
import sound_manager as sfx

from dashboard   import DashboardFrame
from occasions   import OccasionsFrame
from anniversary import AnniversaryFrame
from sections    import FlowersFrame, OrdersFrame, ClientsFrame

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


class FlowerShopApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        db.initialize_db()

        self.title(APP_NAME)
        self.geometry("1300x800")
        self.minsize(1100, 680)
        self.configure(fg_color=BG_ROOT)

        self._current  = None
        self._nav_btns = {}
        self._frames   = {}

        self._build_layout()
        self._navigate("dashboard")

    # ── Layout ──────────────────────────────────────────────────
    def _build_layout(self):
        # Sidebar
        self._sidebar = ctk.CTkFrame(self, fg_color=BG_SIDEBAR,
                                     corner_radius=0, width=230)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Logo
        logo = ctk.CTkFrame(self._sidebar, fg_color="#1A0D30",
                            corner_radius=0, height=90)
        logo.pack(fill="x")
        logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="🌸", font=(FONT_FAMILY, 34)).pack(pady=(12, 0))
        ctk.CTkLabel(logo, text="Bloom & Petal",
                     font=(FONT_FAMILY, 15, "bold"),
                     text_color="#FFD6EC").pack()

        # Nav buttons
        nav = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        nav.pack(fill="both", expand=True, pady=14)

        for label, icon, key in NAV_ITEMS:
            btn = ctk.CTkButton(
                nav,
                text=f"  {icon}  {label}",
                anchor="w",
                font=(FONT_FAMILY, 13),
                text_color="#C0A8D8",
                fg_color="transparent",
                hover_color="#3D2060",
                height=48,
                corner_radius=10,
                command=lambda k=key: self._navigate(k)
            )
            btn.pack(fill="x", padx=12, pady=3)
            self._nav_btns[key] = btn

        # Bottom version label
        ctk.CTkLabel(self._sidebar, text="v2.0  •  Bloom & Petal",
                     font=(FONT_FAMILY, 10),
                     text_color="#5A4070").pack(side="bottom", pady=12)

        # Main content
        self._content = ctk.CTkFrame(self, fg_color=BG_ROOT, corner_radius=0)
        self._content.pack(side="left", fill="both", expand=True)

    # ── Navigation — KEY FIX: always destroy & rebuild frames ───
    def _navigate(self, key: str):
        if self._current == key:
            return
        sfx.click()

        # Update sidebar highlights
        for k, btn in self._nav_btns.items():
            T = SECTION_THEMES.get(k, {})
            if k == key:
                btn.configure(
                    fg_color=T.get("btn", "#E91E8C"),
                    text_color="#FFFFFF",
                    font=(FONT_FAMILY, 13, "bold")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color="#C0A8D8",
                    font=(FONT_FAMILY, 13)
                )

        # Hide old frame
        if self._current and self._current in self._frames:
            self._frames[self._current].pack_forget()

        self._current = key

        # ALWAYS rebuild the frame fresh — fixes blank tab bug
        if key in self._frames:
            try:
                self._frames[key].destroy()
            except Exception:
                pass
            del self._frames[key]

        frame = self._build_section(key)
        self._frames[key] = frame
        frame.pack(fill="both", expand=True)

    def _build_section(self, key: str):
        builders = {
            "dashboard":   lambda: DashboardFrame(self._content),
            "flowers":     lambda: FlowersFrame(self._content, self),
            "occasions":   lambda: OccasionsFrame(self._content, self),
            "anniversary": lambda: AnniversaryFrame(self._content, self),
            "orders":      lambda: OrdersFrame(self._content, self),
            "clients":     lambda: ClientsFrame(self._content, self),
        }
        builder = builders.get(key)
        if builder:
            return builder()
        f = ctk.CTkFrame(self._content, fg_color=BG_ROOT)
        ctk.CTkLabel(f, text=f"'{key}' coming soon.",
                     font=(FONT_FAMILY, 18), text_color="#888899").pack(expand=True)
        return f


if __name__ == "__main__":
    app = FlowerShopApp()
    app.mainloop()
