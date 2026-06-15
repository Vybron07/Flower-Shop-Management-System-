import customtkinter as ctk
from database import (get_all_orders, create_order, get_order_details,
                      update_order_status, get_all_customers, get_all_flowers)

class OrdersFrame(ctk.CTkFrame):
    def __init__(self, parent, staff):
        super().__init__(parent, fg_color="transparent")
        self.staff = staff
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(top, text="Orders & Billing",
                     font=("Arial", 22, "bold")).pack(side="left")
        ctk.CTkButton(top, text="+ New Order", width=120,
                      command=self.open_new_order).pack(side="right")

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 10))
        self.filter_var = ctk.StringVar(value="All")
        for status in ["All", "Pending", "Completed", "Cancelled"]:
            ctk.CTkRadioButton(bar, text=status,
                               variable=self.filter_var,
                               value=status,
                               command=self.refresh).pack(side="left", padx=10)

        headers = ["Order #", "Customer", "Staff", "Date",
                   "Total", "Discount", "Final", "Status", "Actions"]
        hf = ctk.CTkFrame(self, fg_color="transparent")
        hf.pack(fill="x")
        for j, h in enumerate(headers):
            ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"),
                         text_color="gray").grid(row=0, column=j,
                                                  padx=8, pady=4, sticky="w")

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        orders = get_all_orders()
        fv = self.filter_var.get()
        if fv != "All":
            orders = [o for o in orders if o["status"] == fv]

        if not orders:
            ctk.CTkLabel(self.scroll, text="No orders found.",
                         text_color="gray").pack(pady=30)
            return

        status_colors = {
            "Pending":   "#F59E0B",
            "Completed": "#10B981",
            "Cancelled": "#EF4444"
        }

        for i, order in enumerate(orders):
            bg = ("gray92", "gray18") if i % 2 == 0 else ("white", "gray15")
            rf = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=6)
            rf.pack(fill="x", pady=2)

            vals = [f"#{order['id']}", order["customer"], order["staff"],
                    order["order_date"][:16],
                    f"₹{order['total_amount']:.2f}",
                    f"{order['discount']}%",
                    f"₹{order['final_amount']:.2f}"]

            for j, v in enumerate(vals):
                ctk.CTkLabel(rf, text=v,
                             font=("Arial", 12)).grid(row=0, column=j,
                                                       padx=8, pady=8, sticky="w")

            sc = status_colors.get(order["status"], "gray")
            ctk.CTkLabel(rf, text=order["status"],
                         font=("Arial", 11, "bold"),
                         text_color=sc).grid(row=0, column=7, padx=8, sticky="w")

            bf = ctk.CTkFrame(rf, fg_color="transparent")
            bf.grid(row=0, column=8, padx=8)
            ctk.CTkButton(bf, text="Receipt", width=65, height=26,
                          command=lambda oid=order["id"]: self.show_receipt(oid)
                          ).pack(side="left", padx=2)
            if order["status"] == "Pending":
                ctk.CTkButton(bf, text="Complete", width=75, height=26,
                              fg_color="#10B981", hover_color="#059669",
                              command=lambda oid=order["id"]: self.mark_complete(oid)
                              ).pack(side="left", padx=2)
                ctk.CTkButton(bf, text="Cancel", width=65, height=26,
                              fg_color="#EF4444", hover_color="#DC2626",
                              command=lambda oid=order["id"]: self.mark_cancel(oid)
                              ).pack(side="left", padx=2)

    def open_new_order(self):
        dialog = NewOrderDialog(self, self.staff)
        dialog.grab_set()

    def mark_complete(self, order_id):
        update_order_status(order_id, "Completed")
        self.refresh()

    def mark_cancel(self, order_id):
        update_order_status(order_id, "Cancelled")
        self.refresh()

    def show_receipt(self, order_id):
        ReceiptWindow(self, order_id)


