from django.contrib import admin

# Register your models here.







import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
import csv
from django.contrib import messages
from .models import *

customer_details = CusTable(200)
products = Carttable(250)
search_tree = products.build_tree()

def members(request):
    """
    Renders the home page template.

    Returns:
        HttpResponse: Response containing the rendered home page template.
    """
    template = loader.get_template('home.html')
    return HttpResponse(template.render())

def intro(request):
    """
    Renders the intro text template.

    Returns:
        HttpResponse: Response containing the rendered intro text template.
    """
    template = loader.get_template('introtext.html')
    return HttpResponse(template.render())

def login(request):
    
    if request.method == 'POST':
        user_mail = request.POST['mail']
        user_password = request.POST['password']
        if user_mail == "client@gmail.com" and user_password == "clienthappy":
            return redirect("user_update_quantity")
        else:
            with open("./members/userdetails.csv", "r") as f:
                pass_details = csv.reader(f)
                for row in pass_details:
                    if row[0] == user_mail and row[1] == user_password:
                        request.session["username"] = user_mail
                        return redirect("dashboard")

    return render(request, "loginpage.html")

def register(request):
  
    if request.method == 'POST':
        user_mail = request.POST['mail']
        user_password = request.POST['password']
        list_user = [user_mail, user_password]
        with open("./members/userdetails.csv", "a", newline="") as f:
            csvwrite = csv.writer(f)
            csvwrite.writerow(list_user)
            return redirect("/members/login")

    return render(request, "register-page.html")

def dashboard(request):
   
    username = request.session.get("username")
    slides_queue = Queue.import_from_csv('./members/slides.csv')

    slide_list = []
    fruits = products.get_node_addresses()
    while not slides_queue.is_empty():
        slide = slides_queue.dequeue()
        slide_list.append(slide)
    context = {
        "username": username,
        'slides_queue': slide_list,
        "fruits": fruits,
    }

    return render(request, "dashboard.html", context)

def dummy(request):
    
    fruits = products.get_node_addresses()

    context = {
        "fruits": fruits,
    }

    if request.method == "POST":
        order = request.POST.get("order")
        if order == "lowtohigh":
            context["fruits"] = search_tree.inorder_traversal()

    return render(request, "dummy.html", context)

def price(request):
  
    items = products.get_node_addresses()

    context = {
        "items": items,
    }

    if request.method == "POST":
        order = request.POST.get("order")
        if order == "lowtohigh":
            context["items"] = search_tree.inorder_traversal()
            return render(request, "products.html", context)
        elif order == "hightolow":
            context["items"] = [search_tree.inorder_traversal()[i] for i in range(len(search_tree.inorder_traversal()) - 1, -1, -1)]
            return render(request, "products.html", context)

def veggies(request):
  
    global products
    items = products.get_node_addresses()

    if request.method == "POST":
        product_name = request.POST["pname"]
        product_quantity = int(request.POST["total-quantity"])
        product_description = request.POST["pdescription"]
        product_price = float(request.POST["pprice"])
        product_image = request.POST["pimage"]
        cart_list = []
        total_price = round(product_price * product_quantity, 1)
        cart_list.append(["Fruits", product_name, product_description, total_price, product_quantity, product_image])
        with open("./members/cart-items.csv", "a", newline="") as f:
            csvwrite = csv.writer(f)
            csvwrite.writerow(cart_list[-1])

    return render(request, "products.html", {"items": items})

def add_cart(request):
  
    global cart_items
    cart_items = Carttable(129)
    build_cart_from_csv('./members/cart-items.csv', cart_items)
    username = request.session.get("username")
    p = {"items": []}

    if request.method == "POST":
        cart_items.remove_zero_quantity_nodes()
        updated_quantity = request.POST["total-quantity"]
        product_name = request.POST["pname"]
        p = {"items": [], "username": username, "totalprice": cart_items.get_total_amount(),
             "search_quantity": products.search(product_name).quantity}
        cart_items.modify_quantity(product_name, updated_quantity, products)
        build_csv_from_cart(cart_items, './members/cart-items.csv')

    p["totalprice"] = cart_items.get_total_amount()
    items = cart_items.get_node_addresses()
    p["items"] = items

    return render(request, "addtocart.html", p)


def user_update_quantity(request):
  
    if request.method == "POST":
        updated_quantity = request.POST["total-quantity"]
        product_name = request.POST["pname"]
        products.update_user_quantity(product_name, updated_quantity)
        build_csv_from_cart(products, "./members/product-details.csv")
    return render(request, "userproduct.html", {"items": products.get_node_addresses()})

