from flask import Flask, flash,render_template, request, redirect, url_for, session,jsonify
from datetime import datetime
import mysql.connector
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace 'your_secret_key_here' with your actual secret key
bcrypt = Bcrypt(app)


@app.route('/total_sales_shampoo_last_7_days')
def total_sales_shampoo_last_7_days():
    try:
        # Calculate the date 7 days ago
        seven_days_ago = datetime.now() - timedelta(days=7)
        seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%d')

        db = get_db_connection()
        cursor = db.cursor()

        # Execute SQL query to find total sales amount of "shampoo" in the last 7 days
        sql = "SELECT SUM(rate) FROM purchase WHERE item = 't-shirt' AND date_of_purchase >= %s"
        cursor.execute(sql, (seven_days_ago_str,))
        total_sales = cursor.fetchone()[0]  # Fetch the total sales amount

        cursor.close()
        db.close()

        return jsonify({"total_t_shirt_last_7_days": total_sales})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/date')
def dateshow():
    return render_template('date.html')
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password='12345',
        database='flask'
    )

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

@app.route('/')
def home():
    return render_template('nav.html')

@app.route('/log')
def eh():
    return render_template('login.html')
@app.route('/usersignup')
def usersignup():
    return render_template('signup.html')

@app.route('/adminsignup')
def adminsignup():
    return render_template('admin.html')


@app.route('/addproduct', methods=['POST', 'GET'])
def add():
    if request.method == "POST":
        productname = request.form['product_name']
        rate = request.form['rate']
        stock = request.form['stock']
        
        db = get_db_connection()
        cursor = db.cursor()
        try:
            sql = "INSERT INTO PRODUCTS (PRODUCT_NAME, RATE, STOCK) VALUES (%s, %s, %s)"
            val = (productname, rate, stock)
            cursor.execute(sql, val)
            db.commit()
        finally:
            cursor.close()
            db.close()
        
        return "Added successfully"

@app.route('/signup', methods=["POST"])
def signups():
    if request.method == "POST":
        firstname = request.form["first-name"]
        lastname = request.form["last-name"]
        age = request.form["age"]
        sex = request.form["sex"]
        contactnumber = request.form["contact-number"]
        email = request.form["email-id"]
        password = request.form["password"]
        hashed_password = hash_password(password)

        db = get_db_connection()
        cursor = db.cursor()
        try:
            sql = 'INSERT INTO USER_DETAILS (FIRST_NAME, LAST_NAME, AGE, SEX, CONTACT_NUMBER, EMAIL_ID, PASSWORD) VALUES (%s, %s, %s, %s, %s, %s, %s)'
            val = (firstname, lastname, age, sex, contactnumber, email, hashed_password)
            cursor.execute(sql, val)
            db.commit()
        finally:
            cursor.close()
            db.close()
        return render_template("login.html")

@app.route('/order', methods=["POST"])
def alter():
    if request.method == "POST":
        product_name = request.form['product_name']  # Correct variable name
        quantity = request.form['quantity']
        rate=request.form['rate']
        db = get_db_connection()
        cursor = db.cursor()
        purchase_date = datetime.now()
        user_id = session.get('user_id')
        amount=int(quantity)*float(rate)
        try:
            cursor.execute("UPDATE products SET stock = stock - %s WHERE product_name = %s;", (quantity, product_name))
            cursor.execute("INSERT INTO purchase (user_id, item, quantity,rate,date_of_purchase) VALUES (%s, %s, %s, %s,%s);", (user_id, product_name, quantity,amount, purchase_date))
            db.commit()  # Remember to commit the changes
        except Exception as e:
            print(f"Error: {e}")
            db.rollback()  # Rollback changes if an error occurs
        finally:
            cursor.close()
            db.close()
        return render_template('demo.html') # Corrected spelling of "success"
