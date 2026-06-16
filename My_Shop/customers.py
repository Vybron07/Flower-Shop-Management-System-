import customtkinter as ctk
import theme
from database import get_all_customers, add_customer, delete_customer

class CustomersFrame(ctk.CTkFrame):
    def __init__(self, parent, staff):
        super().__init__(parent, fg_color=theme.BG_DARK, corner_radius=0)
        self.staff = staff
        self._build()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="#0F0F23", height=64, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="👥  Customers",
                     font=("Arial", 20, "bold"),
                     text_color="white").pack(side="left", padx=24, pady=18)
        ctk.CTkButton(header, text="+ Add Customer", width=140, height=36,
                      fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
                      font=("Arial", 12, "bold"), corner_radius=8,
                      command=self.open_add_dialog).pack(side="right", padx=20, pady=14)

        bar = ctk.CTkFrame(self, fg_color="#0F0F23", height=56, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *a: self.refresh())
        ctk.CTkEntry(bar, placeholder_text="🔍  Search customers...",
                     textvariable=self.search_var, width=300, height=36,
                     fg_color="#1A1A35",
                     border_color=theme.PRIMARY).pack(side="left", padx=20, pady=10)

        # Table header
        th = ctk.CTkFrame(self, fg_color="#0F0F23", height=40, corner_radius=0)
        th.pack(fill="x", padx=20, pady=(12, 0))
        for j, (h, w) in enumerate([("ID",60),("Name",180),("Email",200),
                                     ("Phone",130),("Joined",120),("Action",80)]):
            ctk.CTkLabel(th, text=h, font=("Arial", 11, "bold"),
                         text_color=theme.PRIMARY,
                         width=w, anchor="w").grid(row=0, column=j, padx=8, pady=8)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_DARK)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=(4, 16))
        self.refresh()

    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        kw = self.search_var.get().strip().lower()
        customers = get_all_customers()
        if kw:
            customers = [c for c in customers
                         if kw in c["name"].lower()
                         or kw in (c["email"] or "").lower()]
        if not customers:
            ctk.CTkLabel(self.scroll, text="No customers found.",
                         text_color=theme.TEXT_GRAY,
                         font=("Arial", 14)).pack(pady=40)
            return
        for i, c in enumerate(customers):
            fg = "#0F0F23" if i % 2 == 0 else "#16213E"
            rf = ctk.CTkFrame(self.scroll, fg_color=fg, corner_radius=10)
            rf.pack(fill="x", pady=3)
            for j, (v, w) in enumerate([(c["id"],60),(c["name"],180),
                                         (c["email"] or "-",200),
                                         (c["phone"] or "-",130),
                                         (c["joined_date"],120)]):
                ctk.CTkLabel(rf, text=str(v), font=("Arial", 12),
                             text_color="white", width=w,
                             anchor="w").grid(row=0, column=j, padx=8, pady=10)
            ctk.CTkButton(rf, text="Remove", width=75, height=28,
                          fg_color=theme.DANGER, hover_color="#C0392B",
                          font=("Arial", 11), corner_radius=6,
                          command=lambda cid=c["id"]: self.remove(cid)).grid(
                              row=0, column=5, padx=8)

    def open_add_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Customer")
        dialog.geometry("400x360")
        dialog.configure(fg_color=theme.BG_DARK)
        dialog.grab_set()
        ctk.CTkLabel(dialog, text="👥  Add Customer",
                     font=("Arial", 18, "bold"),
                     text_color="white").pack(pady=(24, 16))
        fields = {}
        for label, key, ph in [("Name *","name","Full name"),
                                ("Email","email","email@example.com"),
                                ("Phone","phone","+91 XXXXX XXXXX")]:
            ctk.CTkLabel(dialog, text=label, font=("Arial", 12),
                         text_color=theme.TEXT_GRAY).pack(anchor="w", padx=30, pady=(8,0))
            e = ctk.CTkEntry(dialog, width=320, height=40,
                             placeholder_text=ph,
                             fg_color="#0F0F23",
                             border_color=theme.PRIMARY)
            e.pack(padx=30)
            fields[key] = e
        def save():
            name = fields["name"].get().strip()
            if not name: return
            add_customer(name, fields["email"].get(), fields["phone"].get())
            dialog.destroy()
            self.refresh()
        ctk.CTkButton(dialog, text="Add Customer", width=320, height=44,
                      fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
                      font=("Arial", 13, "bold"), corner_radius=10,
                      command=save).pack(pady=20)

    def remove(self, cid):
        delete_customer(cid)
        self.refresh()