class NewOrderDialog(ctk.CTkToplevel):
    def __init__(self, parent, staff):
        super().__init__(parent)
        self.parent = parent
        self.staff = staff
        self.title("New Order")
        self.geometry("580x640")
        self.cart = []
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="New Order",
                     font=("Arial", 18, "bold")).pack(pady=(16, 4))

        ctk.CTkLabel(self, text="Select Customer").pack(anchor="w", padx=20)
        customers = get_all_customers()
        self.customer_map = {c["name"]: c["id"] for c in customers}
        self.customer_var = ctk.StringVar(
            value=customers[0]["name"] if customers else "")
        ctk.CTkOptionMenu(self, values=list(self.customer_map.keys()) or ["No customers"],
                          variable=self.customer_var,
                          width=520).pack(padx=20, pady=(0, 10))

        ctk.CTkLabel(self, text="Add Flowers to Cart").pack(anchor="w", padx=20)
        flowers = get_all_flowers()
        self.flower_map = {f["name"]: (f["id"], f["price"]) for f in flowers}

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=4)
        self.flower_var = ctk.StringVar(
            value=list(self.flower_map.keys())[0] if self.flower_map else "")
        ctk.CTkOptionMenu(row, values=list(self.flower_map.keys()) or ["No flowers"],
                          variable=self.flower_var,
                          width=260).pack(side="left", padx=(0, 8))
        self.qty_var = ctk.StringVar(value="1")
        ctk.CTkEntry(row, textvariable=self.qty_var,
                     placeholder_text="Qty", width=80).pack(side="left", padx=(0, 8))
        ctk.CTkButton(row, text="+ Add to Cart", width=120,
                      command=self.add_to_cart).pack(side="left")

        ctk.CTkLabel(self, text="Cart",
                     font=("Arial", 13, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        self.cart_frame = ctk.CTkScrollableFrame(self, height=160)
        self.cart_frame.pack(fill="x", padx=20)

        disc_row = ctk.CTkFrame(self, fg_color="transparent")
        disc_row.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(disc_row, text="Discount %:").pack(side="left", padx=(0, 8))
        self.disc_var = ctk.StringVar(value="0")
        ctk.CTkEntry(disc_row, textvariable=self.disc_var, width=80).pack(side="left")

        self.total_label = ctk.CTkLabel(self, text="Total: ₹0.00",
                                         font=("Arial", 15, "bold"))
        self.total_label.pack(pady=4)
        self.final_label = ctk.CTkLabel(self, text="Final: ₹0.00",
                                         font=("Arial", 16, "bold"),
                                         text_color="#10B981")
        self.final_label.pack(pady=2)
        self.disc_var.trace("w", lambda *a: self.update_totals())

        ctk.CTkButton(self, text="Place Order ✓", width=520, height=44,
                      command=self.place_order).pack(pady=16, padx=20)

    def add_to_cart(self):
        name = self.flower_var.get()
        if not name or name not in self.flower_map:
            return
        try:
            qty = int(self.qty_var.get())
            if qty <= 0:
                return
        except ValueError:
            return
        fid, price = self.flower_map[name]
        for item in self.cart:
            if item["flower_id"] == fid:
                item["quantity"] += qty
                item["subtotal"] = item["quantity"] * price
                self.render_cart()
                return
        self.cart.append({"flower_id": fid, "name": name, "quantity": qty,
                           "unit_price": price, "subtotal": qty * price})
        self.render_cart()

    def render_cart(self):
        for w in self.cart_frame.winfo_children():
            w.destroy()
        if not self.cart:
            ctk.CTkLabel(self.cart_frame, text="Cart is empty.",
                         text_color="gray").pack(pady=10)
            return
        for i, item in enumerate(self.cart):
            rf = ctk.CTkFrame(self.cart_frame, fg_color="transparent")
            rf.pack(fill="x", pady=2)
            ctk.CTkLabel(rf, text=f"🌸 {item['name']}",
                         font=("Arial", 12), width=180, anchor="w").pack(side="left")
            ctk.CTkLabel(rf, text=f"x{item['quantity']}",
                         font=("Arial", 12), width=50).pack(side="left")
            ctk.CTkLabel(rf, text=f"₹{item['unit_price']} each",
                         font=("Arial", 12), width=100,
                         text_color="gray").pack(side="left")
            ctk.CTkLabel(rf, text=f"₹{item['subtotal']:.2f}",
                         font=("Arial", 12, "bold"), width=80).pack(side="left")
            ctk.CTkButton(rf, text="✕", width=28, height=26,
                          fg_color="#EF4444", hover_color="#DC2626",
                          command=lambda idx=i: self.remove_item(idx)).pack(side="right")
        self.update_totals()

    def remove_item(self, idx):
        self.cart.pop(idx)
        self.render_cart()

    def update_totals(self):
        total = sum(i["subtotal"] for i in self.cart)
        try:
            disc = float(self.disc_var.get())
        except ValueError:
            disc = 0.0
        final = total - (total * disc / 100)
        self.total_label.configure(text=f"Total: ₹{total:.2f}")
        self.final_label.configure(text=f"Final: ₹{final:.2f}")

    def place_order(self):
        if not self.cart:
            return
        customer_id = self.customer_map.get(self.customer_var.get())
        if not customer_id:
            return
        try:
            disc = float(self.disc_var.get())
        except ValueError:
            disc = 0.0
        order_id = create_order(customer_id, self.staff["id"], self.cart, disc)
        self.destroy()
        self.parent.refresh()
        ReceiptWindow(self.parent, order_id)


class ReceiptWindow(ctk.CTkToplevel):
    def __init__(self, parent, order_id):
        super().__init__(parent)
        self.title(f"Receipt — Order #{order_id}")
        self.geometry("420x580")
        self.resizable(False, False)
        self._build(order_id)

    def _build(self, order_id):
        order, items = get_order_details(order_id)
        if not order:
            ctk.CTkLabel(self, text="Order not found.").pack(pady=20)
            return

        card = ctk.CTkFrame(self, corner_radius=12)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(card, text="🌸 Flowerina",
                     font=("Arial", 20, "bold")).pack(pady=(20, 2))
        ctk.CTkLabel(card, text="Receipt",
                     font=("Arial", 13), text_color="gray").pack()
        ctk.CTkLabel(card, text=f"Order #{order['id']}  •  {order['order_date'][:16]}",
                     font=("Arial", 11), text_color="gray").pack(pady=(2, 10))

        ctk.CTkFrame(card, height=1, fg_color="gray").pack(fill="x", padx=16, pady=4)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(info, text=f"Customer:  {order['customer']}",
                     font=("Arial", 12)).pack(anchor="w")
        ctk.CTkLabel(info, text=f"Phone:        {order['customer_phone'] or '-'}",
                     font=("Arial", 12)).pack(anchor="w")
        ctk.CTkLabel(info, text=f"Served by:  {order['staff']}",
                     font=("Arial", 12)).pack(anchor="w")

        ctk.CTkFrame(card, height=1, fg_color="gray").pack(fill="x", padx=16, pady=6)

        ctk.CTkLabel(card, text="Items",
                     font=("Arial", 12, "bold")).pack(anchor="w", padx=16)
        for item in items:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=2)
            ctk.CTkLabel(row, text=f"🌸 {item['flower']} x{item['quantity']}",
                         font=("Arial", 12)).pack(side="left")
            ctk.CTkLabel(row, text=f"₹{item['subtotal']:.2f}",
                         font=("Arial", 12)).pack(side="right")

        ctk.CTkFrame(card, height=1, fg_color="gray").pack(fill="x", padx=16, pady=6)

        totals = ctk.CTkFrame(card, fg_color="transparent")
        totals.pack(fill="x", padx=16)
        for label, val, bold in [
            ("Subtotal",     f"₹{order['total_amount']:.2f}", False),
            ("Discount",     f"{order['discount']}%",          False),
            ("Final Amount", f"₹{order['final_amount']:.2f}",  True),
        ]:
            row = ctk.CTkFrame(totals, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=label,
                         font=("Arial", 13, "bold" if bold else "normal")).pack(side="left")
            ctk.CTkLabel(row, text=val,
                         font=("Arial", 13, "bold" if bold else "normal"),
                         text_color="#10B981" if bold else None).pack(side="right")

        ctk.CTkFrame(card, height=1, fg_color="gray").pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(card, text="Thank you for your purchase! 🌸",
                     font=("Arial", 12), text_color="gray").pack(pady=(0, 16))

        ctk.CTkButton(self, text="Close", width=360,
                      command=self.destroy).pack(pady=(0, 16))
