import smtplib
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Slide:
    """
    Represents a slide in a slideshow.
    """
    def __init__(self, image, caption, title, subtitle, offer):
        """
        Initializes a Slide object.
        
        Args:
            image (str): The image URL.
            caption (str): The caption of the slide.
            title (str): The title of the slide.
            subtitle (str): The subtitle of the slide.
            offer (str): The offer associated with the slide.
        """
        self.image = image
        self.caption = caption
        self.title = title
        self.subtitle = subtitle
        self.offer = offer


class Queue:
    """
    Represents a queue of slides for a slideshow.
    """
    def __init__(self):
        """
        Initializes a Queue object.
        """
        self.slides = []

    def enqueue(self, slide):
        """
        Adds a slide to the end of the queue.
        
        Args:
            slide (Slide): The slide to enqueue.
        """
        self.slides.append(slide)

    def dequeue(self):
        """
        Removes and returns the first slide from the queue.
        
        Returns:
            Slide: The first slide in the queue, or None if the queue is empty.
        """
        if not self.is_empty():
            return self.slides.pop(0)
        return None

    def is_empty(self):
        """
        Checks if the queue is empty.
        
        Returns:
            bool: True if the queue is empty, False otherwise.
        """
        return len(self.slides) == 0

    def export_to_csv(self, filename):
        """
        Exports the queue of slides to a CSV file.
        
        Args:
            filename (str): The filename of the CSV file.
        """
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Image', 'Caption', 'Title', 'Subtitle', 'Offer'])
            for slide in self.slides:
                writer.writerow([slide.image, slide.caption, slide.title, slide.subtitle, slide.offer])

    @classmethod
    def import_from_csv(cls, filename):
        """
        Imports a queue of slides from a CSV file.
        
        Args:
            filename (str): The filename of the CSV file.
            
        Returns:
            Queue: The imported queue of slides.
        """
        queue = cls()
        with open(filename, 'r', newline='') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                image, caption, title, subtitle, offer = row
                slide = Slide(image, caption, title, subtitle, offer)
                queue.enqueue(slide)
        return queue


class TreeNode:
    """
    Represents a node in a binary search tree.
    """
    def __init__(self, name, description, price, quantity, image, category):
        """
        Initializes a TreeNode object.
        
        Args:
            name (str): The name of the product.
            description (str): The description of the product.
            price (float): The price of the product.
            quantity (int): The quantity of the product.
            image (str): The image URL of the product.
            category (str): The category of the product.
        """
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity
        self.image = image
        self.category = category


