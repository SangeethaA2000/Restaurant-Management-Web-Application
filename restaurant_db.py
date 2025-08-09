#import necessary libraries

import sqlite3                    #used to connect and interact with sqlite database
from datetime import datetime     #to get current time

conn=sqlite3.connect("restaurant_data.db")   #create or connect to sql database - if db not there it creates, 
                                                                           # if already available it connects

cursor=conn.cursor()                 #cursor object to execute sql commands

#---- optional to clean if already below table exists ----

cursor.execute("drop table if exists orders")
cursor.execute("drop table if exists customers")
cursor.execute("drop table if exists menu")
cursor.execute("drop table if exists tables")


#----create customer table to store customer details----

cursor.execute("""create table if not exists customers
                (cus_id integer primary key autoincrement,  
                 name text not null,
                 phone text,            
                 email text unique)""")    

# cus_id - PK - unique ID for each customer
# email - must be unique for all customer
# phone -will be in numbers bt considered as text / string

#------create tables - which will be in restaurant - not db table --

cursor.execute("""create table if not exists tables
                (tab_id integer primary key autoincrement,
                capacity integer,
                is_available int default 1)""")

# is_available -- default 1 -- means --- 1 = available , 0 = booked ---

#----menu table to store food items -----

cursor.execute("""create table if not exists menu
                (item_id integer primary key autoincrement,
                 item_name text not null,
                 category text,
                 price real not null)""")

# item_id - PK - unique id for each dish
# item_name - dish name
#category - like starter , main course, sweet etc
# price - real - can be whole or decimal values also bt should not be null

#------ orders table to store order history------------

cursor.execute("""create table if not exists orders
                (order_id integer primary key autoincrement,
                 
                 customer_id int not null references customers(cus_id),
                 
                 table_id int references tables(tab_id),
                 
                 item_id int references menu(item_id),
                 
                 quantity int,
                 spice_level text,
                 sweetness text,
                 texture text,
                 status text default 'pending')""")

# FK - foreign key -- link one table to other -- have to give references in same line
# else --- seperately give like -- foreign key(customer_id) references customers(cus_id)

# status -- to show whether order pending or completed


#---- save changes to db

conn.commit()

print("All tables created successfully")


def add_customer():

    try:

        name=input("enter customer name:").strip()
        phone=input("enter phone number:").strip()
        email=input("enter email address:").strip()

        if not name:
            print("name cannot be empty")
            return

    #check if email already exists

        cursor.execute("select * from customers where email=?",(email,))
        
        if cursor.fetchone():
            print("email already exists, try another")
            return

    #insert values to database

        cursor.execute("""insert into customers(name, phone, email) values(?,?,?)""",(name,phone, email))

        conn.commit()
        print(f"customer {name} added successfully")

    except Exception as e:
        print("error while adding customer",e)

add_customer()


def view_customers():
    cursor.execute("select * from customers")
    rows=cursor.fetchall()

    print("\n customer list:")
    print("ID | NAME | PHONE | EMAIL ")

    for row in rows:
        print(row)

view_customers()


#function to add new table

def add_table():
    try:
        cap=int(input("enter seating capacity for table:"))

        if cap<=0:
            print("capacity must be greater than 0")
            return

        cursor.execute("insert into tables (capacity) values (?)", (cap,))

        conn.commit()

        print(f"table with capacity {cap} added successfully")

    except ValueError:
        print("please enter a valid number")

    except Exception as e:
        print("error while adding table:",e)

add_table()
        

#view all tables

def view_tables():

    cursor.execute("select * from tables")
    tables=cursor.fetchall()

    print("\n Table List:")
    print("Table ID | Capacity | Available (1 = YES, 0 = No)")

    for t in tables:
        table_id, capacity, is_available=t

        if is_available==1:
           
            status="YES"
            
        else: 
            status="NO"


    print(f"{table_id} | {capacity} | {status}")



view_tables()

#update table availability

def update_table_status():
    #available -1, unavailable -0

    table_id=int(input("enter table ID to update:"))
    new_status=int(input("enter new status (1=Available, 0=Booked)"))

    cursor.execute("update tables set is_available=? where tab_id=?",(new_status, table_id))

    conn.commit()

    print(f"table {table_id} status updated to {'Available' if new_status else 'Booked'}")

update_table_status()

def add_order_time_column():
    conn = sqlite3.connect('restaurant_data.db')
    cursor = conn.cursor()

    # Check if 'order_time' column already exists
    cursor.execute("PRAGMA table_info(orders)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'order_time' not in columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN order_time TEXT")
        conn.commit()
        print("✅ 'order_time' column added to orders table.")
    else:
        print("ℹ️ 'order_time' column already exists.")

    conn.close()

add_order_time_column()

def create_users_table():
    conn = sqlite3.connect('restaurant_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('owner', 'chef', 'customer')) NOT NULL
    )''')
    
    conn.commit()
    conn.close()
    print("✅ Users table created or already exists.")

create_users_table()


#to avoid error give correct column name from tables

# to check column names

cursor.execute("PRAGMA table_info(customers)")  #PRAGMA - sqlite keyword - command used to modify 
print("customer table:")
for customers in cursor.fetchall():
    print(customers)
    
cursor.execute("PRAGMA table_info(tables)")
print("tables table:")
for tables in cursor.fetchall():
    print(tables)
    
cursor.execute("PRAGMA table_info(menus)")
print("menus table:")
for menus in cursor.fetchall():
    print(menus)
    
cursor.execute("PRAGMA table_info(orders)")
print("orders table:")
for orders in cursor.fetchall():
    print(orders)




#below is just for testing == > in orders table should get pending - it worked

# def add_status_column_if_not_exists():
#     conn=sqlite3.connect('restaurant_data.db')
#     cursor=conn.cursor()

#     try:
#         cursor.execute("select status from orders limit 1")
        
#     except sqlite3.OperationalError:
#         cursor.execute("alter table orders add column status text default 'Pending'")
#         conn.commit()
#         print("status column added to orders table")
#     conn.close()

# add_status_column_if_not_exists()
    