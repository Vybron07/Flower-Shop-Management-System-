import customtkinter as ctk 
from database import get_stats, get_sold_flowers

class DashboardFrame(ctk, CtkFrame):
    def __init__(self,parent,staff):
        super().__init__(parent, fg_color="transparent")
        self.staff = staff
        self._build()
    
    def _build(self):
        ctk.CTkLabel(self, text="Dashboard", font=("Arial", 22, "bold")).pack(anchor="w", pady=(0, 20))
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=(0, 20))
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True)
        self.refresh()
    def refresh(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()
        for w in self.table_frame.winfo_children():
            w.destroy()

 
        stats = get_stats()
        cards = [
            ("📚 Total Flowers",   stats["total_flowers"],   "#3B82F6"),
            ("👥 Customers",       stats["total_customers"], "#10B981"),
            ("📤 Sold",        stats["total_sold"],  "#F59E0B"),
        ]
        for i, (label, value, color) in enumerate(cards):
            card = ctk.CTkFrame(self.stats_frame, corner_radius=12)
            card.grid(row=0, column=i, padx=8, pady=4, sticky="ew")
            self.stats_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=str(value), font=("Arial", 28, "bold"), text_color=color).pack(pady=(16, 2))
            ctk.CTkLabel(card, text=label, font=("Arial", 12), text_color="gray").pack(pady=(0, 16))
        # Currently sold table
        ctk.CTkLabel(self.table_frame, text="Currently Sold Flowers",
                     font=("Arial", 15, "bold")).pack(anchor="w", padx=12, pady=(12, 6))
        headers = ["#", "Flower Name", "Customer", "Sale Date", "Quantity", "Status"]
        header_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=12)
        for j, h in enumerate(headers):
            ctk.CTkLabel(header_frame, text=h, font=("Arial", 12, "bold"),
                         text_color="gray").grid(row=0, column=j, padx=8, pady=4, sticky="w")
        records = get_sold_flowers()
        scroll = ctk.CTkScrollableFrame(self.table_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=(0,12))
        if not records:
            ctk.CTkLabel(scroll, text="No flowers currently sold.", text_color="gray").pack(pady=20)
        else:
            for i, row in enumerate(records):
                bg = ("gray92", "gray18") if i % 2 == 0 else ("white", "gray15")
                rf = ctk.CTkFrame(scroll, fg_color=bg, corner_radius=6)
                rf.pack(fill="x", pady=2)
                vals = [str(i+1), row["title"], row["member"],
                        row["issue_date"], row["due_date"], row["status"]]
                for j, v in enumerate(vals):
                    ctk.CTkLabel(rf, text=v, font=("Arial", 12)).grid(
                        row=0, column=j, padx=8, pady=6, sticky="w")