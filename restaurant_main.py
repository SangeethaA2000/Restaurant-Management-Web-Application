import sqlite3
from flask import Flask, render_template,request,redirect, url_for, session
from datetime import datetime
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key='sangeetha@2000'

@app.route('/')
def home():
    return render_template('landing.html')  # ✅ This line must be returned

@app.route('/add-customer',methods=['GET','POST'])
def add_customer():
    if request.method=='POST':
        name=request.form['name']
        phone=request.form['phone']
        email=request.form['email']

        try:
            conn=sqlite3.connect('restaurant_data.db')
            cursor=conn.cursor()

            cursor.execute("insert into customers (name, phone, email) values (?,?,?)",(name, phone, email))
            conn.commit()
            conn.close()

            return "<h3> Customer added successfully! </h3> <a href='/'> Back to Home </a>"

        except sqlite3.IntegrityError:    #duplicate email error
            return "<h3 style='color:red;'> Error: Email already exists! </h3><a href='/add-customer'> Try again </a>"
 
        except Exception as e:
            return f"<h3 style='color:red;'> Unexpected Error: {e} </h3>"

    return render_template('add_customer.html')  

@app.route('/menu')
def menu():
    conn=sqlite3.connect("restaurant_data.db")
    cursor=conn.cursor()

    cursor.execute("select * from menu")
    items=cursor.fetchall()

    conn.close()

    return render_template('menu.html',menu_items=items)  

@app.route('/order', methods=['GET','POST'])
def order():

    conn=sqlite3.connect('restaurant_data.db')
    cursor=conn.cursor()

    cursor.execute("select cus_id, name from customers")
    customers=cursor.fetchall()

    cursor.execute("select tab_id, capacity from tables where is_available=1")
    tables= cursor.fetchall()
    
    cursor.execute("select item_id, item_name from menu")
    items=cursor.fetchall()

    if request.method=='POST':
        customer_id=request.form['customer_id']
        table_id=request.form['table_id']
        item_id=request.form['item_id']
        quantity=request.form['quantity']
        spice_level=request.form['spice_level']
        sweetness=request.form['sweetness']
        texture=request.form['texture']

        order_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        try:
            cursor.execute("""insert into orders (customer_id, table_id, item_id, quantity, spice_level, sweetness, texture, status, order_time)
            values (?,?,?,?,?,?,?,?,?)""",(customer_id, table_id, item_id, quantity, spice_level, sweetness, texture,'Pending',order_time))

            # mark table as unavailable

            cursor.execute("update tables set is_available=0 where tab_id=?",(table_id,))
            conn.commit()
            message="order placed successfully"

        except Exception as e:
            conn.rollback()
            message=f"failed to place order: {e}"

        finally:
            conn.close()

        return f"<h3> {message} </h3> <br> <a href='/'> Back to Home </a>"

    conn.close()

    return render_template('order.html',customers=customers, tables=tables, items=items)  

@app.route('/view_orders',methods=['GET','POST'])
def view_orders():
    conn=sqlite3.connect('restaurant_data.db')
    cursor=conn.cursor()

    selected_status= request.form.get('status_filter','All')

    if selected_status == "All":


        cursor.execute("""select o.order_id, c.name, m.item_name, o.quantity, o.spice_level, o.sweetness, o.texture, t.tab_id, o.status, o.order_time
        from orders o
        join customers c on o.customer_id=c.cus_id
        join menu m on o.item_id=m.item_id
        join tables t on o.table_id=t.tab_id
        order by o.order_time desc""")

    else:
        cursor.execute("""select o.order_id, c.name, m.item_name, o.quantity, o.spice_level, o.sweetness, o.texture, t.tab_id, o.status, o.order_time
        from orders o
        join customers c on o.customer_id=c.cus_id
        join menu m on o.item_id=m.item_id
        join tables t on o.table_id=t.tab_id
        where o.status=? order by o.order_time desc""",(selected_status,))

    
    orders=cursor.fetchall()
    conn.close()
    

    return render_template('view_orders.html',orders=orders,selected_status=selected_status) 


