import customtkinter as ctk
from PIL import Image
import os
import theme
from database import get_stats, get_low_stock_flowers, get_order_stats, get_all_orders

ASSET = os.path.join(os.path.dirname(__file__), "assets")

def load_img(name, size):
    path = os.path.join(ASSET, f"{name}.jpg")
    if os.path.exists(path):
        return ctk.CTkImage(Image.open(path), size=size)
    return None

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, staff):
        super().__init__(parent, fg_color=theme.BG_DARK, corner_radius=0)
        self.staff = staff
        self._build()

    def _build(self):
        # ── Top header bar ──
        header = ctk.CTkFrame(self, fg_color="#0F0F23", height=64, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="Dashboard",
                     font=("Arial", 20, "bold"),
                     text_color="white").pack(side="left", padx=24, pady=18)
        ctk.CTkLabel(header, text="🌸  Welcome to Flowerina",
                     font=("Arial", 12),
                     text_color=theme.PRIMARY).pack(side="right", padx=24)

        # Scrollable body
        self.body = ctk.CTkScrollableFrame(self, fg_color=theme.BG_DARK, corner_radius=0)
        self.body.pack(fill="both", expand=True, padx=0, pady=0)

        self.stats_frame      = ctk.CTkFrame(self.body, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.order_stats_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.order_stats_frame.pack(fill="x", padx=20, pady=(0, 16))

        self.bottom_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.bottom_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.bottom_frame.grid_columnconfigure(0, weight=3)
        self.bottom_frame.grid_columnconfigure(1, weight=1)

        self.table_frame = ctk.CTkFrame(self.bottom_frame,
                                         fg_color="#0F0F23", corner_radius=12)
        self.table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.alert_frame = ctk.CTkFrame(self.bottom_frame,
                                         fg_color="#0F0F23", corner_radius=12)
        self.alert_frame.grid(row=0, column=1, sticky="nsew")

        self.refresh()

    def _stat_card(self, parent, col, label, value, color, icon):
        card = ctk.CTkFrame(parent, fg_color="#0F0F23", corner_radius=14)
        card.grid(row=0, column=col, padx=6, pady=4, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(16, 4))
        ctk.CTkLabel(top, text=icon, font=("Arial", 22)).pack(side="left")
        ind = ctk.CTkFrame(top, width=8, height=8,
                           fg_color=color, corner_radius=4)
        ind.pack(side="right", pady=8)

        ctk.CTkLabel(card, text=str(value),
                     font=("Arial", 30, "bold"),
                     text_color=color).pack(anchor="w", padx=16, pady=(0, 2))
        ctk.CTkLabel(card, text=label,
                     font=("Arial", 11),
                     text_color=theme.TEXT_GRAY).pack(anchor="w", padx=16, pady=(0, 16))

    def refresh(self):
        for w in self.stats_frame.winfo_children():      w.destroy()
        for w in self.order_stats_frame.winfo_children(): w.destroy()
        for w in self.table_frame.winfo_children():       w.destroy()
        for w in self.alert_frame.winfo_children():       w.destroy()

        stats = get_stats()
        stat_cards = [
            ("Total Flowers",  stats["total_flowers"],   theme.PRIMARY, "🌸"),
            ("Customers",      stats["total_customers"], theme.SUCCESS,  "👥"),
            ("Completed",      stats["total_sold"],      "#A78BFA",     "✅"),
            ("Pending",        stats["pending"],         theme.WARNING,  "⏳"),
        ]
        for i, (label, value, color, icon) in enumerate(stat_cards):
            self._stat_card(self.stats_frame, i, label, value, color, icon)

        try:
            ostats = get_order_stats()
            order_cards = [
                ("Total Orders",   ostats["total_orders"],             "#A78BFA", "🛒"),
                ("Revenue",        f"₹{ostats['total_revenue']:.0f}",  theme.SUCCESS, "💰"),
                ("Pending Orders", ostats["pending"],                   theme.WARNING, "⏳"),
                ("Today's Orders", ostats["today_orders"],              theme.PRIMARY, "📅"),
            ]
            for i, (label, value, color, icon) in enumerate(order_cards):
                self._stat_card(self.order_stats_frame, i, label, value, color, icon)
        except Exception:
            pass

        # ── Recent orders ──
        header_row = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        header_row.pack(fill="x", padx=16, pady=(16, 8))
        ctk.CTkLabel(header_row, text="Recent Orders",
                     font=("Arial", 15, "bold"),
                     text_color="white").pack(side="left")
        ctk.CTkLabel(header_row, text="Last 8",
                     font=("Arial", 10),
                     text_color=theme.TEXT_GRAY).pack(side="right")

        try:
            orders = get_all_orders()[:8]
            scroll = ctk.CTkScrollableFrame(self.table_frame,
                                             fg_color="transparent", height=260)
            scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))

            if not orders:
                ctk.CTkLabel(scroll, text="No orders yet 🌸",
                             text_color=theme.TEXT_GRAY).pack(pady=30)
            else:
                cols = ["#", "Customer", "Date", "Amount", "Status"]
                hf = ctk.CTkFrame(scroll, fg_color="#1A1A35", corner_radius=8)
                hf.pack(fill="x", pady=(0, 6))
                for j, h in enumerate(cols):
                    ctk.CTkLabel(hf, text=h, font=("Arial", 11, "bold"),
                                 text_color=theme.PRIMARY).grid(
                                     row=0, column=j, padx=12, pady=8, sticky="w")

                sc_map = {"Pending": theme.WARNING,
                          "Completed": theme.SUCCESS,
                          "Cancelled": theme.DANGER}
                for i, o in enumerate(orders):
                    fg = "#16213E" if i % 2 == 0 else "#1A1A35"
                    rf = ctk.CTkFrame(scroll, fg_color=fg, corner_radius=8)
                    rf.pack(fill="x", pady=2)
                    for j, v in enumerate([f"#{o['id']}", o["customer"],
                                            o["order_date"][:10],
                                            f"₹{o['final_amount']:.0f}"]):
                        ctk.CTkLabel(rf, text=v, font=("Arial", 11),
                                     text_color="white").grid(
                                         row=0, column=j, padx=12, pady=7, sticky="w")
                    sc = sc_map.get(o["status"], "gray")
                    badge = ctk.CTkFrame(rf, fg_color=sc, corner_radius=6)
                    badge.grid(row=0, column=4, padx=12, pady=6)
                    ctk.CTkLabel(badge, text=o["status"],
                                 font=("Arial", 10, "bold"),
                                 text_color="white").pack(padx=8, pady=3)
        except Exception:
            ctk.CTkLabel(self.table_frame, text="No data yet.",
                         text_color=theme.TEXT_GRAY).pack(pady=20)

        # ── Low stock panel ──
        low_stock = get_low_stock_flowers(threshold=5)
        ac = len(low_stock)
        ctk.CTkLabel(self.alert_frame,
                     text=f"⚠️ Low Stock ({ac})" if ac else "✅ Stock OK",
                     font=("Arial", 14, "bold"),
                     text_color=theme.DANGER if ac else theme.SUCCESS).pack(
                         anchor="w", padx=14, pady=(14, 6))

        s2 = ctk.CTkScrollableFrame(self.alert_frame, fg_color="transparent")
        s2.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        if not low_stock:
            ctk.CTkLabel(s2, text="All stocked! 🌸",
                         text_color=theme.TEXT_GRAY).pack(pady=20)
        else:
            for f in low_stock:
                card = ctk.CTkFrame(s2, fg_color="#16213E", corner_radius=10)
                card.pack(fill="x", pady=4, padx=4)
                ctk.CTkLabel(card, text=f"🌸 {f['name']}",
                             font=("Arial", 12, "bold"),
                             text_color="white").pack(anchor="w", padx=10, pady=(8, 2))
                sc = theme.DANGER if f["available_stock"] == 0 else theme.WARNING
                ctk.CTkLabel(card,
                             text="OUT OF STOCK" if f["available_stock"] == 0
                             else f"{f['available_stock']} left",
                             font=("Arial", 11, "bold"),
                             text_color=sc).pack(anchor="w", padx=10, pady=(0, 8))
