import customtkinter as ctk
import theme
from database import get_all_staff, add_staff

class StaffFrame(ctk.CTkFrame):
    def __init__(self, parent, staff):
        super().__init__(parent, fg_color=theme.BG_DARK, corner_radius=0)
        self.staff = staff
        self._build()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="#0F0F23", height=64, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="🪪  Staff",
                     font=("Arial", 20, "bold"),
                     text_color="white").pack(side="left", padx=24, pady=18)
        if self.staff["role"] == "Admin":
            ctk.CTkButton(header, text="+ Add Staff", width=120, height=36,
                          fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
                          font=("Arial", 12, "bold"), corner_radius=8,
                          command=self.open_add_dialog).pack(side="right", padx=20, pady=14)

        th = ctk.CTkFrame(self, fg_color="#0F0F23", height=40, corner_radius=0)
        th.pack(fill="x", padx=20, pady=(12, 0))
        for j, (h, w) in enumerate([("ID",50),("Name",160),("Username",130),
                                     ("Role",100),("Email",180),("Phone",130),("Joined",110)]):
            ctk.CTkLabel(th, text=h, font=("Arial", 11, "bold"),
                         text_color=theme.PRIMARY,
                         width=w, anchor="w").grid(row=0, column=j, padx=8, pady=8)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_DARK)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=(4, 16))
        self.refresh()

    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        staff_list = get_all_staff()
        if not staff_list:
            ctk.CTkLabel(self.scroll, text="No staff found.",
                         text_color=theme.TEXT_GRAY,
                         font=("Arial", 14)).pack(pady=40)
            return
        role_colors = {"Admin": theme.DANGER, "Manager": theme.PRIMARY,
                       "Assistant": theme.SUCCESS}
        for i, s in enumerate(staff_list):
            fg = "#0F0F23" if i % 2 == 0 else "#16213E"
            rf = ctk.CTkFrame(self.scroll, fg_color=fg, corner_radius=10)
            rf.pack(fill="x", pady=3)
            for j, (v, w) in enumerate([(s["id"],50),(s["name"],160),
                                         (s["username"],130),(s["role"],100),
                                         (s["email"] or "-",180),
                                         (s["phone"] or "-",130),
                                         (s["joined_date"],110)]):
                color = role_colors.get(str(v), "white") if j == 3 else "white"
                ctk.CTkLabel(rf, text=str(v), font=("Arial", 12),
                             text_color=color, width=w,
                             anchor="w").grid(row=0, column=j, padx=8, pady=10)

    def open_add_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Staff")
        dialog.geometry("420x500")
        dialog.configure(fg_color=theme.BG_DARK)
        dialog.grab_set()
        ctk.CTkLabel(dialog, text="🪪  Add Staff Member",
                     font=("Arial", 18, "bold"),
                     text_color="white").pack(pady=(24, 16))
        fields = {}
        for label, key, ph in [("Name *","name","Full name"),
                                ("Username *","username","login username"),
                                ("Password *","password","secure password"),
                                ("Email","email","email@example.com"),
                                ("Phone","phone","+91 XXXXX XXXXX")]:
            ctk.CTkLabel(dialog, text=label, font=("Arial", 12),
                         text_color=theme.TEXT_GRAY).pack(anchor="w", padx=30, pady=(8,0))
            e = ctk.CTkEntry(dialog, width=340, height=40,
                             placeholder_text=ph,
                             show="*" if key == "password" else "",
                             fg_color="#0F0F23",
                             border_color=theme.PRIMARY)
            e.pack(padx=30)
            fields[key] = e
        ctk.CTkLabel(dialog, text="Role", font=("Arial", 12),
                     text_color=theme.TEXT_GRAY).pack(anchor="w", padx=30, pady=(8,0))
        role = ctk.CTkOptionMenu(dialog, values=["Manager","Admin","Assistant"],
                                  width=340, fg_color="#0F0F23",
                                  button_color=theme.PRIMARY)
        role.pack(padx=30)
        def save():
            name  = fields["name"].get().strip()
            uname = fields["username"].get().strip()
            pwd   = fields["password"].get().strip()
            if not all([name, uname, pwd]): return
            add_staff(name, uname, pwd, role.get(),
                      fields["email"].get(), fields["phone"].get())
            dialog.destroy()
            self.refresh()
        ctk.CTkButton(dialog, text="Add Staff Member", width=340, height=44,
                      fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
                      font=("Arial", 13, "bold"), corner_radius=10,
                      command=save).pack(pady=20)
