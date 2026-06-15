import customtkinter as ctk
from database import get_low_stock_flowers

def show_startup_alerts(parent):
    low_stock = get_low_stock_flowers(threshold=5)
    if not low_stock:
        return

    popup = ctk.CTkToplevel(parent)
    popup.title("⚠️ Stock Alerts")
    popup.geometry("380x460")
    popup.resizable(False, False)
    popup.grab_set()
    popup.lift()
    popup.focus_force()

    ctk.CTkLabel(popup, text="⚠️ Low Stock Warning",
                 font=("Arial", 18, "bold"),
                 text_color="#EF4444").pack(pady=(20, 4))
    ctk.CTkLabel(popup, text=f"{len(low_stock)} flower(s) are running low!",
                 font=("Arial", 13),
                 text_color="gray").pack(pady=(0, 12))

    ctk.CTkFrame(popup, height=1, fg_color="gray").pack(fill="x", padx=20, pady=4)

    scroll = ctk.CTkScrollableFrame(popup, fg_color="transparent", height=260)
    scroll.pack(fill="x", padx=20, pady=8)

    for flower in low_stock:
        card = ctk.CTkFrame(scroll, corner_radius=10,
                            fg_color=("gray92", "gray18"))
        card.pack(fill="x", pady=5)

        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", padx=12, pady=10)
        ctk.CTkLabel(left, text=f"🌸 {flower['name']}",
                     font=("Arial", 13, "bold")).pack(anchor="w")
        ctk.CTkLabel(left, text=f"Type: {flower.get('flower_type', '-')}",
                     font=("Arial", 11),
                     text_color="gray").pack(anchor="w")

        stock_color = "#EF4444" if flower["available_stock"] == 0 else "#F59E0B"
        badge = ctk.CTkFrame(card, fg_color=stock_color,
                             corner_radius=8, width=70)
        badge.pack(side="right", padx=12, pady=10)
        badge.pack_propagate(False)
        label = "OUT" if flower["available_stock"] == 0 else str(flower["available_stock"])
        ctk.CTkLabel(badge, text=label,
                     font=("Arial", 13, "bold"),
                     text_color="white").pack(expand=True)

    ctk.CTkFrame(popup, height=1, fg_color="gray").pack(fill="x", padx=20, pady=4)
    ctk.CTkLabel(popup, text="Please restock these items soon.",
                 font=("Arial", 11),
                 text_color="gray").pack(pady=6)
    ctk.CTkButton(popup, text="Got it ✓", width=320,
                  command=popup.destroy).pack(pady=(4, 20))
