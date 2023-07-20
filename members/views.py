import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render,redirect
import csv
from django.contrib import messages 
from .models import *
customer_details=CusTable(200)
build_customer_from_csv("./members/userdetails.csv",customer_details)

global products
products=Carttable(250)
build_cart_from_csv("./members/product-details.csv",products)
search_tree=products.build_tree()
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
  """
    Handles the login functionality.

    If the request method is POST and the provided email and password match the predefined values,
    it redirects to the `user_update_quantity` view. Otherwise, it checks the provided email and
    password against the values stored in the "userdetails.csv" file and redirects to the `dashboard`
    view if there's a match.

    Returns:
        HttpResponseRedirect: Response for successful login or redirection to the login page.
    """
  if request.method == 'POST':
    user_mail=request.POST['mail']
    user_password=request.POST['password']
    if user_mail =="client@gmail.com" and user_password=="clienthappy":
      return redirect("user_update_quantity")
    else:
      with open("./members/userdetails.csv","r") as f:
        pass_details=csv.reader(f)
        for row in pass_details:
          if row[0]==user_mail and row[1]==user_password:
            request.session["username"]=user_mail
            return redirect("dashboard")
    
  return render(request,"loginpage.html")


def register(request):
  """
    Handles the user registration functionality.

    If the request method is POST, it retrieves the provided email and password, appends them to
    the "userdetails.csv" file, and redirects to the login page.

    Returns:
        HttpResponseRedirect: Response for successful registration or redirection to the registration page.
    """
  if request.method == 'POST':
    user_mail=request.POST['mail']
    user_password=request.POST['password']
    list_user=[user_mail,user_password]
    with open("./members/userdetails.csv","a", newline="") as f:
      csvwrite=csv.writer(f)
      csvwrite.writerow(list_user)
      return redirect("/members/login")

  return render(request,"register-page.html")

def dashboard(request):
  """
    Renders the dashboard template.

    Retrieves the username from the session and builds a context that includes the username, a list of slides,
    and a list of fruits. The context is then passed to the template for rendering.

    Returns:
        HttpResponse: Response containing the rendered dashboard template.
    """
  global username
  username=request.session.get("username")
  slides_queue = Queue.import_from_csv('./members/slides.csv')
  slide_list = []
  fruits = products.get_node_addresses()
  while not slides_queue.is_empty():
    slide = slides_queue.dequeue()
    slide_list.append(slide)
    print(slide_list)
  context={
    "username":username,
    'slides_queue': slide_list,
    "fruits":fruits,
  }

  return render(request,"dashboard.html",context)


def dummy(request):
  """
    Renders the dummy template and handles the ordering of products based on user selection (low to high).

    Returns:
        HttpResponse: Response containing the rendered dummy template.
    """
  fruits = products.get_node_addresses()

  context={
    "fruits":fruits,

  }
  if request.method == "POST":
    order=request.POST.get("order")
    if order == "lowtohigh":
      context["fruits"]=search_tree.inorder_traversal()

       
  return render(request,"dummy.html",context)

def price(request):
  """
    Renders the products template and handles the ordering of items based on user selection (low to high or high to low).

    Returns:
        HttpResponse: Response containing the rendered products template.
    """
  items = products.get_node_addresses()

  context={
    "items":items,

  }
  if request.method == "POST":
    order=request.POST.get("order")
    if order == "lowtohigh":
      context["items"]=search_tree.inorder_traversal()
      return render(request,"products.html",context)
    elif order == "hightolow":
      context["items"]=[search_tree.inorder_traversal()[i] for i in range(len(search_tree.inorder_traversal())-1,-1,-1)]
      return render(request,"products.html",context)
       
  