class Carttable:
    """
    Represents a hash table for storing products in a shopping cart.
    """
    def __init__(self, size):
        """
        Initializes a Carttable object.
        
        Args:
            size (int): The size of the hash table.
        """
        self.size = size
        self.table = [None] * size

    def get_order_details(self):
        """
        Retrieves the order details from the cart.
        
        Returns:
            list: A list of [product, quantity] pairs representing the order details.
        """
        order_details = []
        items = self.get_node_addresses()

        for item in items:
            product = [item.name, item.quantity]
            order_details.append(product)

        return order_details

    def _hash_function1(self, key):
        """
        Performs the first hash function for the given key.
        
        Args:
            key (str): The key to hash.
        
        Returns:
            int: The hashed value.
        """
        total = 0
        if key is not None:  # Check if key is not empty
            for char in key:
                total += ord(char)
        return total % self.size

    def _hash_function2(self, key):
        """
        Performs the second hash function for the given key.
        
        Args:
            key (str): The key to hash.
        
        Returns:
            int: The hashed value.
        """
        total = 0
        for char in key:
            total += ord(char)
        return (total % (self.size - 1)) + 1

    def _hash(self, key, attempt):
        """
        Performs the hashing operation for the given key and attempt.
        
        Args:
            key (str): The key to hash.
            attempt (int): The current attempt count.
        
        Returns:
            int: The hashed index value.
        """
        return (self._hash_function1(key) + attempt * self._hash_function2(key)) % self.size

    def insert(self, name, description, price, quantity, image, category):
        """
        Inserts a product into the cart.
        
        Args:
            name (str): The name of the product.
            description (str): The description of the product.
            price (float): The price of the product.
            quantity (int): The quantity of the product.
            image (str): The image URL of the product.
            category (str): The category of the product.
        """
        attempt = 0
        index = self._hash(name, attempt)
        while self.table[index] is not None:
            attempt += 1
            index = self._hash(name, attempt)
        self.table[index] = TreeNode(name, description, price, quantity, image, category)

    def search(self, name):
        """
        Searches for a product in the cart by its name.
        
        Args:
            name (str): The name of the product to search.
        
        Returns:
            TreeNode: The matching product node, or None if not found.
        """
        attempt = 0
        index = self._hash(name, attempt)
        while self.table[index] is not None:
            if self.table[index].name == name:
                return self.table[index]
            attempt += 1
            index = self._hash(name, attempt)
        return None

    def modify_quantity(self, name, new_quantity, object):
        """
        Modifies the quantity of a product in the cart.
        
        Args:
            name (str): The name of the product to modify.
            new_quantity (int): The new quantity of the product.
            object (Carttable): The reference to the original cart table.
        """
        node = self.search(name)
        price_new = object.search(name).price
        if node is not None:
            node.quantity = new_quantity
            node.price = round(float(price_new) * float(new_quantity), 2)

    def modify_user_quantity(self, name, new_quantity):
        """
        Modifies the quantity of a product in the cart based on user input.
        
        Args:
            name (str): The name of the product to modify.
            new_quantity (int): The new quantity of the product.
        """
        node = self.search(name)
        if node is not None:
            node.quantity = node.quantity - new_quantity

    def update_user_quantity(self, name, new_quantity):
        """
        Updates the quantity of a product in the cart based on user input.
        
        Args:
            name (str): The name of the product to update.
            new_quantity (int): The new quantity of the product.
        """
        node = self.search(name)
        if node is not None:
            node.quantity = new_quantity

    def get_node_addresses(self):
        """
        Retrieves the addresses of nodes in the cart table.
        
        Returns:
            list: A list of node addresses.
        """
        addresses = []
        for node in self.table:
            if node is not None:
                addresses.append(node)
        return addresses

    def get_total_amount(self):
        """
        Calculates the total amount of the cart.
        
        Returns:
            float: The total amount.
        """
        total_price = 0
        items = self.get_node_addresses()
        for item in items:
            total_price += item.price
        return round(total_price, 3)

    def build_tree(self):
        """
        Builds a binary search tree from the cart table.
        
        Returns:
            BinarySearchTree: The binary search tree.
        """
        bst = BinarySearchTree()
        items = self.get_node_addresses()
        for item in items:
            bst.insert(item)
        return bst

    def remove_zero_quantity_nodes(self):
        """
        Removes nodes with zero quantity from the cart table.
        """
        for index in range(self.size):
            node = self.table[index]
            if node is not None and node.quantity == 0:
                self.table[index] = None

    def search_and_modify_quantity(self, name, other_object, quantity):
        """
        Searches for a product in the cart and modifies its quantity if found. Otherwise, inserts the product into the cart.
        
        Args:
            name (str): The name of the product.
            other_object (Carttable): The reference to the other cart table.
            quantity (int): The quantity of the product.
        """
        other_node = other_object.search(name)
        if other_node is not None:
            node = self.search(name)
            if node is not None:
                node.quantity = quantity
            else:
                self.insert(
                    other_node.name,
                    other_node.description,
                    other_node.price,
                    quantity,
                    other_node.image,
                    other_node.category
                )


def build_cart_from_csv(csv_file_path, hash_table):
    """
    Builds a cart table from a CSV file.
    
    Args:
        csv_file_path (str): The path of the CSV file.
        hash_table (Carttable): The cart table to build.
    """
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['name']
            description = row['description']
            price = float(row['price'])
            image = row['image']
            quantity = int(row['quantity'])
            category = row['category']
            hash_table.insert(name, description, price, quantity, image, category)


def build_csv_from_cart(cart, csv_file_path):
    """
    Builds a CSV file from a cart table.
    
    Args:
        cart (Carttable): The cart table.
        csv_file_path (str): The path of the CSV file to build.
    """
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["category", "name", "description", "price", "quantity", "image"])
        for item in cart.table:
            if item is not None:
                writer.writerow([item.category, item.name, item.description, item.price, item.quantity, item.image])


class Node:
    """
    Represents a node in a binary search tree.
    """
    def __init__(self, item):
        """
        Initializes a Node object.
        
        Args:
            item: The item to store in the node.
        """
        self.item = item
        self.left = None
        self.right = None


