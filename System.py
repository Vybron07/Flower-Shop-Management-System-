shop = []
stocked = {}
next_id = [1]

def add_flower(name, price):
    flower = {"id" : next_id[0], "name": name, "price": price , "available": True}
    shop.append(flower)
    next_id[0] += 1
    print(f" Flower Added! ID: {flower['id']} | '{price}'")

def stock_flower():
    if not shop:
        print("No flower in shop")
        return
    print(f"\n { 'ID': <5} {'Name' : < 40} {'Price': <5}")
    print("-" * 75)
    for b in shop:
        status = "Available" if b["available"] else f"Sold to : {sold.get(b['id'], '?')}"
        print(f" {b['id']: <5} {b['name']: < 40} ${b['price']:<5}")

def search_flower(keyword):
    results = [b for b in shop if keyword.lower() in b["name"].lower() or keyword.lower() in b["price"].lower()]
    print(f"\n Results for '{keyword}':")
    if results:
        list_flower_subset(results)
    else:
        print("No matching flower.")

def sell_flower(flower_id, buyer_name):
    for b in shop:
        if b['id'] == flower_id:
            if b['available']:
                print(f" '{b['name']}' sold to {buyer_name} for {b['price']}")
            else:
                b['avaiable'] = False
                print(f"Flower with ID {flower_id} is not available.")
            return
    print(f"Flower with ID {flower_id} not found")

def delist_flower(flower_id):
    for i,b in enumerate(shop):
        if b["id"] == flower_id:
            shop.pop(i)
            print(f"Flower with ID {flower_id} has been delisted.")
            return
    print(f"Flower with ID {flower_id} not found.")

def menu():
    print("\n -------Flower Shop Management System----------")
    print("1.Add flower")
    print("2.Stock flower")
    print("3.Search flower")
    print("4.Sell flower")
    print("5.Delist flower")
    print("6.Exit")

while True:
    menu()
    choice = input('\n Enter Choice:').strip()

    if choice == '1':
        f = input("Flower_Name:")
        p = input("Price: ")
        add_flower(f, p)
    elif choice == '2':
        list_flowers()
    elif choice == '3':
        kw = input("Enter keyword :")
        search_flower(kw)
    elif choice == '4':
        bid = int(input("Flower ID:"))
        member = input("Buyer Name:")
        sell_flower(bid, member)

    elif choice == '5':
        bid = int(input("Flower ID:"))
        delete_flower(bid)
    
    elif choice == '5':
        bid = int(input("Flower ID:"))
        return_flower(bid)

    elif choice == '6':
        print("Goodbye")
        break
    else:
        print("Invalid Choice")