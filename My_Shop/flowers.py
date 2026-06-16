import customtkinter as ctk
from PIL import Image, ImageDraw
import io, random, os
import theme
from database import get_all_flowers, add_flower, search_flowers, filter_flowers, delete_flower, update_flower_condition

ASSET = os.path.join(os.path.dirname(__file__), "assets")
FLOWER_IMGS = ["rose","tulip","sunflower","lily","orchid","daisy","lavender","bouquet"]

def get_flower_img(name, size=(160, 180)):
    key = name.lower().split()[0] if name else "rose"
    path = os.path.join(ASSET, f"{key}.jpg")
    if not os.path.exists(path):
        path = os.path.join(ASSET, f"{random.choice(FLOWER_IMGS)}.jpg")
    if os.path.exists(path):
        img = Image.open(path).resize(size)
        return ctk.CTkImage(img, size=size)
    # fallback generated
    img = Image.new("RGB", size, random.choice(["#FF6B35","#FF8C42","#FFB347"]))
    return ctk.CTkImage(img, size=size)

class FlowersFrame(ctk.CTkFrame):
    def __init__(self, parent, staff):
        super().__init__(parent, fg_color=theme.BG_DARK, corner_radius=0)
        self.staff = staff
        self._build()

    def _build(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="#0F0F23", height=64, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="🌸  Flowers",
                     font=("Arial", 20, "bold"),
                     text_color="white").pack(side="left", padx=24, pady=18)
        ctk.CTkButton(header, text="+ Add Flower", width=130, height=36,
                      fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
                      font=("Arial", 12, "bold"), corner_radius=8,
                      command=self.open_add_dialog).pack(side="right", padx=20, pady=14)

        # Search bar
        bar = ctk.CTkFrame(self, fg_color="#0F0F23", height=56, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *a: self.refresh())
        ctk.CTkEntry(bar, placeholder_text="🔍  Search flowers...",
                     textvariable=self.search_var, width=300, height=36,
                     fg_color="#1A1A35", border_color=theme.PRIMARY).pack(
                         side="left", padx=20, pady=10)
        self.filter_var = ctk.StringVar(value="All")
        for label in ["All", "Available", "Fresh", "Damaged"]:
            ctk.CTkButton(bar, text=label, width=80, height=30,
                          fg_color="transparent", border_width=1,
                          border_color=theme.PRIMARY,
                          text_color=theme.PRIMARY,
                          hover_color="#1E1E3A",
                          font=("Arial", 11),
                          corner_radius=20,
                          command=lambda l=label: self._set_filter(l)).pack(
                              side="left", padx=4, pady=13)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_DARK)
        self.scroll.pack(fill="both", expand=True, padx=16, pady=12)
        self.refresh()

    def _set_filter(self, val):
        self.filter_var.set(val)
        self.refresh()

    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        kw = self.search_var.get().strip()
        fv = self.filter_var.get()

        if kw:
            flowers = search_flowers(kw)
        elif fv == "Available":
            flowers = filter_flowers(available_only=True)
        elif fv in ["Fresh", "Damaged"]:
            flowers = filter_flowers(condition=fv)
        else:
            flowers = get_all_flowers()

        if not flowers:
            ctk.CTkLabel(self.scroll, text="No flowers found 🌸",
                         font=("Arial", 16),
                         text_color=theme.TEXT_GRAY).pack(pady=60)
            return

        cols = 4
        for i, flower in enumerate(flowers):
            card = ctk.CTkFrame(self.scroll, fg_color="#0F0F23",
                                corner_radius=14, width=200)
            card.grid(row=i // cols, column=i % cols, padx=10, pady=10, sticky="n")

            # Image
            photo = get_flower_img(flower["name"], (180, 160))
            img_label = ctk.CTkLabel(card, image=photo, text="",
                                      corner_radius=10)
            img_label.pack(pady=(10, 0), padx=10)

            # Availability badge
            avail = flower["available_stock"] > 0
            badge_frame = ctk.CTkFrame(card,
                                        fg_color=theme.SUCCESS if avail else theme.DANGER,
                                        corner_radius=6)
            badge_frame.pack(pady=(6, 0))
            ctk.CTkLabel(badge_frame,
                         text="● Available" if avail else "● Out of Stock",
                         font=("Arial", 10, "bold"),
                         text_color="white").pack(padx=8, pady=3)

            ctk.CTkLabel(card, text=flower["name"],
                         font=("Arial", 13, "bold"),
                         text_color="white",
                         wraplength=170).pack(padx=10, pady=(6, 0))
            ctk.CTkLabel(card,
                         text=flower.get("flower_type", "") or "Flower",
                         font=("Arial", 10),
                         text_color=theme.TEXT_GRAY).pack()
            ctk.CTkLabel(card, text=f"₹{flower['price']}",
                         font=("Arial", 16, "bold"),
                         text_color=theme.PRIMARY).pack(pady=(2, 0))
            ctk.CTkLabel(card,
                         text=f"Stock: {flower['available_stock']}  •  {flower['condition']}",
                         font=("Arial", 10),
                         text_color=theme.TEXT_GRAY).pack(pady=(2, 6))

            bf = ctk.CTkFrame(card, fg_color="transparent")
            bf.pack(pady=(0, 12))
            ctk.CTkButton(bf, text="Edit", width=70, height=28,
                          fg_color="#1A1A35", hover_color="#252550",
                          text_color=theme.PRIMARY, border_width=1,
                          border_color=theme.PRIMARY, corner_radius=8,
                          command=lambda b=flower: self.open_edit_dialog(b)).pack(
                              side="left", padx=4)
            ctk.CTkButton(bf, text="Delete", width=70, height=28,
                          fg_color=theme.DANGER, hover_color="#C0392B",
                          corner_radius=8,
                          command=lambda b=flower: self.confirm_delete(b)).pack(
                              side="left", padx=4)

    def open_add_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Flower")
        dialog.geometry("440x520")
        dialog.configure(fg_color=theme.BG_DARK)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="🌸  Add New Flower",
                     font=("Arial", 18, "bold"),
                     text_color="white").pack(pady=(24, 16))

        fields = {}
        for label, key, ph in [
            ("Flower Name *", "name",        "e.g. Red Rose"),
            ("Price (₹) *",   "price",       "e.g. 250"),
            ("Type/Category", "flower_type", "e.g. Bouquet"),
            ("Stock Qty",     "stock",       "e.g. 10"),
        ]:
            ctk.CTkLabel(dialog, text=label, font=("Arial", 12),
                         text_color=theme.TEXT_GRAY).pack(anchor="w", padx=30, pady=(8, 0))
            e = ctk.CTkEntry(dialog, width=360, height=40,
                             placeholder_text=ph,
                             fg_color="#0F0F23",
                             border_color=theme.PRIMARY)
            e.pack(padx=30)
            fields[key] = e

        ctk.CTkLabel(dialog, text="Condition", font=("Arial", 12),
                     text_color=theme.TEXT_GRAY).pack(anchor="w", padx=30, pady=(8, 0))
        cond = ctk.CTkOptionMenu(dialog, values=["Fresh", "Damaged"],
                                  width=360, fg_color="#0F0F23",
                                  button_color=theme.PRIMARY)
        cond.pack(padx=30)

        def save():
            name  = fields["name"].get().strip()
            price = fields["price"].get().strip()
            if not name or not price:
                return
            try:
                pv = float(price)
                sv = int(fields["stock"].get() or 1)
            except ValueError:
                return
            add_flower(name, pv, fields["flower_type"].get(), cond.get(), sv)
            dialog.destroy()
            self.refresh()

        ctk.CTkButton(dialog, text="Save Flower 🌸", width=360, height=44,
                      fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
                      font=("Arial", 13, "bold"), corner_radius=10,
                      command=save).pack(pady=20, padx=30)

    def open_edit_dialog(self, flower):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Flower")
        dialog.geometry("360x240")
        dialog.configure(fg_color=theme.BG_DARK)
        dialog.grab_set()
        ctk.CTkLabel(dialog, text=f"Edit: {flower['name']}",
                     font=("Arial", 15, "bold"),
                     text_color="white").pack(pady=(24, 10))
        ctk.CTkLabel(dialog, text="Condition",
                     text_color=theme.TEXT_GRAY).pack()
        cond = ctk.CTkOptionMenu(dialog, values=["Fresh", "Damaged"],
                                  width=280, fg_color="#0F0F23",
                                  button_color=theme.PRIMARY)
        cond.set(flower["condition"])
        cond.pack(pady=8)
        def save():
            update_flower_condition(flower["id"], cond.get())
            dialog.destroy()
            self.refresh()
        ctk.CTkButton(dialog, text="Update", width=280, height=42,
                      fg_color=theme.PRIMARY, corner_radius=10,
                      command=save).pack(pady=12)

    def confirm_delete(self, flower):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Delete")
        dialog.geometry("340x180")
        dialog.configure(fg_color=theme.BG_DARK)
        dialog.grab_set()
        ctk.CTkLabel(dialog, text=f"Delete '{flower['name']}'?",
                     font=("Arial", 14), text_color="white").pack(pady=30)
        bf = ctk.CTkFrame(dialog, fg_color="transparent")
        bf.pack()
        ctk.CTkButton(bf, text="Cancel", width=130,
                      fg_color="transparent", border_width=1,
                      border_color=theme.TEXT_GRAY,
                      command=dialog.destroy).pack(side="left", padx=8)
        ctk.CTkButton(bf, text="Delete", width=130,
                      fg_color=theme.DANGER, corner_radius=8,
                      command=lambda: [delete_flower(flower["id"]),
                                       dialog.destroy(),
                                       self.refresh()]).pack(side="left")