def veggies(request):
    """
    Renders the products template for displaying vegetable items.
    Handles adding selected items to the cart.

    Returns:
        HttpResponse: Response containing the rendered products template.
    """
    items = products.get_node_addresses()
    if request.method == "POST":
        product_name = request.POST["pname"]
        product_quantity = int(request.POST["total-quantity"])
        product_description = request.POST["pdescription"]
        product_price = float(request.POST["pprice"])
        product_image = request.POST["pimage"]
        cart_list = []
        total_price = round(product_price * product_quantity, 1)
        cart_list.append(["Fruits", product_name, product_description, total_price, product_quantity,product_image  ])
        with open("./members/cart-items.csv", "a", newline="") as f:
            csvwrite = csv.writer(f)
            csvwrite.writerow(cart_list[-1])
    return render(request, "products.html", {"items": items})

def add_cart(request):
    """
    Handles the addition of items to the cart.

    Retrieves the updated quantity from the request, modifies the quantity in the cart,
    and rebuilds the CSV file. Finally, it renders the add-to-cart template with the updated cart items.

    Returns:
        HttpResponse: Response containing the rendered add-to-cart template.
    """
    global cart_items
    cart_items = Carttable(129)
    build_cart_from_csv('./members/cart-items.csv', cart_items)
    username = request.session.get("username")
    p={"items":[]}
    if request.method == "POST":
        cart_items.remove_zero_quantity_nodes()
        updated_quantity = request.POST["total-quantity"]
        product_name = request.POST["pname"]
        p = {"items": [], "username": username,"totalprice":cart_items.get_total_amount(),"search_quantity":products.search(product_name).quantity}
        cart_items.modify_quantity(product_name, updated_quantity,products)
        build_csv_from_cart(cart_items,'./members/cart-items.csv')
    p["totalprice"]=cart_items.get_total_amount()
    items = cart_items.get_node_addresses()
    p["items"] = items
    return render(request, "addtocart.html", p)



def user_update_quantity(request):
  """
    Handles the update of product quantity by the user.

    If the request method is POST, it retrieves the updated quantity from the request,
    updates the quantity in the product list, and rebuilds the CSV file.

    Returns:
        HttpResponse: Response containing the rendered userproduct template.
    """
  if request.method == "POST":
      updated_quantity = request.POST["total-quantity"]
      product_name=request.POST["pname"]
      products.update_user_quantity(product_name, updated_quantity)
      build_csv_from_cart(products,"./members/product-details.csv")
  return render(request, "userproduct.html",{"items": products.get_node_addresses()})

def search(request):
  """
    Handles the search functionality.

    If the request method is POST, it retrieves the search item from the request,
    performs a search using a search tree, and renders the products template with the search results.

    Returns:
        HttpResponse: Response containing the rendered products template.
    """
  if request.method == "POST":
    search_item=request.POST["search"]
    a=search_tree.search_all_starts_with(search_item)
    return render(request, "products.html",{"items": a})
  return render(request, "search.html") 


def checkout(request):
    """
  Handles the checkout functionality.

    If the request method is POST, it redirects to the customerdetails view.
    Otherwise, it builds the context with cart items and total price and renders the checkout template.

    Returns:
        HttpResponse or HttpResponseRedirect: Response for successful checkout or redirection to the checkout page.
    """
    global cart_items
    cart_items = Carttable(129)
    build_cart_from_csv('./members/cart-items.csv', cart_items)
    
    p={"items":cart_items.get_node_addresses(),"totalprice":cart_items.get_total_amount()  }
    if request.method =="POST":
       return redirect("customer_detail")
    return render(request, "checkout.html",p)