class BinarySearchTree:
    """
    Represents a binary search tree.
    """
    def __init__(self):
        """
        Initializes a BinarySearchTree object.
        """
        self.root = None

    def insert(self, node):
        """
        Inserts a node into the binary search tree.
        
        Args:
            node (Node): The node to insert.
        """
        if self.root is None:
            self.root = Node(node)
        else:
            self._insert_recursive(self.root, node)

    def _insert_recursive(self, current_node, node):
        """
        Recursively inserts a node into the binary search tree.
        
        Args:
            current_node (Node): The current node in the recursion.
            node (Node): The node to insert.
        """
        if node.price < current_node.item.price:
            if current_node.left is None:
                current_node.left = Node(node)
            else:
                self._insert_recursive(current_node.left, node)
        else:
            if current_node.right is None:
                current_node.right = Node(node)
            else:
                self._insert_recursive(current_node.right, node)

    def inorder_traversal(self):
        """
        Performs an inorder traversal of the binary search tree.
        
        Returns:
            list: A list of items in the inorder traversal order.
        """
        if self.root is None:
            return []

        result = []
        self._inorder_traversal_recursive(self.root, result)
        return result

    def _inorder_traversal_recursive(self, node, result):
        """
        Recursively performs an inorder traversal of the binary search tree.
        
        Args:
            node (Node): The current node in the recursion.
            result (list): The list to store the traversal result.
        """
        if node:
            self._inorder_traversal_recursive(node.left, result)
            result.append(node.item)
            self._inorder_traversal_recursive(node.right, result)

    def search(self, value):
        """
        Searches for a node in the binary search tree by its value.
        
        Args:
            value: The value to search for.
        
        Returns:
            Node: The matching node, or None if not found.
        """
        if self.root is None:
            return None

        return self._search_recursive(self.root, value)

    def _search_recursive(self, node, value):
        """
        Recursively searches for a node in the binary search tree by its value.
        
        Args:
            node (Node): The current node in the recursion.
            value: The value to search for.
        
        Returns:
            Node: The matching node, or None if not found.
        """
        if node is None or node.item.name == value:
            return node
        if value < node.item.name:
            return self._search_recursive(node.left, value)
        else:
            return self._search_recursive(node.right, value)

    def search_all_starts_with(self, prefix):
        """
        Searches for all nodes in the binary search tree whose values start with the given prefix.
        
        Args:
            prefix (str): The prefix to search for.
        
        Returns:
            list: A list of matching nodes.
        """
        result = []
        self._search_all_starts_with_recursive(self.root, prefix, result)
        return result

    def _search_all_starts_with_recursive(self, node, prefix, result):
        """
        Recursively searches for all nodes in the binary search tree whose values start with the given prefix.
        
        Args:
            node (Node): The current node in the recursion.
            prefix (str): The prefix to search for.
            result (list): The list to store the matching nodes.
        """
        if node:
            if node.item.name.startswith(prefix):
                result.append(node.item)
            if node.item.name >= prefix:
                self._search_all_starts_with_recursive(node.left, prefix, result)
            self._search_all_starts_with_recursive(node.right, prefix, result)


class orders:
    """
    Represents an order.
    """
    def __init__(self, order_num, customer, list_of_orders, time, total_amount, status):
        """
        Initializes an orders object.
        
        Args:
            order_num (int): The order number.
            customer (str): The customer name.
            list_of_orders (str): The list of ordered items.
            time (str): The order time.
            total_amount (float): The total amount of the order.
            status (str): The order status.
        """
        self.order_num = order_num
        self.customer = customer
        self.list_of_orders = list_of_orders
        self.total_amount = total_amount
        self.time = time
        self.status = status


class Customer:
    """
    Represents a customer.
    """
    def __init__(self, username, password, name, address1, address2, pincode, mobile):
        """
        Initializes a Customer object.
        
        Args:
            username (str): The username of the customer.
            password (str): The password of the customer.
            name (str): The name of the customer.
            address1 (str): The first address of the customer.
            address2 (str): The second address of the customer.
            pincode (str): The pincode of the customer.
            mobile (str): The mobile number of the customer.
        """
        self.username = username
        self.password = password
        self.name = name
        self.address1 = address1
        self.address2 = address2
        self.pincode = pincode
        self.mobile = mobile


