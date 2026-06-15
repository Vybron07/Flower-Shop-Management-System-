import customtkinter as ctk
from database import get_all_staff, add_staff

class StaffFrame(ctk.CTkFrame):
    def __init__(self, parent, staff):
        super().__init__(parent, fg_color="transparent")
        self.staff = staff
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(top, text="Staff",
                     font=("Arial", 22, "bold")).pack(side="left")
        if self.staff["role"] == "Admin":
            ctk.CTkButton(top, text="+ Add Staff", width=110,
                          command=self.open_add_dialog).pack(side="right")

        headers = ["ID", "Name", "Username", "Role", "Email", "Phone", "Joined"]
        hf = ctk.CTkFrame(self, fg_color="transparent")
        hf.pack(fill="x")
        for j, h in enumerate(headers):
            ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"),
                         text_color="gray").grid(row=0, column=j,
                                                  padx=10, pady=4, sticky="w")

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        staff_list = get_all_staff()
        if not staff_list:
            ctk.CTkLabel(self.scroll, text="No staff found.",
                         text_color="gray").pack(pady=30)
            return
        for i, s in enumerate(staff_list):
            bg = ("gray92", "gray18") if i % 2 == 0 else ("white", "gray15")
            rf = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=6)
            rf.pack(fill="x", pady=2)
            for j, v in enumerate([s["id"], s["name"], s["username"],
                                    s["role"], s["email"] or "-",
                                    s["phone"] or "-", s["joined_date"]]):
                ctk.CTkLabel(rf, text=str(v),
                             font=("Arial", 12)).grid(row=0, column=j,
                                                       padx=10, pady=8, sticky="w")

    def open_add_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Staff")
        dialog.geometry("380x420")
        dialog.grab_set()
        fields = {}
        for label, key in [("Name*", "name"), ("Username*", "username"),
                            ("Password*", "password"), ("Email", "email"),
                            ("Phone", "phone")]:
            ctk.CTkLabel(dialog, text=label).pack(anchor="w", padx=20, pady=(10, 0))
            e = ctk.CTkEntry(dialog, width=320,
                             show="*" if key == "password" else "")
            e.pack(padx=20)
            fields[key] = e

        ctk.CTkLabel(dialog, text="Role").pack(anchor="w", padx=20, pady=(10, 0))
        role = ctk.CTkOptionMenu(dialog,
                                  values=["Manager", "Admin", "Assistant"],
                                  width=320)
        role.pack(padx=20)

        def save():
            name  = fields["name"].get().strip()
            uname = fields["username"].get().strip()
            pwd   = fields["password"].get().strip()
            if not all([name, uname, pwd]):
                return
            add_staff(name, uname, pwd, role.get(),
                      fields["email"].get(), fields["phone"].get())
            dialog.destroy()
            self.refresh()

        ctk.CTkButton(dialog, text="Add Staff", width=320,
                      command=save).pack(pady=20)