@app.route('/add-table', methods=['GET','POST'])
def add_table():
    if request.method=='POST':
        try:
            capacity=int(request.form['capacity'])
            if capacity<=0:
                return "<h3 style='color:red;'> Capacity must be greater than 0. </h3> <a href='/add-table'> Try again </a>"

                conn=sqlite3.connect('restaurant_data.db')
                cursor= conn.cursor()
                cursor.execute("insert into tables (capacity) values (?)", (capacity,))
                conn.commit()
                conn.close()

            
            return "<h3> Table added successfully ! </h3> <a href='/'>Back to Home </a>"

        except ValueError:
            return "<h3 style='color:red;'>Please enter a valid number.</h3> <a href='/add-table'> Try Again </a>"

        except Exception as e:
            return f"<h3 style='color:red;'>Unexpected Error: {e} </h3>"

    return render_template('add_table.html')



@app.route('/tables_status')
def tables_status():
    conn=sqlite3.connect('restaurant_data.db')
    cursor=conn.cursor()
    cursor.execute("select tab_id,is_available from tables")
    tables=cursor.fetchall()
    conn.close()
    return render_template('tables_status.html',tables=tables)



@app.route('/order_summary')
def order_summary():
    conn=sqlite3.connect("restaurant_data.db")
    cursor=conn.cursor()

    # count of orders by status

    cursor.execute("select status, count(*) from orders group by status")
    status_summary=cursor.fetchall()

    #total no. of orders today
    cursor.execute("select count(*) from orders where DATE(order_time) = DATE('now')")
    today_count=cursor.fetchone()[0]
    conn.close()

    return render_template("summary.html",status_summary=status_summary, today_count=today_count)

@app.route('/update_status', methods=['POST'])
def update_status():
    order_id = request.form['order_id']
    new_status = request.form['new_status']

    conn = sqlite3.connect('restaurant_data.db')
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE orders SET status=? WHERE order_id=?", (new_status, order_id))

        # If order is served, make table available again
        if new_status == "Served":
            cursor.execute("SELECT table_id FROM orders WHERE order_id=?", (order_id,))
            table_id = cursor.fetchone()[0]
            cursor.execute("UPDATE tables SET is_available=1 WHERE tab_id=?", (table_id,))

        conn.commit()

    except Exception as e:
        conn.rollback()
        return f"<h3>Failed to update status: {e}</h3>"

    finally:
        conn.close()

    return redirect('/view_orders')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        conn = sqlite3.connect('restaurant_data.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                           (username, email, password, role))
            conn.commit()
        except Exception as e:
            conn.close()
            return f"<h3 style='color:red;'>Error: {e}</h3><a href='/register'>Try Again</a>"

        conn.close()
        return redirect('/login?role=' + role)
    
    role = request.args.get('role', '')
    return render_template('register.html', role=role)


@app.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role', 'customer')  # Default role

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('restaurant_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND role=?", (email, role))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):  # Assuming password hash is at index 3
            session['user_id'] = user[0]  # Assuming user ID is at index 0
            session['role'] = role

            return redirect('/dashboard')  # Redirect based on role
        else:
            return f"<h3 style='color:red;'>Invalid credentials or role!</h3><a href='/login?role={role}'> Try Again </a>"

    return render_template('login.html', role=role)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    role = session['role']

    if role == 'owner':
        return redirect('/owner_home')
    elif role == 'chef':
        return redirect('/chef_home')
    elif role == 'customer':
        return redirect('/customer_home')
    else:
        return "Unknown role."


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/owner_home')
def owner_home():
    if 'user_id' not in session or session.get('role') != 'owner':
        return redirect('/login')
    return render_template('owner_home.html')


@app.route('/chef_home')
def chef_home():
    if 'user_id' not in session or session.get('role') != 'chef':
        return redirect('/login')
    return render_template('chef_home.html')


@app.route('/customer_home')
def customer_home():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect('/login')
    return render_template('customer_home.html')

# --- Menu Pages ---

@app.route('/menu/starters')
def show_starters():
    return render_template('starters.html')

@app.route('/menu/tiffin')
def show_tiffin():
    return render_template('tiffin.html')

@app.route('/menu/maincourse')
def show_maincourse():
    return render_template('maincourse.html')

@app.route('/menu/dessert')
def show_dessert():
    return render_template('dessert.html')

# --- Cart Functionality ---

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item = request.form['item']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({'item': item, 'price': price, 'quantity': quantity})
    session.modified = True
    return redirect(request.referrer)

@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('view_cart'))

# --- Home or Main Menu Page (optional) ---

@app.route('/')
def show_menu():
    return render_template('menu.html')  # Assuming you have a main menu.html


if __name__ == '__main__':
    app.run(debug=True,port=8000)