def customerdetails(request):
    """
    Handles the customer details functionality.

    If the request method is POST, it retrieves the customer details from the request,
    updates the customer information, rebuilds the "userdetails.csv" file,
    updates the product quantities, rebuilds the product CSV file, builds an order CSV file,
    sends an email to the customer and the admin with the order details, and redirects to the add_cart view.

    Returns:
        HttpResponse or HttpResponseRedirect: Response for successful order placement or redirection to the customerdetails page.
    """
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
        address=address1+"\n"+address2+"\n"+pincode
        customer_details.modify_customer(username, customer_name, customer_mobile, pincode, address1, address2)        
        build_csv_from_customer(customer_details, "./members/userdetails.csv")
        finalcart=Carttable(200)
        build_cart_from_csv("./members/cart-items.csv",finalcart)
        for i in finalcart.get_node_addresses():
           products.modify_user_quantity(i.name,i.quantity)
        build_csv_from_cart(products, "./members/product-details.csv")
        with open("./members/orders.csv","a",newline="") as csv_file:
            csvwrite=csv.writer(csv_file)
            csvwrite.writerow([random.randint(0,1111),customer_name,finalcart.get_order_details(),time_slot,finalcart.get_total_amount()])
        order_no = random.randint(0, 1111)
        ordered_products = finalcart.get_order_details()
        # Retrieve the timeslot and total amount from the request or calculate them
        timeslot = request.POST["timeslot"]
        total_amount = finalcart.get_total_amount()
        sender_email="sanjeevi2210539@ssn.edu.in"
        sender_password="Sanjeevi@05"
        subject="FreshFare Service"
        with open("./members/orders.csv", "r") as csv_file:
          csv_reader = csv.DictReader(csv_file)
          for row in csv_reader:
              order_no = row["orderno"]
              customer = row["customer"]
              list_of_orders = row["list_of_orders"]
              total_amount = row["total_amount"]
              status = row["status"]
        
        message = generate_email_message(order_no, customer,address, list_of_orders, total_amount, status)
        

        receiver_email=username
        # Send the email with customer details and order information
        send_email(
            sender_email,
            sender_password,
            receiver_email,
            subject,
            message
            )
        receiver_email_email="san5jeevi55@gmail.com"
        send_email(
            sender_email,
            sender_password,
            receiver_email,
            subject,
            message
            )






        f=open("./members/cart-items.csv","w")
        csvwriter=csv.writer(f)
        csvwriter.writerow(["category","name","description","price","quantity","image","\n"])
        f.close()
        messages.success(request, "Order placed successfully!")

        return redirect(add_cart)
           
    p = {"cus_details": node}
    return render(request, "customerdetails.html", p)


import ast
def user_manage_order(request):
  """
    Handles the user order management functionality.

    Retrieves the order details from the "orders.csv" file and populates a list of order objects.
    If the request method is POST, it updates the order status and CSV file based on the provided order number.
    
    Returns:
        HttpResponse: Response containing the rendered user_order_accesspage template.
    """
  list_of_details =[]
  with open("./members/orders.csv","r") as csv_file:
      reader = csv.DictReader(csv_file)
      for row in reader:
         
         order_no=row["orderno"]
         customer_name=row["customer"]
         global list_of_orders
         list_of_orders=ast.literal_eval(row["list_of_orders"])
         time_delivery=row["time_delivery"]
         total_amount=row["total_amount"]
         status=row["status"]
         final_product=Carttable(1299)
         for i in list_of_orders:
            final_product.search_and_modify_quantity(i[0],products,i[1])
         list_of_details.append(orders(order_no,customer_details.search_by_name(customer_name),final_product.get_node_addresses(),time_delivery,total_amount,status))
  if request.method == 'POST':
    num=request.POST["order_num"]
    print(num)
    list_of_details=search_order_status(list_of_details,"./members/orders.csv",num)


  return render(request,"user_order_accesspage.html",{"orders":list_of_details})


def search_order_status(list_of_orders, csv_file, number):
    """
    Searches for an order by order number and updates the status.

    Args:
        list_of_orders (list): List of order objects.
        csv_file (str): Path to the CSV file containing order details.
        number (str): Order number to search.

    Returns:
        list: Updated list of order objects.
    """
    for order in list_of_orders:
        if order.order_num == number:
            order.status = "Delivered"
            print(order.order_num)

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



