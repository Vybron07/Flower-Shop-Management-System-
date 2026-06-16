import customtkinter as ctk
import theme
from database import (get_all_orders, create_order, get_order_details,
                      update_order_status, get_all_customers, get_all_flowers)

class OrdersFrame(ctk.CTkFrame):
    def __init__(self, parent, staff):
        super().__init__(parent, fg_color=theme.BG_DARK, corner_radius=0)
        self.staff = staff
        self._build()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="#0F0F23", height=64, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="🛒  Orders & Billing",
                     font=("Arial", 20, "bold"),
                     text_color="white").pack(side="left", padx=24, pady=18)
        ctk.CTkButton(header, text="+ New Order", width=130, height=36,
                      fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
                      font=("Arial", 12, "bold"), corner_radius=8,
                      command=self.open_new_order).pack(side="right", padx=20, pady=14)

        bar = ctk.CTkFrame(self, fg_color="#0F0F23", height=52, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        self.filter_var = ctk.StringVar(value="All")
        for status in ["All", "Pending", "Completed", "Cancelled"]:
            ctk.CTkButton(bar, text=status, width=90, height=30,
                          fg_color="transparent", border_width=1,
                          border_color=theme.PRIMARY,
                          text_color=theme.PRIMARY,
                          hover_color="#1E1E3A",
                          corner_radius=20,
                          command=lambda s=status: self._filter(s)).pack(
                              side="left", padx=6, pady=11)

        th = ctk.CTkFrame(self, fg_color="#0F0F23", height=40, corner_radius=0)
        th.pack(fill="x", padx=20, pady=(8,0))
        for j, (h, w) in enumerate([("#",50),("Customer",160),("Staff",130),
                                     ("Date",130),("Total",90),("Disc",60),
                                     ("Final",90),("Status",110),("Actions",180)]):
            ctk.CTkLabel(th, text=h, font=("Arial", 11, "bold"),
                         text_color=theme.PRIMARY, width=w,
                         anchor="w").grid(row=0, column=j, padx=6, pady=8)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_DARK)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=(4,16))
        self.refresh()

    def _filter(self, val):
        self.filter_var.set(val)
        self.refresh()

    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        orders = get_all_orders()
        fv = self.filter_var.get()
        if fv != "All":
            orders = [o for o in orders if o["status"] == fv]
        if not orders:
            ctk.CTkLabel(self.scroll, text="No orders found 🛒",
                         text_color=theme.TEXT_GRAY,
                         font=("Arial", 14)).pack(pady=40)
            return

        sc_map = {"Pending": theme.WARNING,
                  "Completed": theme.SUCCESS,
                  "Cancelled": theme.DANGER}

        for i, order in enumerate(orders):
            fg = "#0F0F23" if i % 2 == 0 else "#16213E"
            rf = ctk.CTkFrame(self.scroll, fg_color=fg, corner_radius=10)
            rf.pack(fill="x", pady=3)

            for j, (v, w) in enumerate([
                (f"#{order['id']}",50), (order["customer"],160),
                (order["staff"],130), (order["order_date"][:10],130),
                (f"₹{order['total_amount']:.0f}",90),
                (f"{order['discount']}%",60),
                (f"₹{order['final_amount']:.0f}",90),
            ]):
                ctk.CTkLabel(rf, text=str(v), font=("Arial", 11),
                             text_color="white", width=w,
                             anchor="w").grid(row=0, column=j, padx=6, pady=9)

            sc = sc_map.get(order["status"], "gray")
            badge = ctk.CTkFrame(rf, fg_color=sc, corner_radius=6, width=90)
            badge.grid(row=0, column=7, padx=6, pady=7)
            badge.grid_propagate(False)
            ctk.CTkLabel(badge, text=order["status"],
                         font=("Arial", 10, "bold"),
                         text_color="white").pack(expand=True, padx=4)

            bf = ctk.CTkFrame(rf, fg_color="transparent")
            bf.grid(row=0, column=8, padx=6)
            ctk.CTkButton(bf, text="Receipt", width=65, height=26,
                          fg_color="#1A1A35", border_width=1,
                          border_color=theme.PRIMARY,
                          text_color=theme.PRIMARY, corner_radius=6,
                          command=lambda oid=order["id"]: ReceiptWindow(self, oid)
                          ).pack(side="left", padx=2)
            if order["status"] == "Pending":
                ctk.CTkButton(bf, text="✓", width=30, height=26,
                              fg_color=theme.SUCCESS, corner_radius=6,
                              command=lambda oid=order["id"]: self._complete(oid)
                              ).pack(side="left", padx=2)
                ctk.CTkButton(bf, text="✗", width=30, height=26,
                              fg_color=theme.DANGER, corner_radius=6,
                              command=lambda oid=order["id"]: self._cancel(oid)
                              ).pack(side="left", padx=2)

    def open_new_order(self):
        NewOrderDialog(self, self.staff).grab_set()

    def _complete(self, oid):
        update_order_status(oid, "Completed"); self.refresh()

    def _cancel(self, oid):
        update_order_status(oid, "Cancelled"); self.refresh()


