from flask import Flask,  flash, render_template, request, redirect, url_for, session
from flaskext.mysql import MySQL
import pymysql
from datetime import date

app = Flask(__name__)
app.secret_key = "pizzaapp-coder"

mysql = MySQL()

#MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'nFNkHt1vzc'
app.config['MYSQL_DATABASE_PASSWORD'] = 'xjZMqDNM1F'
app.config['MYSQL_DATABASE_DB'] = 'nFNkHt1vzc'
app.config['MYSQL_DATABASE_HOST'] = 'remotemysql.com'
mysql.init_app(app)


@app.route('/cart', methods=['POST','GET'])
def go_to_shopping_cart():
    try:
        return render_template('cart.html')
    except Exception as e:
        print(e)

@app.route('/quantity',methods=['POST','GET'])
def change_quantity():
    try:
        _quantity = int(request.form['quantity'])
        _code = request.form['code']
        print(_quantity)
        print(_code)


        if _quantity and _code and request.method == 'POST':
            print("here")
            all_total_price = 0
            all_total_quantity = 0
            session.modified = True
            for item in session['cart_item'].items():
                print("inside for ")
                if item[0] ==_code:
                    print("find item")
                    individual_quantity = session['cart_item'][_code]['quantity']
                    session['cart_item'][_code]['quantity']= _quantity
                    session['cart_item'][_code]['total_price'] = _quantity * session['cart_item'][_code]['price']
                    session['cart_item'][_code]['total_price_dollar'] = round(_quantity * session['cart_item'][_code]['price'] * 1.13, 2)
                    all_total_quantity =  session['all_total_quantity']+ _quantity - individual_quantity
                    all_total_price = session['all_total_price'] + session['cart_item'][_code]['price'] * (_quantity - individual_quantity)

                    session['all_total_quantity'] = all_total_quantity
                    session['all_total_price'] = all_total_price
                    break
            print("redirecting")
            return redirect(request.referrer)
        else:
            return 'Error while updating the quantity of item in cart'

    except Exception as e:
        print(e)



@app.route('/checkout', methods=['GET'])
def checkout():
    try:
        return render_template('checkout.html')
    except Exception as e:
        print(e)


@app.route('/save',methods=['POST','GET'])
def save_checkout():
    try:
        print("it's here")
        _fname = request.form['firstname']
        _lname = request.form['lastname']
        _email = request.form['email']
        _address = request.form['address']
        _city = request.form['city']
        _country = request.form['country']
        _zip = request.form['zip']
        print(_fname)
        print("it came here")
        if _fname and _lname and _email and _address and _country and _city and request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            sqlQuery = "SELECT * FROM customers WHERE fname='" + _fname + "' AND lname='" +_lname +"' AND email='"+ _email +"';"
            cursor.execute(sqlQuery)

            row = cursor.fetchone()
            print(row)
            if row == None:
                print("empty")
                # Insert Customer into Database
                if _zip == "":
                    sqlInsert = "INSERT INTO customers(fname,lname,email,address,city,country) VALUES('"+_fname+"','"+ _lname +"','"+_email+"','"+_address+"','"+_city +"','"+_country +"');"
                else:
                    sqlInsert = "INSERT INTO customers(fname,lname,email,address,city,country,zip) VALUES('" + _fname + "','" + _lname + "','" + _email + "','" + _address + "','" + _city + "','" + _country +"',"+ _zip+");"
                cursor.execute(sqlInsert)
                cursor.execute(sqlQuery)
                row = cursor.fetchone()
                print(row)
            today = date.today()
            print("adding order")
            sqlInsert = "INSERT INTO nFNkHt1vzc.Order(customer_id,order_date,shipping_price) VALUES(" +str(row['id'])+",'"+str(today)+"',7.0);"
            cursor.execute(sqlInsert)

            print("find order id")
            sqlQuery ="SELECT id FROM nFNkHt1vzc.Order WHERE customer_id=" + str(row['id']) + " AND order_date='" +str(today )+"';"
            cursor.execute(sqlQuery)
            orderId = cursor.fetchone()
            print(orderId)
            print("add order items")
            for key, value in session['cart_item'].items():
                print(key)
                sqlInsert ="INSERT INTO nFNkHt1vzc.OrderItem(Order_ID,Product_ID,Quantity)  VALUES(" +str(orderId['id']) +","+str(session['cart_item'][key]['pid'])+","+str(session['cart_item'][key]['quantity'])+");"
                cursor.execute(sqlInsert)

            session.clear()
            return render_template('cart.html', response="Your order has been received.")
        else:
            print("empty")
            flash('You must fill in all the required(*) fields.')
            return redirect(url_for('.checkout'))


    except Exception as e:
        print(e)
    finally:
        conn.commit()
        cursor.close()
        conn.close()