def search(request):
   
    if request.method == "POST":
        search_item = request.POST["search"]
        a = search_tree.search_all_starts_with(search_item)
        return render(request, "products.html", {"items": a})
    return render(request, "search.html")

def checkout(request):
  

    global cart_items
    cart_items = Carttable(129)
    build_cart_from_csv('./members/cart-items.csv', cart_items)

    p = {"items": cart_items.get_node_addresses(), "totalprice": cart_items.get_total_amount()}

    if request.method == "POST":
        return redirect("customerdetails")

    return render(request, "checkout.html", p)

def customerdetails(request):
  
    import random
    p = {"cus_details": ""}
    username = request.session.get("username")
    node = customer_details.search(username)

    if request.method == "POST":
        customer_name = request.POST["name"]
        address1 = request.POST["address1"]
        address2 = request.POST["address2"]
        pincode = request.POST["pincode"]
        time_slot = request.POST["timeslot"]
        customer_mobile = request.POST["mobile"]
        address = address1 + "\n" + address2 + "\n" + pincode
        customer_details.modify_customer(username, customer_name, customer_mobile, pincode, address1, address2)
        build_csv_from_customer(customer_details, "./members/userdetails.csv")
        finalcart = Carttable(200)
        build_cart_from_csv("./members/cart-items.csv", finalcart)
        for i in finalcart.get_node_addresses():
            products.modify_user_quantity(i.name, i.quantity)
        build_csv_from_cart(products, "./members/product-details.csv")
        with open("./members/orders.csv", "a", newline="") as csv_file:
            csvwrite = csv.writer(csv_file)
            csvwrite.writerow([random.randint(0, 1111), customer_name, finalcart.get_order_details(), time_slot, finalcart.get_total_amount()])
        order_no = random.randint(0, 1111)
        ordered_products = finalcart.get_order_details()
        timeslot = request.POST["timeslot"]
        total_amount = finalcart.get_total_amount()
        sender_email = "sanjeevi2210539@ssn.edu.in"
        sender_password = "Sanjeevi@05"
        subject = "FreshFare Service"
        with open("./members/orders.csv", "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                order_no = row["orderno"]
                customer = row["customer"]
                list_of_orders = row["list_of_orders"]
                total_amount = row["total_amount"]
                status = row["status"]

        message = generate_email_message(order_no, customer, address, list_of_orders, total_amount, status)

        receiver_email = username
        send_email(sender_email, sender_password, receiver_email, subject, message)
        receiver_email_email = "san5jeevi55@gmail.com"
        send_email(sender_email, sender_password, receiver_email, subject, message)

        f = open("./members/cart-items.csv", "w")
        csvwriter = csv.writer(f)
        csvwriter.writerow(["category", "name", "description", "price", "quantity", "image", "\n"])
        f.close()

        messages.success(request, "Order placed successfully!")
        return redirect(add_cart)

    p = {"cus_details": node}
    return render(request, "customerdetails.html", p)

def user_manage_order(request):
    """
    Handles the user order management functionality.

    Retrieves the order details from the "orders.csv" file and populates a list of order objects.
    If the request method is POST, it updates the order status and CSV file based on the provided order number.
    
    Returns:
        HttpResponse: Response containing the rendered user_order_accesspage template.
    """
    list_of_details = []
    with open("./members/orders.csv", "r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            order_no = row["orderno"]
            customer_name = row["customer"]
            list_of_orders = ast.literal_eval(row["list_of_orders"])
            time_delivery = row["time_delivery"]
            total_amount = row["total_amount"]
            status = row["status"]
            final_product = Carttable(1299)
            for i in list_of_orders:
                final_product.search_and_modify_quantity(i[0], products, i[1])
            list_of_details.append(orders(order_no, customer_details.search_by_name(customer_name),
                                         final_product.get_node_addresses(), time_delivery, total_amount, status))
    if request.method == 'POST':
        num = request.POST["order_num"]
        list_of_details = search_order_status(list_of_details, "./members/orders.csv", num)

    return render(request, "user_order_accesspage.html", {"orders": list_of_details})

def search_order_status(list_of_orders, csv_file, number):

    for order in list_of_orders:
        if order.order_num == number:
            order.status = "Delivered"


    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    for row in rows:
        if row["orderno"] == number:
            row["status"] = "Delivered"

    with open(csv_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return list_of_orders

# Rest of the code...