class NewOrderDialog(ctk.CTkToplevel):
    def __init__(self, parent, staff):
        super().__init__(parent)
        self.parent = parent
        self.staff  = staff
        self.title("New Order")
        self.geometry("600x660")
        self.configure(fg_color=theme.BG_DARK)
        self.cart = []
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="🛒  New Order",
                     font=("Arial", 18, "bold"),
                     text_color="white").pack(pady=(20, 4))

        ctk.CTkLabel(self, text="Customer", font=("Arial", 12),
                     text_color=theme.TEXT_GRAY).pack(anchor="w", padx=24)
        customers = get_all_customers()
        self.cmap = {c["name"]: c["id"] for c in customers}
        self.cvar = ctk.StringVar(value=customers[0]["name"] if customers else "")
        ctk.CTkOptionMenu(self, values=list(self.cmap.keys()) or ["No customers"],
                          variable=self.cvar, width=540,
                          fg_color="#0F0F23",
                          button_color=theme.PRIMARY).pack(padx=24, pady=(2,12))

        ctk.CTkLabel(self, text="Add Flowers", font=("Arial", 12),
                     text_color=theme.TEXT_GRAY).pack(anchor="w", padx=24)
        flowers = get_all_flowers()
        self.fmap = {f["name"]: (f["id"], f["price"]) for f in flowers}

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=4)
        self.fvar = ctk.StringVar(
            value=list(self.fmap.keys())[0] if self.fmap else "")
        ctk.CTkOptionMenu(row, values=list(self.fmap.keys()) or ["No flowers"],
                          variable=self.fvar, width=280,
                          fg_color="#0F0F23",
                          button_color=theme.PRIMARY).pack(side="left", padx=(0,8))
        self.qty = ctk.StringVar(value="1")
        ctk.CTkEntry(row, textvariable=self.qty, width=80, height=36,
                     placeholder_text="Qty",
                     fg_color="#0F0F23",
                     border_color=theme.PRIMARY).pack(side="left", padx=(0,8))
        ctk.CTkButton(row, text="+ Add", width=110, height=36,
                      fg_color=theme.PRIMARY, corner_radius=8,
                      command=self.add_to_cart).pack(side="left")

        ctk.CTkLabel(self, text="Cart", font=("Arial", 13, "bold"),
                     text_color="white").pack(anchor="w", padx=24, pady=(10,2))
        self.cart_frame = ctk.CTkScrollableFrame(self, height=160,
                                                  fg_color="#0F0F23",
                                                  corner_radius=10)
        self.cart_frame.pack(fill="x", padx=24)

        dr = ctk.CTkFrame(self, fg_color="transparent")
        dr.pack(fill="x", padx=24, pady=10)
        ctk.CTkLabel(dr, text="Discount %:",
                     text_color=theme.TEXT_GRAY).pack(side="left", padx=(0,8))
        self.disc = ctk.StringVar(value="0")
        ctk.CTkEntry(dr, textvariable=self.disc, width=80,
                     fg_color="#0F0F23",
                     border_color=theme.PRIMARY).pack(side="left")
        self.disc.trace("w", lambda *a: self.update_totals())

        self.total_lbl = ctk.CTkLabel(self, text="Total: ₹0",
                                       font=("Arial", 14),
                                       text_color=theme.TEXT_GRAY)
        self.total_lbl.pack()
        self.final_lbl = ctk.CTkLabel(self, text="Final: ₹0",
                                       font=("Arial", 18, "bold"),
                                       text_color=theme.PRIMARY)
        self.final_lbl.pack(pady=2)

        ctk.CTkButton(self, text="✓  Place Order", width=540, height=48,
                      fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
                      font=("Arial", 14, "bold"), corner_radius=10,
                      command=self.place_order).pack(pady=16, padx=24)

    def add_to_cart(self):
        name = self.fvar.get()
        if name not in self.fmap: return
        try: qty = int(self.qty.get()); assert qty > 0
        except: return
        fid, price = self.fmap[name]
        for item in self.cart:
            if item["flower_id"] == fid:
                item["quantity"] += qty
                item["subtotal"] = item["quantity"] * price
                self.render_cart(); return
        self.cart.append({"flower_id":fid,"name":name,"quantity":qty,
                           "unit_price":price,"subtotal":qty*price})
        self.render_cart()

    def render_cart(self):
        for w in self.cart_frame.winfo_children(): w.destroy()
        if not self.cart:
            ctk.CTkLabel(self.cart_frame, text="Cart is empty",
                         text_color=theme.TEXT_GRAY).pack(pady=10); return
        for i, item in enumerate(self.cart):
            rf = ctk.CTkFrame(self.cart_frame, fg_color="#16213E", corner_radius=8)
            rf.pack(fill="x", pady=3)
            ctk.CTkLabel(rf, text=f"🌸 {item['name']}",
                         font=("Arial", 12), text_color="white",
                         width=200, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(rf, text=f"x{item['quantity']}",
                         font=("Arial", 12), text_color=theme.TEXT_GRAY,
                         width=40).pack(side="left")
            ctk.CTkLabel(rf, text=f"₹{item['unit_price']}",
                         font=("Arial", 12), text_color=theme.TEXT_GRAY,
                         width=80).pack(side="left")
            ctk.CTkLabel(rf, text=f"₹{item['subtotal']:.0f}",
                         font=("Arial", 12, "bold"),
                         text_color=theme.PRIMARY).pack(side="left")
            ctk.CTkButton(rf, text="✕", width=28, height=26,
                          fg_color=theme.DANGER, corner_radius=6,
                          command=lambda idx=i: [self.cart.pop(idx),
                                                  self.render_cart()]).pack(
                                                      side="right", padx=8, pady=4)
        self.update_totals()

    def update_totals(self):
        total = sum(i["subtotal"] for i in self.cart)
        try: disc = float(self.disc.get())
        except: disc = 0.0
        final = total - total * disc / 100
        self.total_lbl.configure(text=f"Total: ₹{total:.0f}")
        self.final_lbl.configure(text=f"Final: ₹{final:.0f}")

    def place_order(self):
        if not self.cart: return
        cid = self.cmap.get(self.cvar.get())
        if not cid: return
        try: disc = float(self.disc.get())
        except: disc = 0.0
        oid = create_order(cid, self.staff["id"], self.cart, disc)
        self.destroy()
        self.parent.refresh()
        ReceiptWindow(self.parent, oid)


class ReceiptWindow(ctk.CTkToplevel):
    def __init__(self, parent, order_id):
        super().__init__(parent)
        self.title(f"Receipt #{order_id}")
        self.geometry("440x600")
        self.configure(fg_color=theme.BG_DARK)
        self.resizable(False, False)
        self._build(order_id)

    def _build(self, oid):
        order, items = get_order_details(oid)
        if not order:
            ctk.CTkLabel(self, text="Not found").pack(pady=20); return

        card = ctk.CTkFrame(self, fg_color="#0F0F23", corner_radius=16)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        hdr = ctk.CTkFrame(card, fg_color=theme.PRIMARY, corner_radius=12)
        hdr.pack(fill="x", padx=16, pady=(16,12))
        ctk.CTkLabel(hdr, text="🌸  Flowerina",
                     font=("Arial", 20, "bold"),
                     text_color="white").pack(pady=(12,2))
        ctk.CTkLabel(hdr, text="Official Receipt",
                     font=("Arial", 11),
                     text_color="#FFE5D0").pack(pady=(0,12))

        ctk.CTkLabel(card, text=f"Order #{order['id']}  •  {order['order_date'][:16]}",
                     font=("Arial", 11),
                     text_color=theme.TEXT_GRAY).pack(pady=4)

        ctk.CTkFrame(card, height=1, fg_color="#2A2A4A").pack(fill="x", padx=16, pady=6)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(fill="x", padx=20, pady=4)
        for label, val in [("Customer", order["customer"]),
                            ("Phone",    order["customer_phone"] or "-"),
                            ("Served by",order["staff"])]:
            r = ctk.CTkFrame(info, fg_color="transparent")
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=label, font=("Arial", 11),
                         text_color=theme.TEXT_GRAY, width=80,
                         anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=val, font=("Arial", 11),
                         text_color="white").pack(side="left")

        ctk.CTkFrame(card, height=1, fg_color="#2A2A4A").pack(fill="x", padx=16, pady=6)

        ctk.CTkLabel(card, text="Items", font=("Arial", 12, "bold"),
                     text_color=theme.PRIMARY).pack(anchor="w", padx=20)
        for item in items:
            r = ctk.CTkFrame(card, fg_color="transparent")
            r.pack(fill="x", padx=20, pady=2)
            ctk.CTkLabel(r, text=f"🌸 {item['flower']} x{item['quantity']}",
                         font=("Arial", 11), text_color="white").pack(side="left")
            ctk.CTkLabel(r, text=f"₹{item['subtotal']:.0f}",
                         font=("Arial", 11, "bold"),
                         text_color=theme.PRIMARY).pack(side="right")

        ctk.CTkFrame(card, height=1, fg_color="#2A2A4A").pack(fill="x", padx=16, pady=8)

        for label, val, highlight in [
            ("Subtotal",     f"₹{order['total_amount']:.0f}", False),
            ("Discount",     f"{order['discount']}%",          False),
            ("Final Amount", f"₹{order['final_amount']:.0f}",  True),
        ]:
            r = ctk.CTkFrame(card, fg_color="#16213E" if highlight else "transparent",
                             corner_radius=8)
            r.pack(fill="x", padx=16, pady=2)
            ctk.CTkLabel(r, text=label,
                         font=("Arial", 13 if highlight else 12,
                               "bold" if highlight else "normal"),
                         text_color="white").pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(r, text=val,
                         font=("Arial", 13 if highlight else 12,
                               "bold" if highlight else "normal"),
                         text_color=theme.PRIMARY if highlight else theme.TEXT_GRAY
                         ).pack(side="right", padx=10)

        ctk.CTkLabel(card, text="Thank you for choosing Flowerina! 🌸",
                     font=("Arial", 11), text_color=theme.TEXT_GRAY).pack(pady=12)

        ctk.CTkButton(self, text="Close", width=380, height=42,
                      fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
                      corner_radius=10,
                      command=self.destroy).pack(pady=(0,16))