@app.route('/add', methods=['POST','GET'])
def add_product_to_cart():
    cursor = None
    try:
        _quantity = int(request.form['quantity'])
        _code = request.form['code']
        # validate the received values
        if _quantity and _code and request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM product WHERE code=%s", _code)
            row = cursor.fetchone()

            itemArray = {
                row['code']: {'name': row['name'], 'code': row['code'],  'pid': row['pid'], 'quantity': _quantity, 'price': row['price'],
                              'image': row['image'], 'total_price': _quantity * row['price'], 'total_price_dollar': round(_quantity * row['price'] * 1.13,2)}}
            print(itemArray)

            all_total_price = 0
            all_total_quantity = 0

            session.modified = True
            if 'cart_item' in session:
                if row['code'] in session['cart_item']:
                    for key, value in session['cart_item'].items():
                        if row['code'] == key:
                            old_quantity = session['cart_item'][key]['quantity']
                            total_quantity = int(old_quantity )+ _quantity
                            session['cart_item'][key]['quantity'] = total_quantity
                            session['cart_item'][key]['total_price'] = total_quantity * row['price']
                            session['cart_item'][key]['total_price_dollar'] = round(total_quantity * row['price'] *1.13, 2)
                else:
                    session['cart_item'] = array_merge(session['cart_item'], itemArray)

                for key, value in session['cart_item'].items():
                    individual_quantity = int(session['cart_item'][key]['quantity'])
                    individual_price = float(session['cart_item'][key]['total_price'])
                    all_total_quantity = all_total_quantity + individual_quantity
                    all_total_price = all_total_price + individual_price
            else:
                session['cart_item'] = itemArray
                all_total_quantity = all_total_quantity + _quantity
                all_total_price = all_total_price + _quantity * row['price']

            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

            return redirect(request.referrer)
        else:
            return 'Error while adding item to cart'
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
@app.route("/")
def products():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM  nFNkHt1vzc.product")
        rows = cursor.fetchall()
        return render_template('app.html', products = rows)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()



###????
@app.route('/empty')
def empty_cart():
    try:
        session.clear()
        return redirect(url_for('.products'))
    except Exception as e:
        print(e)


@app.route('/delete/<string:code>')
def delete_product(code):
    try:
        all_total_price = 0
        all_total_quantity = 0
        session.modified = True

        for item in session['cart_item'].items():
            if item[0] == code:
                session['cart_item'].pop(item[0], None)
                if 'cart_item' in session:
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(session['cart_item'][key]['quantity'])
                        individual_price = float(session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                break

        if all_total_quantity == 0:
            session.clear()
            return redirect(url_for('.products'))
        else:
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price
            return redirect(request.referrer)

    except Exception as e:
        print(e)


def array_merge( first_array , second_array ):
    if isinstance( first_array , list ) and isinstance( second_array , list ):
        return first_array + second_array
    elif isinstance( first_array , dict ) and isinstance( second_array , dict ):
        return dict( list( first_array.items() ) + list( second_array.items() ) )
    elif isinstance( first_array , set ) and isinstance( second_array , set ):
        return first_array.union( second_array )
    return False

if __name__ == "__main__":
    app.run(debug=True)