import sqlite3
from datetime import datetime, timedelta

from faker import Faker
import random
import os

# Initialize Faker for Hebrew
faker = Faker('he_IL')
Faker.seed(0)  # Ensure reproducibility

# Database file path
db_file_path = 'C:\\sqlite\\db\\shipping_company.db'


def create_database(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create tables
    # Customers
    c.execute('''CREATE TABLE IF NOT EXISTS customers
                 (id INTEGER PRIMARY KEY, name TEXT, contact_info TEXT, address TEXT)''')
    # Orders
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY, customer_id INTEGER, product TEXT, 
                 status TEXT, order_date TEXT, expected_delivery TEXT,
                 FOREIGN KEY(customer_id) REFERENCES customers(id))''')
    # Order Status Logs
    c.execute('''CREATE TABLE IF NOT EXISTS order_status_logs
                 (id INTEGER PRIMARY KEY, order_id INTEGER, status TEXT, change_date TEXT,
                 FOREIGN KEY(order_id) REFERENCES orders(id))''')
    # Customer Communication Logs
    c.execute('''CREATE TABLE IF NOT EXISTS customer_communication_logs
                 (id INTEGER PRIMARY KEY, customer_id INTEGER, communication_date TEXT, notes TEXT,
                 FOREIGN KEY(customer_id) REFERENCES customers(id))''')
    # Drivers
    c.execute('''CREATE TABLE IF NOT EXISTS drivers
                 (id INTEGER PRIMARY KEY, name TEXT, contact_info TEXT)''')
    # Order Delivery Details
    c.execute('''CREATE TABLE IF NOT EXISTS order_delivery_details
                 (order_id INTEGER PRIMARY KEY, delivery_date TEXT, driver_id INTEGER,
                 FOREIGN KEY(order_id) REFERENCES orders(id),
                 FOREIGN KEY(driver_id) REFERENCES drivers(id))''')

    conn.commit()
    return conn


def generate_dates():
    order_date = faker.date_this_year().isoformat()
    # Add a random number of days to the order date for the expected delivery to ensure it's always after the order date
    order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
    expected_delivery = order_date + timedelta(days=random.randint(1, 60))
    return order_date, expected_delivery


def generate_data(conn):
    c = conn.cursor()

    # Generate Customers
    for i in range(100):
        c.execute("INSERT INTO customers (name, contact_info, address) VALUES (?, ?, ?)",
                  (faker.name(), faker.phone_number(), faker.address()))

    # Generate Drivers
    for i in range(10):  # Assuming 10 drivers
        c.execute("INSERT INTO drivers (name, contact_info) VALUES (?, ?)",
                  (faker.name(), faker.phone_number()))

    customers = [i for i in range(1, 101)]
    drivers = [i for i in range(1, 11)]
    statuses = ['הוזמן', 'בטיפול', 'נשלח לספק', 'בדרך', 'נמסר']
    products = ['מקרר', 'מכונת כביסה', 'טלוויזיה', 'מדיח כלים', 'תנור חשמלי']

    # Generate Orders and Logs
    for i in range(300):
        customer_id = random.choice(customers)
        driver_id = random.choice(drivers)
        product = random.choice(products)
        order_date, expected_delivery = generate_dates()
        c.execute(
            "INSERT INTO orders (customer_id, product, status, order_date, expected_delivery) VALUES (?, ?, ?, ?, ?)",
            (customer_id, product, statuses[0], order_date, expected_delivery))
        order_id = c.lastrowid

        # Insert a random log for each status change
        for status in random.sample(statuses, random.randint(1, len(statuses))):
            c.execute("INSERT INTO order_status_logs (order_id, status, change_date) VALUES (?, ?, ?)",
                      (order_id, status,
                       faker.date_between_dates(date_start=order_date, date_end=expected_delivery).isoformat()))

        # Generate Customer Communication Logs randomly
        if random.choice([True, False]):
            c.execute(
                "INSERT INTO customer_communication_logs (customer_id, communication_date, notes) VALUES (?, ?, ?)",
                (customer_id, faker.date_between_dates(date_start=order_date, date_end=expected_delivery).isoformat(),
                 faker.sentence()))

        # Insert delivery details
        c.execute("INSERT INTO order_delivery_details (order_id, delivery_date, driver_id) VALUES (?, ?, ?)",
                  (order_id, expected_delivery, driver_id))

    conn.commit()


def main(db_path):
    conn = create_database(db_path)
    generate_data(conn)
    conn.close()


main(db_file_path)

