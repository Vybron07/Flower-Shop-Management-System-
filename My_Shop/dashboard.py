import customtkinter as ctk
from database import get_stats, get_low_stock_flowers, get_order_stats, get_all_orders

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, staff):
        super().__init__(parent, fg_color="transparent")
        self.staff = staff
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Dashboard",
                     font=("Arial", 22, "bold")).pack(anchor="w", pady=(0, 20))

        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=(0, 10))

        self.order_stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.order_stats_frame.pack(fill="x", pady=(0, 20))

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="both", expand=True)
        self.bottom_frame.grid_columnconfigure(0, weight=3)
        self.bottom_frame.grid_columnconfigure(1, weight=1)

        self.table_frame = ctk.CTkFrame(self.bottom_frame)
        self.table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.alert_frame = ctk.CTkFrame(self.bottom_frame)
        self.alert_frame.grid(row=0, column=1, sticky="nsew")

        self.refresh()

    def refresh(self):
        # ── Clear all frames ──
        for w in self.stats_frame.winfo_children():
            w.destroy()
        for w in self.order_stats_frame.winfo_children():
            w.destroy()
        for w in self.table_frame.winfo_children():
            w.destroy()
        for w in self.alert_frame.winfo_children():
            w.destroy()

        # ── Shop stats cards ──
        stats = get_stats()
        cards = [
            ("🌸 Total Flowers",  stats["total_flowers"],   "#3B82F6"),
            ("👥 Customers",      stats["total_customers"], "#10B981"),
            ("✅ Completed",      stats["total_sold"],      "#8B5CF6"),
            ("⏳ Pending",        stats["pending"],         "#F59E0B"),
        ]
        for i, (label, value, color) in enumerate(cards):
            card = ctk.CTkFrame(self.stats_frame, corner_radius=12)
            card.grid(row=0, column=i, padx=8, pady=4, sticky="ew")
            self.stats_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=str(value),
                         font=("Arial", 28, "bold"),
                         text_color=color).pack(pady=(16, 2))
            ctk.CTkLabel(card, text=label,
                         font=("Arial", 12),
                         text_color="gray").pack(pady=(0, 16))

        # ── Order stats cards ──
        try:
            ostats = get_order_stats()
            order_cards = [
                ("🛒 Total Orders",   ostats["total_orders"],            "#8B5CF6"),
                ("💰 Total Revenue",  f"₹{ostats['total_revenue']:.2f}", "#10B981"),
                ("⏳ Pending",        ostats["pending"],                  "#F59E0B"),
                ("📅 Today's Orders", ostats["today_orders"],             "#3B82F6"),
            ]
            for i, (label, value, color) in enumerate(order_cards):
                card = ctk.CTkFrame(self.order_stats_frame, corner_radius=12)
                card.grid(row=0, column=i, padx=8, pady=4, sticky="ew")
                self.order_stats_frame.grid_columnconfigure(i, weight=1)
                ctk.CTkLabel(card, text=str(value),
                             font=("Arial", 22, "bold"),
                             text_color=color).pack(pady=(14, 2))
                ctk.CTkLabel(card, text=label,
                             font=("Arial", 12),
                             text_color="gray").pack(pady=(0, 14))
        except Exception:
            pass

        # ── Recent orders table ──
        ctk.CTkLabel(self.table_frame, text="Recent Orders",
                     font=("Arial", 15, "bold")).pack(anchor="w", padx=12, pady=(12, 6))
        try:
            orders = get_all_orders()[:8]
            scroll = ctk.CTkScrollableFrame(self.table_frame, fg_color="transparent")
            scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))

            if not orders:
                ctk.CTkLabel(scroll, text="No orders yet.",
                             text_color="gray").pack(pady=20)
            else:
                headers = ["#", "Customer", "Date", "Final", "Status"]
                hf = ctk.CTkFrame(scroll, fg_color="transparent")
                hf.pack(fill="x")
                for j, h in enumerate(headers):
                    ctk.CTkLabel(hf, text=h, font=("Arial", 11, "bold"),
                                 text_color="gray").grid(row=0, column=j,
                                                          padx=8, pady=4, sticky="w")
                status_colors = {
                    "Pending":   "#F59E0B",
                    "Completed": "#10B981",
                    "Cancelled": "#EF4444"
                }
                for i, o in enumerate(orders):
                    bg = ("gray92", "gray18") if i % 2 == 0 else ("white", "gray15")
                    rf = ctk.CTkFrame(scroll, fg_color=bg, corner_radius=6)
                    rf.pack(fill="x", pady=2)
                    sc = status_colors.get(o["status"], "gray")
                    for j, v in enumerate([f"#{o['id']}", o["customer"],
                                            o["order_date"][:10],
                                            f"₹{o['final_amount']:.2f}"]):
                        ctk.CTkLabel(rf, text=v, font=("Arial", 11)).grid(
                            row=0, column=j, padx=8, pady=6, sticky="w")
                    ctk.CTkLabel(rf, text=o["status"],
                                 font=("Arial", 11, "bold"),
                                 text_color=sc).grid(row=0, column=4,
                                                      padx=8, pady=6, sticky="w")
        except Exception:
            ctk.CTkLabel(self.table_frame, text="No order data yet.",
                         text_color="gray").pack(pady=20)

        # ── Low stock alerts panel ──
        low_stock = get_low_stock_flowers(threshold=5)
        alert_count = len(low_stock)
        alert_color = "#EF4444" if alert_count > 0 else "#10B981"
        alert_title = f"⚠️ Low Stock ({alert_count})" if alert_count > 0 else "✅ Stock OK"

        ctk.CTkLabel(self.alert_frame, text=alert_title,
                     font=("Arial", 14, "bold"),
                     text_color=alert_color).pack(anchor="w", padx=12, pady=(12, 6))

        scroll2 = ctk.CTkScrollableFrame(self.alert_frame, fg_color="transparent")
        scroll2.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        if not low_stock:
            ctk.CTkLabel(scroll2, text="All flowers\nwell stocked! 🌸",
                         text_color="gray", justify="center").pack(pady=20)
        else:
            for flower in low_stock:
                card = ctk.CTkFrame(scroll2, corner_radius=8,
                                    fg_color=("gray92", "gray18"))
                card.pack(fill="x", pady=4, padx=4)
                ctk.CTkLabel(card, text=f"🌸 {flower['name']}",
                             font=("Arial", 12, "bold")).pack(anchor="w",
                                                               padx=10, pady=(8, 2))
                stock_color = "#EF4444" if flower["available_stock"] == 0 else "#F59E0B"
                ctk.CTkLabel(card, text=f"Stock: {flower['available_stock']} left",
                             font=("Arial", 11),
                             text_color=stock_color).pack(anchor="w",
                                                           padx=10, pady=(0, 8))