class CusTable:
    """
    Represents a hash table for storing customers.
    """
    def __init__(self, size):
        """
        Initializes a CusTable object.
        
        Args:
            size (int): The size of the hash table.
        """
        self.size = size
        self.table = [None] * size

    def search_by_name(self, name):
        """
        Searches for a customer in the table by their name.
        
        Args:
            name (str): The name of the customer to search.
        
        Returns:
            Customer: The matching customer, or None if not found.
        """
        for customer in self.table:
            if customer is not None and customer.name == name:
                return customer
        return None

    def _hash_function1(self, key):
        """
        Performs the first hash function for the given key.
        
        Args:
            key (str): The key to hash.
        
        Returns:
            int: The hashed value.
        """
        total = 0
        if key is not None:  # Check if key is not empty
            for char in key:
                total += ord(char)
        return total % self.size

    def _hash_function2(self, key):
        """
        Performs the second hash function for the given key.
        
        Args:
            key (str): The key to hash.
        
        Returns:
            int: The hashed value.
        """
        total = 0
        for char in key:
            total += ord(char)
        return (total % (self.size - 1)) + 1

    def _hash(self, key, attempt):
        """
        Performs the hashing operation for the given key and attempt.
        
        Args:
            key (str): The key to hash.
            attempt (int): The current attempt count.
        
        Returns:
            int: The hashed index value.
        """
        return (self._hash_function1(key) + attempt * self._hash_function2(key)) % self.size

    def insert(self, customer):
        """
        Inserts a customer into the hash table.
        
        Args:
            customer (Customer): The customer to insert.
        """
        attempt = 0
        index = self._hash(customer.username, attempt)
        while self.table[index] is not None:
            attempt += 1
            index = self._hash(customer.username, attempt)
        self.table[index] = customer

    def search(self, name):
        """
        Searches for a customer in the hash table by their name.
        
        Args:
            name (str): The name of the customer to search.
        
        Returns:
            Customer: The matching customer, or None if not found.
        """
        attempt = 0
        index = self._hash(name, attempt)
        while self.table[index] is not None:
            if self.table[index].username == name:
                return self.table[index]
            attempt += 1
            index = self._hash(name, attempt)
        return None

    def get_node_addresses(self):
        """
        Retrieves the addresses of nodes in the hash table.
        
        Returns:
            list: A list of node addresses.
        """
        addresses = []
        for node in self.table:
            if node is not None:
                addresses.append(node)
        return addresses

    def modify_customer(self, username, new_name, new_mobile, new_pincode, new_address1, new_address2):
        """
        Modifies a customer's information in the hash table.
        
        Args:
            username (str): The username of the customer to modify.
            new_name (str): The new name of the customer.
            new_mobile (str): The new mobile number of the customer.
            new_pincode (str): The new pincode of the customer.
            new_address1 (str): The new first address of the customer.
            new_address2 (str): The new second address of the customer.
        """
        customer = self.search(username)
        if customer is not None:
            customer.name = new_name
            customer.mobile = new_mobile
            customer.pincode = new_pincode
            customer.address1 = new_address1
            customer.address2 = new_address2


def build_customer_from_csv(csv_file_path, hash_table):
    """
    Builds a customer hash table from a CSV file.
    
    Args:
        csv_file_path (str): The path of the CSV file.
        hash_table (CusTable): The customer hash table to build.
    """
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            username = row['username']
            password = row['password']
            name = row['name']
            address1 = row['address1']
            address2 = row['address2']
            pincode = row['pincode']
            mobile = row['mobile']
            customer = Customer(username, password, name, address1, address2, pincode, mobile)
            hash_table.insert(customer)


def build_csv_from_customer(hash_table, csv_file_path):
    """
    Builds a CSV file from a customer hash table.
    
    Args:
        hash_table (CusTable): The customer hash table.
        csv_file_path (str): The path of the CSV file to build.
    """
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["username", "password", "name", "address1", "address2", "pincode", "mobile"])
        for customer in hash_table.table:
            if customer is not None:
                writer.writerow([customer.username, customer.password, customer.name, customer.address1,
                                 customer.address2, customer.pincode, customer.mobile])



def send_email(sender_email, sender_password, receiver_email, subject, message):
    """
    Sends an email using the provided SMTP server.
    
    Args:
        sender_email (str): The sender's email address.
        sender_password (str): The sender's email password.
        receiver_email (str): The receiver's email address.
        subject (str): The subject of the email.
        message (str): The message body of the email.
    """
    message_obj = MIMEMultipart()
    message_obj["From"] = sender_email
    message_obj["To"] = receiver_email
    message_obj["Subject"] = subject

    message_obj.attach(MIMEText(message, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message_obj.as_string())


def generate_email_message(order_no, customer, address, list_of_orders, total_amount, status):
    """
    Generates an email message for an order.
    
    Args:
        order_no (int): The order number.
        customer (str): The customer name.
        address (str): The customer address.
        list_of_orders (str): The list of ordered items.
        total_amount (float): The total amount of the order.
        status (str): The order status.
    
    Returns:
        str: The generated email message.
    """
    message = f"Order No: {order_no}\n\n"
    message += f"Customer: {customer}\n\n"
    message += f"Customer Address: {address}\n\n"

    message += "Ordered Items:\n"

    ordered_items = eval(list_of_orders)

    for item in ordered_items:
        product = item[0]
        quantity = item[1]
        message += f"- {product}: {quantity}\n"

    message += f"\nTotal Amount: {total_amount}\n"
    message += f"Status: {status}\n"

    return message

