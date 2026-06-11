import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import io, random
from Database import get_all_flowers
from database import get_all_flowerss, add_flower, search_flowers, filter_flowers, delete_flower, update_flower_condition

COLORS = ["#3B82F6","#10B981","#F59E0B","#EF4444","#8B5CF6","#EC4899","#06B6D4","#84CC16"]

def generate_cover(flower_name, price, size=(120, 160)):
    color = random.choice(COLORS)
    img = Image.new("RGB", size, color=color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, size[1]-40, size[0], size[1]], fill="#00000033")
    # Title text (wrapped)
    words = flower_name.split()
    lines, line = [], ""
    for w in words:
        if len(line + w) < 14:
            line += w + " "
        else:
            lines.append(line.strip())
            line = w + " "
    lines.append(line.strip())
    y = 20
    for l in lines[:3]:
        draw.text((10, y), l, fill="white")
        y += 18
    draw.text((10, size[1]-30), str(price)[:18], fill="#ffffffcc")
    return img

class FlowersFrame(ctk.CTkFrame):
    def __init__(self, parent, staff):
        super().__init__(parent, fg_color="transparent")
        self.staff = staff
        self._build()

    def _build(self):
        # Top bar
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0,10))
        ctk.CTkLabel(top, text="Flowers", font=("Arial", 22, "bold")).pack(side="left")
        ctk.CTkButton(top, text="+ Add Flower", width=110, command=self.open_add_dialog).pack(side="right")
    
    # Search & filter bar
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", pady=(0,10))
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *a: self.refresh())
        ctk.CTkEntry(bar, placeholder_text="Search by flower name, customer, condition...",
                     textvariable=self.search_var, width=280).pack(side="left", padx=(0,10))
        
        self.filter_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(bar, values=["All", "Available Only", "Fresh", "Damaged"],
                        variable=self.filter_var, command=lambda _: self.refresh(),
                        width=160).pack(side="left")    
    
    # Flowers grid (scrollable)
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)
        self.refresh()
 
    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        kw = self.search_var.get().strip()
        fv = self.filter_var.get()

        if kw:
            flowers = search_flowers(kw)
        elif fv == "Available Only":
            flowers = filter_flowers(available_only=True)
        elif fv in ["Fresh", "Damaged"]:
            flowers = filter_flowers(condition=fv)
        else:
            flowers = get_all_flowers()

        if not flowers:
            ctk.CTkLabel(self.scroll, text="No flowers found.", text_color="gray").pack(pady=40)
            return
        
        cols = 4
        for i, flower in enumerate(flowers):
            card = ctk.CTkFrame(self.scroll, corner_radius=12, width=160)
            card.grid(row=i//cols, column=i%cols, padx=10, pady=10, sticky="n")

            # Cover image
            if flower["cover_image"]:
                img = Image.open(io.BytesIO(flower["cover_image"]))
            else:
                img = generate_cover(flower["title"], flower["price"])
            img = img.resize((120, 160))
            photo = ctk.CTkImage(img, size=(120, 160))
            ctk.CTkLabel(card, image=photo, text="").pack(pady=(10,4))

            ctk.CTkLabel(card, text=flower["title"][:18], font=("Arial", 12, "bold"),
                         wraplength=140).pack(padx=8)
            ctk.CTkLabel(card, text=flower["price"], font=("Arial", 11),
                         text_color="gray").pack()
            
            avail_color = "#10B981" if flower["available_stocks"] > 0 else "#EF4444"
            avail_text  = "Available" if flower["available_stocks"] > 0 else "Not Available"
            ctk.CTkLabel(card, text=avail_text, font=("Arial", 11, "bold"),
                         text_color=avail_color).pack(pady=2)

            ctk.CTkLabel(card, text=f"Condition: {flower['condition']}",
                         font=("Arial", 10), text_color="gray").pack()
            
            # Action buttons
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(pady=(4,10))
            ctk.CTkButton(btn_frame, text="Edit", width=55, height=26,
                          command=lambda b=flower: self.open_edit_dialog(b)).pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="Delete", width=55, height=26,
                          fg_color="#EF4444", hover_color="#DC2626",
                          command=lambda b=flower: self.confirm_delete(b)).pack(side="left", padx=2)
            
    def open_add_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Flower")
        dialog.geometry("400x500")
        dialog.grab_set()

        fields = {}
        for label, key in [("Flower_Name*","flower_name"),("Price*","price"),("Type","type"),
                            ("Condition","condition"),("Available_Stocks","available_stocks")]:
            ctk.CTkLabel(dialog, text=label).pack(anchor="w", padx=20, pady=(10,0))
            e = ctk.CTkEntry(dialog, width=340)
            e.pack(padx=20)
            fields[key] = e

        ctk.CTkLabel(dialog, text="Condition").pack(anchor="w", padx=20, pady=(10,0))
        cond = ctk.CTkOptionMenu(dialog, values=["Fresh","Damaged"], width=340)
        cond.pack(padx=20)
    
    def save():
        flower_name = fields["flower_name"].get().strip()
        price = fields["price"].get().strip()
        if not flower_name or not price:
            return
        type = fields["type"].get().strip()
        available_stocks = int(fields["available_stocks"].get() or 0)
        add_flower(flower_name, price, type, cond.get(), available_stocks)
        dialog.destroy()
        self.refresh()

        ctk.CTkButton(dialog, text="Save Flower", width=340, command=save).pack(pady=20, padx=20)

    def open_edit_dialog(self, flower):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Flower Condition")
        dialog.geometry("300x200")
        dialog.grab_set()
        ctk.CTkLabel(dialog, text=f"Flower: {flower['title']}", font=("Arial",13,"bold")).pack(pady=(20,10))
        ctk.CTkLabel(dialog, text="Update Condition").pack()
        cond = ctk.CTkOptionMenu(dialog, values=["Good","Excellent","Damaged","Lost"], width=240)
        cond.set(flower["condition"])
        cond.pack(pady=10)
        def save():
            update_flower_condition(flower["id"], cond.get())
            dialog.destroy()
            self.refresh()
        ctk.CTkButton(dialog, text="Update", width=240, command=save).pack(pady=10)

    def confirm_delete(self, flower):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("320x160")
        dialog.grab_set()
        ctk.CTkLabel(dialog, text=f"Delete '{flower['title']}'?", font=("Arial",13)).pack(pady=20)
        bf = ctk.CTkFrame(dialog, fg_color="transparent")
        bf.pack()
        ctk.CTkButton(bf, text="Cancel", width=120, fg_color="transparent",
                      border_width=1, command=dialog.destroy).pack(side="left", padx=8)
        ctk.CTkButton(bf, text="Delete", width=120, fg_color="#EF4444",
                      command=lambda: [delete_flower(flower["id"]), dialog.destroy(), self.refresh()]).pack(side="left")

                     

