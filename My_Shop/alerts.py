import customtkinter as ctk
import theme
from database import get_low_stock_flowers

def show_startup_alerts(parent):
    low_stock = get_low_stock_flowers(threshold=5)
    if not low_stock:
        return

    popup = ctk.CTkToplevel(parent)
    popup.title("⚠️ Stock Alerts")
    popup.geometry("400x500")
    popup.configure(fg_color=theme.BG_DARK)
    popup.resizable(False, False)
    popup.grab_set()
    popup.lift()
    popup.focus_force()

    # Header
    hdr = ctk.CTkFrame(popup, fg_color=theme.DANGER, corner_radius=0, height=80)
    hdr.pack(fill="x")
    hdr.pack_propagate(False)
    ctk.CTkLabel(hdr, text="⚠️  Low Stock Warning",
                 font=("Arial", 18, "bold"),
                 text_color="white").pack(pady=(16,2))
    ctk.CTkLabel(hdr, text=f"{len(low_stock)} flower(s) need restocking",
                 font=("Arial", 11),
                 text_color="#FFE0E0").pack()

    scroll = ctk.CTkScrollableFrame(popup, fg_color=theme.BG_DARK, height=320)
    scroll.pack(fill="x", padx=16, pady=12)

    for flower in low_stock:
        card = ctk.CTkFrame(scroll, fg_color="#0F0F23", corner_radius=12)
        card.pack(fill="x", pady=5)
        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", padx=14, pady=12)
        ctk.CTkLabel(left, text=f"🌸  {flower['name']}",
                     font=("Arial", 13, "bold"),
                     text_color="white").pack(anchor="w")
        ctk.CTkLabel(left, text=f"Type: {flower.get('flower_type', '-')}",
                     font=("Arial", 10),
                     text_color=theme.TEXT_GRAY).pack(anchor="w")

        is_out = flower["available_stock"] == 0
        badge = ctk.CTkFrame(card,
                              fg_color=theme.DANGER if is_out else theme.WARNING,
                              corner_radius=8, width=80)
        badge.pack(side="right", padx=14, pady=12)
        badge.pack_propagate(False)
        ctk.CTkLabel(badge,
                     text="OUT" if is_out else str(flower["available_stock"]),
                     font=("Arial", 14, "bold"),
                     text_color="white").pack(expand=True)

    ctk.CTkLabel(popup, text="Please restock soon to avoid lost sales.",
                 font=("Arial", 11),
                 text_color=theme.TEXT_GRAY).pack(pady=4)
    ctk.CTkButton(popup, text="Got it  ✓", width=340, height=44,
                  fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
                  font=("Arial", 13, "bold"), corner_radius=10,
                  command=popup.destroy).pack(pady=(4, 16))
