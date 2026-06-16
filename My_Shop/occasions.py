import customtkinter as ctk
from PIL import Image, ImageDraw
import os, math
import theme
from database import get_all_occasions, add_occasion, delete_occasion, initialize_occasions

ASSET = os.path.join(os.path.dirname(__file__), "assets")

# ── Per-occasion theme configs ──────────────────────────────
OCCASION_THEMES = {
    "Marriage": {
        "bg":       "#1A0000",
        "card_bg":  "#2D0000",
        "accent":   "#D4AF37",
        "accent2":  "#CC0000",
        "text":     "#FFD700",
        "sub":      "#F5CBA7",
        "badge":    "#CC0000",
        "banner":   "marriage_banner.jpg",
        "emoji":    "💍",
        "tagline":  "Celebrate Love with Elegance",
    },
    "Birthday_Children": {
        "bg":       "#001F5B",
        "card_bg":  "#002D7A",
        "accent":   "#4FC3F7",
        "accent2":  "#FFD700",
        "text":     "#FFFFFF",
        "sub":      "#B3E5FC",
        "badge":    "#0288D1",
        "banner":   "birthday_kids_banner.jpg",
        "emoji":    "🎈",
        "tagline":  "Fun & Colorful for Little Ones!",
    },
    "Birthday_Teen": {
        "bg":       "#1A1000",
        "card_bg":  "#2D2000",
        "accent":   "#FFD700",
        "accent2":  "#FF8C00",
        "text":     "#FFD700",
        "sub":      "#FFF3B0",
        "badge":    "#FFA000",
        "banner":   "birthday_teen_banner.jpg",
        "emoji":    "🌻",
        "tagline":  "Bright & Vibrant for Teens!",
    },
    "Birthday_Adult": {
        "bg":       "#1A0015",
        "card_bg":  "#2D0025",
        "accent":   "#FF69B4",
        "accent2":  "#FFFFFF",
        "text":     "#FFB6C1",
        "sub":      "#FFF0F5",
        "badge":    "#E91E8C",
        "banner":   "birthday_adult_banner.jpg",
        "emoji":    "🌸",
        "tagline":  "Elegant Pink & White for Adults",
    },
    "Birthday_Elderly": {
        "bg":       "#0D001A",
        "card_bg":  "#180030",
        "accent":   "#9B59B6",
        "accent2":  "#E8DAEF",
        "text":     "#D7BDE2",
        "sub":      "#F4ECF7",
        "badge":    "#6C3483",
        "banner":   "birthday_elderly_banner.jpg",
        "emoji":    "💜",
        "tagline":  "Graceful & Serene for the Wise",
    },
    "Puja": {
        "bg":       "#2D0A00",
        "card_bg":  "#3D1500",
        "accent":   "#FF6600",
        "accent2":  "#FFD700",
        "text":     "#FFD700",
        "sub":      "#FFE5B4",
        "badge":    "#FF4500",
        "banner":   "puja_banner.jpg",
        "emoji":    "🪔",
        "tagline":  "पवित्र पूजा के लिए फूल  •  Sacred Flowers",
    },
}

def get_theme_key(occ_type, sub_type):
    if occ_type == "Birthday":
        sub = (sub_type or "").strip()
        if sub == "Children": return "Birthday_Children"
        if sub == "Teen":     return "Birthday_Teen"
        if sub == "Adult":    return "Birthday_Adult"
        if sub == "Elderly":  return "Birthday_Elderly"
        return "Birthday_Adult"
    return occ_type


