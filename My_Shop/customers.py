import customtkinter as ctk
from database import get_all_members, add_member, delete_member

class MembersFrame(ctk.CTkFrame):
    def __init__(self, parent, staff):
        super().__init__(parent, fg_color="transparent")
        self.staff = staff
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0,10))
        ctk.CTkLabel(top, text="Members", font=("Arial", 22, "bold")).pack(side="left")
        ctk.CTkButton(top, text="+ Add Member", width=120, command=self.open_add_dialog).pack(side="right")

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *a: self.refresh())
        ctk.CTkEntry(self, placeholder_text="Search members...",
                     textvariable=self.search_var, width=280).pack(anchor="w", pady=(0,10))

        headers = ["ID", "Name", "Email", "Phone", "Joined", "Action"]
        hf = ctk.CTkFrame(self, fg_color="transparent")
        hf.pack(fill="x")
        for j, h in enumerate(headers):
            ctk.CTkLabel(hf, text=h, font=("Arial",12,"bold"),
                         text_color="gray").grid(row=0, column=j, padx=12, pady=4, sticky="w")

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        kw = self.search_var.get().strip().lower()
        members = get_all_members()
        if kw:
            members = [m for m in members if kw in m["name"].lower() or kw in (m["email"] or "").lower()]

        if not members:
            ctk.CTkLabel(self.scroll, text="No members found.", text_color="gray").pack(pady=30)
            return

        for i, m in enumerate(members):
            bg = ("gray92","gray18") if i%2==0 else ("white","gray15")
            rf = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=6)
            rf.pack(fill="x", pady=2)
            for j, v in enumerate([m["id"], m["name"], m["email"] or "-",
                                    m["phone"] or "-", m["joined_date"]]):
                ctk.CTkLabel(rf, text=str(v), font=("Arial",12)).grid(
                    row=0, column=j, padx=12, pady=8, sticky="w")
            ctk.CTkButton(rf, text="Remove", width=75, height=26, fg_color="#EF4444",
                          hover_color="#DC2626",
                          command=lambda mid=m["id"]: self.remove(mid)).grid(
                              row=0, column=5, padx=8)

    def open_add_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Member")
        dialog.geometry("360x320")
        dialog.grab_set()
        fields = {}
        for label, key in [("Name*","name"),("Email","email"),("Phone","phone")]:
            ctk.CTkLabel(dialog, text=label).pack(anchor="w", padx=20, pady=(10,0))
            e = ctk.CTkEntry(dialog, width=300)
            e.pack(padx=20)
            fields[key] = e
        def save():
            name = fields["name"].get().strip()
            if not name: return
            add_member(name, fields["email"].get(), fields["phone"].get())
            dialog.destroy()
            self.refresh()
        ctk.CTkButton(dialog, text="Add Member", width=300, command=save).pack(pady=20)

    def remove(self, mid):
        delete_member(mid)
        self.refresh()