@app.route('/admin', methods=["POST"])
def signup():
    if request.method == "POST":
        passcodes='12345'
        if request.form['company-passcode']==passcodes:
            firstname = request.form["first-name"]
            lastname = request.form["last-name"]
            age = request.form["age"]
            sex = request.form["sex"]
            contactnumber = request.form["contact-number"]
            email = request.form["email-id"]
            password = request.form["password"]
            designation = request.form["designation"]  # Added this line
            hashed_password = hash_password(password)

            db = get_db_connection()
            cursor = db.cursor()
            try:
                sql = 'INSERT INTO store_user (FIRST_NAME, LAST_NAME, AGE, SEX, CONTACT_NUMBER, EMAIL_ID, PASSWORD, DESIGNATION) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'  # Updated SQL query
                val = (firstname, lastname, age, sex, contactnumber, email, hashed_password, designation)  # Updated val
                cursor.execute(sql, val)
                db.commit()
            finally:
                cursor.close()
                db.close()
        
            return render_template("login.html")
@app.route('/up')
def up():
    return render_template('update.html')

@app.route('/update', methods=["PUT", "POST"])
def update_item_rate():
    try:
        # Access form data
        name = request.form['itemId']  # Assuming the form field for item ID is named 'itemId'
        new_rate = request.form['newRate']

        # Convert new rate to float
        new_rate_float = float(new_rate)

        # Validate input parameters
        if name is None or new_rate is None:
            return jsonify({"error": "Missing item ID or new rate parameter"}), 400

        # Update item rate in the database
        db = get_db_connection()
        cursor = db.cursor()
        sql = "UPDATE products SET rate = %s WHERE product_name = %s"
        cursor.execute(sql, (new_rate_float, name))
        db.commit()
        cursor.close()
        db.close()

        return jsonify({"message": "Item rate updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500





@app.route('/index')
def show():
    db = get_db_connection()
    cursor = db.cursor()
    products = []
    try:
        cursor.execute("SELECT product_id, product_name, rate, stock FROM products")
        products = cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        db.close()

    return render_template('productshow.html', products=products)

@app.route('/login', methods=["POST"])
def login():

    if request.method == "POST":
        role = request.form['role']
        if role == 'Manager':
            email = request.form['email-id']
            password = request.form['password']
            
            db = get_db_connection()
            cursor = db.cursor()
            try:
                cursor.execute("SELECT PASSWORD FROM store_user WHERE EMAIL_ID = %s", (email,))
                user = cursor.fetchone()
                
                # This ensures that we handle any remaining unread results
                while cursor.nextset():
                    pass
                
                if user:
                    is_valid = bcrypt.check_password_hash(user[0], password)
                    if is_valid:
                        return render_template("cart.html")
                    else:
                        return "Invalid Password"
                else:
                    return "User not found"
            finally:
                cursor.close()
                db.close()
           
        else:
            email = request.form['email-id']
            password = request.form['password']
            
            db = get_db_connection()
            cursor = db.cursor()
            try:
                cursor.execute("SELECT PASSWORD, USER_ID FROM USER_DETAILS WHERE EMAIL_ID = %s", (email,))
                user = cursor.fetchone()
                
                # This ensures that we handle any remaining unread results
                while cursor.nextset():
                    pass
                
                if user:
                    is_valid = bcrypt.check_password_hash(user[0], password)
                    if is_valid:
                        session['user_id'] = user[1]  # Store the user's ID in the session
                        return redirect(url_for('show'))
                    else:
                        return "Invalid Password"
                else:
                    return "User not found"
            finally:
                cursor.close()
                db.close()
@app.route('/datedata', methods=["GET", "POST"])
def date():
    if request.method == "POST":
        start = request.form['start_date']
        end = request.form['end_date']
        db = get_db_connection()
        cursor = db.cursor()
        products = []
        try:
            sql = "SELECT item, COUNT(*) as total_purchases FROM purchase WHERE date_of_purchase BETWEEN %s AND %s GROUP BY item"
            val = (start, end)
            cursor.execute(sql, val)
            products = cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            db.close()

        return jsonify(products)
    else:
        return jsonify({"error": "Method not allowed"}), 405

@app.route('/addsproduct')
def addproduct():
    return render_template('product.html')

if __name__ == "__main__":
    app.run(debug=True)