class OccasionsFrame(ctk.CTkFrame):
    def __init__(self, parent, staff):
        super().__init__(parent, fg_color=theme.BG_DARK, corner_radius=0)
        self.staff    = staff
        self.active   = "Marriage"   # currently selected tab
        initialize_occasions()
        self._build()

    def _build(self):
        # ── Top header ──
        header = ctk.CTkFrame(self, fg_color="#0F0F23", height=64, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="🎉  Occasions",
                     font=("Arial", 20, "bold"),
                     text_color="white").pack(side="left", padx=24, pady=18)
        ctk.CTkButton(header, text="+ Add Occasion", width=140, height=36,
                      fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
                      font=("Arial", 12, "bold"), corner_radius=8,
                      command=self.open_add_dialog).pack(side="right", padx=20, pady=14)

        # ── Tab bar ──
        tab_bar = ctk.CTkFrame(self, fg_color="#0F0F23", height=56, corner_radius=0)
        tab_bar.pack(fill="x")
        tab_bar.pack_propagate(False)

        self.tab_btns = {}
        tabs = [
            ("💍 Marriage",  "Marriage"),
            ("🎂 Birthday",  "Birthday"),
            ("🪔 Puja",      "Puja"),
        ]
        for label, key in tabs:
            btn = ctk.CTkButton(tab_bar, text=label, width=140, height=36,
                                fg_color="transparent",
                                border_width=2,
                                border_color=theme.PRIMARY,
                                text_color=theme.TEXT_GRAY,
                                hover_color="#1E1E3A",
                                font=("Arial", 13, "bold"),
                                corner_radius=10,
                                command=lambda k=key: self.switch_tab(k))
            btn.pack(side="left", padx=10, pady=10)
            self.tab_btns[key] = btn

        # ── Content area ──
        self.content = ctk.CTkFrame(self, fg_color=theme.BG_DARK, corner_radius=0)
        self.content.pack(fill="both", expand=True)

        self.switch_tab("Marriage")

    def switch_tab(self, key):
        self.active = key
        for k, btn in self.tab_btns.items():
            btn.configure(fg_color="transparent", text_color=theme.TEXT_GRAY)
        self.tab_btns[key].configure(fg_color=theme.PRIMARY, text_color="white")
        self.refresh()

    def refresh(self):
        for w in self.content.winfo_children():
            w.destroy()

        if self.active == "Marriage":
            self._render_marriage()
        elif self.active == "Birthday":
            self._render_birthday()
        elif self.active == "Puja":
            self._render_puja()

    # ── MARRIAGE ────────────────────────────────────────────
    def _render_marriage(self):
        t = OCCASION_THEMES["Marriage"]
        scroll = ctk.CTkScrollableFrame(self.content,
                                         fg_color=t["bg"], corner_radius=0)
        scroll.pack(fill="both", expand=True)

        # Banner
        bp = os.path.join(ASSET, t["banner"])
        if os.path.exists(bp):
            bimg = ctk.CTkImage(Image.open(bp), size=(780, 180))
            lbl = ctk.CTkLabel(scroll, image=bimg, text="",
                               corner_radius=14)
            lbl.pack(padx=20, pady=(16, 4))

        ctk.CTkLabel(scroll, text=f"{t['emoji']}  Marriage Occasions",
                     font=("Arial", 22, "bold"),
                     text_color=t["accent"]).pack(pady=(8, 2))
        ctk.CTkLabel(scroll, text=t["tagline"],
                     font=("Arial", 13),
                     text_color=t["sub"]).pack(pady=(0, 14))

        self._render_cards(scroll, "Marriage", "", t)

    # ── BIRTHDAY ────────────────────────────────────────────
    def _render_birthday(self):
        scroll = ctk.CTkScrollableFrame(self.content,
                                         fg_color="#0A0A1A", corner_radius=0)
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="🎂  Birthday Occasions",
                     font=("Arial", 22, "bold"),
                     text_color="white").pack(pady=(16, 4))
        ctk.CTkLabel(scroll, text="Choose the right flowers for every age!",
                     font=("Arial", 13),
                     text_color=theme.TEXT_GRAY).pack(pady=(0, 14))

        age_groups = [
            ("Children", "🎈 For Children", "Blue & White — Fun & Playful"),
            ("Teen",     "🌻 For Teenagers","Yellow & Orange — Bright & Vibrant"),
            ("Adult",    "🌸 For Adults",   "Pink & White — Elegant & Graceful"),
            ("Elderly",  "💜 For Elderly",  "Purple — Serene & Dignified"),
        ]

        for sub, heading, desc in age_groups:
            tk = get_theme_key("Birthday", sub)
            t  = OCCASION_THEMES[tk]

            # Section header
            sec = ctk.CTkFrame(scroll, fg_color=t["card_bg"], corner_radius=14)
            sec.pack(fill="x", padx=20, pady=8)

            # Mini banner
            bp = os.path.join(ASSET, t["banner"])
            if os.path.exists(bp):
                bimg = ctk.CTkImage(Image.open(bp), size=(740, 100))
                ctk.CTkLabel(sec, image=bimg, text="",
                             corner_radius=10).pack(padx=10, pady=(10, 4))

            hrow = ctk.CTkFrame(sec, fg_color="transparent")
            hrow.pack(fill="x", padx=16, pady=(4, 2))
            ctk.CTkLabel(hrow, text=heading,
                         font=("Arial", 16, "bold"),
                         text_color=t["accent"]).pack(side="left")
            ctk.CTkLabel(hrow, text=desc,
                         font=("Arial", 11),
                         text_color=t["sub"]).pack(side="right")

            self._render_cards(sec, "Birthday", sub, t)

    # ── PUJA ────────────────────────────────────────────────
    def _render_puja(self):
        t = OCCASION_THEMES["Puja"]
        scroll = ctk.CTkScrollableFrame(self.content,
                                         fg_color=t["bg"], corner_radius=0)
        scroll.pack(fill="both", expand=True)

        # Banner
        bp = os.path.join(ASSET, t["banner"])
        if os.path.exists(bp):
            bimg = ctk.CTkImage(Image.open(bp), size=(780, 180))
            ctk.CTkLabel(scroll, image=bimg, text="",
                         corner_radius=14).pack(padx=20, pady=(16, 4))

        ctk.CTkLabel(scroll, text="🪔  पूजा  •  Puja Occasions",
                     font=("Arial", 22, "bold"),
                     text_color=t["accent"]).pack(pady=(8, 2))
        ctk.CTkLabel(scroll, text=t["tagline"],
                     font=("Arial", 13),
                     text_color=t["sub"]).pack(pady=(0, 4))

        # Decorative divider
        div = ctk.CTkFrame(scroll, height=3,
                           fg_color=t["accent"], corner_radius=2)
        div.pack(fill="x", padx=60, pady=8)

        # Sacred symbols row
        sym_row = ctk.CTkFrame(scroll, fg_color="transparent")
        sym_row.pack(pady=4)
        for sym in ["🪔", "🌺", "🌸", "🙏", "🌼", "🪷", "⚜️"]:
            ctk.CTkLabel(sym_row, text=sym, font=("Arial", 22)).pack(side="left", padx=8)

        self._render_cards(scroll, "Puja", "", t)

    # ── SHARED CARD RENDERER ────────────────────────────────
    def _render_cards(self, parent, occ_type, sub_type, t):
        occasions = get_all_occasions()
        filtered = [o for o in occasions
                    if o["type"] == occ_type
                    and (not sub_type or o["sub_type"] == sub_type)]

        if not filtered:
            ctk.CTkLabel(parent,
                         text="No occasions added yet. Click '+ Add Occasion'",
                         font=("Arial", 13),
                         text_color=t["sub"]).pack(pady=20)
            return

        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=12)

        cols = 2
        for i, occ in enumerate(filtered):
            card = ctk.CTkFrame(grid, fg_color=t["card_bg"],
                                corner_radius=14,
                                border_width=1,
                                border_color=t["accent"])
            card.grid(row=i // cols, column=i % cols,
                      padx=8, pady=8, sticky="nsew")
            grid.grid_columnconfigure(i % cols, weight=1)

            # Top accent strip
            strip = ctk.CTkFrame(card, fg_color=t["accent"],
                                 height=5, corner_radius=0)
            strip.pack(fill="x")

            # Card body
            body = ctk.CTkFrame(card, fg_color="transparent")
            body.pack(fill="x", padx=14, pady=10)

            # Icon & name
            name_row = ctk.CTkFrame(body, fg_color="transparent")
            name_row.pack(fill="x")
            ctk.CTkLabel(name_row, text=t["emoji"],
                         font=("Arial", 20)).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(name_row, text=occ["name"],
                         font=("Arial", 14, "bold"),
                         text_color=t["text"]).pack(side="left")

            # Badge
            if occ["sub_type"]:
                badge = ctk.CTkFrame(name_row, fg_color=t["badge"],
                                     corner_radius=6)
                badge.pack(side="right")
                ctk.CTkLabel(badge, text=occ["sub_type"],
                             font=("Arial", 10, "bold"),
                             text_color="white").pack(padx=8, pady=3)

            # Description
            ctk.CTkLabel(body, text=occ["description"],
                         font=("Arial", 11),
                         text_color=t["sub"],
                         wraplength=260,
                         justify="left").pack(anchor="w", pady=(4, 2))

            # Flowers
            ctk.CTkFrame(body, height=1,
                         fg_color=t["accent"]).pack(fill="x", pady=6)
            frow = ctk.CTkFrame(body, fg_color="transparent")
            frow.pack(fill="x")
            ctk.CTkLabel(frow, text="🌸 Flowers:",
                         font=("Arial", 10, "bold"),
                         text_color=t["accent"]).pack(side="left")
            ctk.CTkLabel(frow, text=occ["flowers"],
                         font=("Arial", 10),
                         text_color=t["sub"],
                         wraplength=200).pack(side="left", padx=6)

            # Delete button
            ctk.CTkButton(body, text="Remove", width=80, height=26,
                          fg_color="transparent",
                          border_width=1,
                          border_color=theme.DANGER,
                          text_color=theme.DANGER,
                          hover_color="#2A0A0A",
                          corner_radius=6,
                          command=lambda oid=occ["id"]: self._delete(oid)
                          ).pack(anchor="e", pady=(6, 0))

    def _delete(self, oid):
        delete_occasion(oid)
        self.refresh()

    def open_add_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Occasion")
        dialog.geometry("460x560")
        dialog.configure(fg_color=theme.BG_DARK)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="🎉  Add New Occasion",
                     font=("Arial", 18, "bold"),
                     text_color="white").pack(pady=(24, 16))

        fields = {}
        for label, key, ph in [
            ("Occasion Name *", "name",        "e.g. Grand Wedding"),
            ("Description",     "description", "e.g. Elegant floral arrangements"),
            ("Flowers",         "flowers",     "e.g. Red Rose, Marigold, Jasmine"),
        ]:
            ctk.CTkLabel(dialog, text=label, font=("Arial", 12),
                         text_color=theme.TEXT_GRAY).pack(anchor="w", padx=30, pady=(8, 0))
            e = ctk.CTkEntry(dialog, width=380, height=40,
                             placeholder_text=ph,
                             fg_color="#0F0F23",
                             border_color=theme.PRIMARY)
            e.pack(padx=30)
            fields[key] = e

        ctk.CTkLabel(dialog, text="Type *", font=("Arial", 12),
                     text_color=theme.TEXT_GRAY).pack(anchor="w", padx=30, pady=(8, 0))
        type_var = ctk.StringVar(value="Marriage")
        type_menu = ctk.CTkOptionMenu(dialog,
                                       values=["Marriage", "Birthday", "Puja"],
                                       variable=type_var, width=380,
                                       fg_color="#0F0F23",
                                       button_color=theme.PRIMARY)
        type_menu.pack(padx=30)

        ctk.CTkLabel(dialog, text="Sub-type (Birthday only)",
                     font=("Arial", 12),
                     text_color=theme.TEXT_GRAY).pack(anchor="w", padx=30, pady=(8, 0))
        sub_var = ctk.StringVar(value="")
        ctk.CTkOptionMenu(dialog,
                          values=["", "Children", "Teen", "Adult", "Elderly"],
                          variable=sub_var, width=380,
                          fg_color="#0F0F23",
                          button_color=theme.PRIMARY).pack(padx=30)

        def save():
            name = fields["name"].get().strip()
            if not name:
                return
            add_occasion(name, type_var.get(), sub_var.get(),
                         fields["description"].get(),
                         fields["flowers"].get())
            dialog.destroy()
            self.switch_tab(type_var.get())

        ctk.CTkButton(dialog, text="Add Occasion 🎉", width=380, height=44,
                      fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
                      font=("Arial", 13, "bold"), corner_radius=10,
                      command=save).pack(pady=20, padx=30)
