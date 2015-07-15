from flask import Flask, render_template, request, redirect, url_for
from flask import session as login_session
from flask import make_response, flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Product, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import random
import string
import xml.etree.ElementTree as ET


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']

XML_VERSION = '<?xml version="1.0" encoding="UTF-8"?>'


# Connect to the database and create a database session
engine = create_engine('sqlite:///grocery_store.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/grocerystore/categories/JSON')
def categoriesJSON():
    """JSON API to get info about all categories."""
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/grocerystore/products/JSON')
def productsJSON():
    """JSON API to get info about all products."""
    products = session.query(Product).all()
    return jsonify(products=[p.serialize for p in products])


@app.route('/grocerystore/<category_name>/products/JSON')
def categoryJSON(category_name):
    """JSON API to get info about a given category."""
    session.query(Category).filter_by(name=category_name).one()
    products = session.query(Product).filter_by(
        category_name=category_name).all()
    return jsonify(products=[p.serialize for p in products])


@app.route('/grocerystore/<category_name>/<product_name>/JSON')
def productJSON(category_name, product_name):
    """JSON API to get info about a given product and category."""
    product = session.query(Product).filter_by(name=product_name).one()
    return jsonify(product=product.serialize)


@app.route('/grocerystore/categories/XML')
def categoriesXML():
    """XML API to get info about all categories."""
    allCategories = session.query(Category).all()
    # Build up the XML tree
    categories = ET.Element('categories')
    for category in allCategories:
        cat = ET.SubElement(categories, 'category')
        name = ET.SubElement(cat, 'name')
        name.text = category.name
        description = ET.SubElement(cat, 'description')
        description.text = category.description
        user_id = ET.SubElement(cat, 'user_id')
        user_id.text = str(category.user_id)
    output = XML_VERSION + ET.tostring(categories)
    response = make_response(output, 200)
    response.headers['Content-Type'] = 'application/xml'
    return response


@app.route('/grocerystore/products/XML')
def productsXML():
    """XML API to get info about all products."""
    allProducts = session.query(Product).all()
    # Build up the XML tree
    products = ET.Element('products')
    for product in allProducts:
        prod = ET.SubElement(products, 'product')
        name = ET.SubElement(prod, 'name')
        name.text = product.name
        description = ET.SubElement(prod, 'description')
        description.text = product.description
        price = ET.SubElement(prod, 'price')
        price.text = product.price
        category = ET.SubElement(prod, 'category')
        category.text = product.category_name
        user_id = ET.SubElement(prod, 'user_id')
        user_id.text = str(product.user_id)
    output = XML_VERSION + ET.tostring(products)
    response = make_response(output, 200)
    response.headers['Content-Type'] = 'application/xml'
    return response


@app.route('/grocerystore/<category_name>/products/XML')
def categoryXML(category_name):
    """XML API to get info about a given category."""
    session.query(Category).filter_by(name=category_name).one()
    allProducts = session.query(Product).filter_by(
        category_name=category_name).all()
    # Build up the XML tree
    products = ET.Element('products')
    for product in allProducts:
        prod = ET.SubElement(products, 'product')
        name = ET.SubElement(prod, 'name')
        name.text = product.name
        description = ET.SubElement(prod, 'description')
        description.text = product.description
        price = ET.SubElement(prod, 'price')
        price.text = product.price
        category = ET.SubElement(prod, 'category')
        category.text = product.category_name
        user_id = ET.SubElement(prod, 'user_id')
        user_id.text = str(product.user_id)
    output = XML_VERSION + ET.tostring(products)
    response = make_response(output, 200)
    response.headers['Content-Type'] = 'application/xml'
    return response


@app.route('/grocerystore/<category_name>/<product_name>/XML')
def productXML(category_name, product_name):
    """XML API to get info about a given product and category."""
    product = session.query(Product).filter_by(name=product_name).one()
    # Build up the XML tree
    prod = ET.Element('product')
    name = ET.SubElement(prod, 'name')
    name.text = product.name
    description = ET.SubElement(prod, 'description')
    description.text = product.description
    price = ET.SubElement(prod, 'price')
    price.text = product.price
    category = ET.SubElement(prod, 'category')
    category.text = product.category_name
    user_id = ET.SubElement(prod, 'user_id')
    user_id.text = str(product.user_id)
    output = XML_VERSION + ET.tostring(prod)
    response = make_response(output, 200)
    response.headers['Content-Type'] = 'application/xml'
    return response


@app.route('/login/')
def login():
    """Login function which creates and saves an
       anti forgery token, renders the login page and
       starts the login process."""
    # redirect to the main page after logging in
    # TODO redirect to different pages
    redirect_to = url_for('showGroceryStore')
    if 'redirect_to' in login_session.keys():
        redirect_to = login_session['redirect_to']
        del login_session['redirect_to']
    return render_template('login.html',
                           CLIENT_ID=CLIENT_ID,
                           REDIRECT_TO=redirect_to)


@app.route('/')
@app.route('/grocerystore/')
def showGroceryStore():
    """Show the grocerystore with all categories."""
    categories = session.query(Category).order_by(asc(Category.name))
    products = session.query(Product).order_by(asc(Product.category_name))
    username = getUsername()
    return render_template('showGroceryStore.html',
                           categories=categories,
                           products=products,
                           username=username)


@app.route('/grocerystore/<category_name>/products/')
def showCategory(category_name):
    """Show the products of a given category."""
    category = session.query(Category).filter_by(name=category_name).one()
    products = session.query(Product).filter_by(
        category_name=category.name).all()
    username = getUsername()
    return render_template('showCategory.html',
                           products=products,
                           category=category,
                           username=username)


@app.route('/grocerystore/<category_name>/<product_name>')
def showProduct(category_name, product_name):
    """Show one given product of a given category."""
    product = session.query(Product).filter_by(
        category_name=category_name, name=product_name).one()
    category = session.query(Category).filter_by(name=category_name).one()
    username = getUsername()
    return render_template('showProduct.html',
                           product=product,
                           category=category,
                           username=username)


@app.route('/grocerystore/newcategory/', methods=['GET', 'POST'])
def newCategory():
    """Create a new category."""
    if 'username' not in login_session.keys():
        login_session['redirect_to'] = url_for('newCategory')
        return redirect(url_for('login'))
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                               description=request.form['description'],
                               user_id=login_session['user_id'])
        # TODO do not create a category that is already existing
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showGroceryStore'))
    else:
        username = getUsername()
        return render_template('newCategory.html',
                               username=username,
                               category=None)


@app.route('/grocerystore/newproduct/', methods=['GET', 'POST'])
def newProduct():
    """Create a new product."""
    if 'username' not in login_session.keys():
        login_session['redirect_to'] = url_for('newProduct')
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category_name = request.form['category']

        newProduct = Product(name=name,
                             description=description,
                             price=price,
                             category_name=category_name,
                             user_id=login_session['user_id'])
        # TODO do not create an product that is already existing for the cat
        session.add(newProduct)
        session.commit()
        return redirect(url_for('showCategory', category_name=category_name))
    else:
        categories = session.query(Category).order_by(asc(Category.name))
        username = getUsername()
        return render_template('newProduct.html',
                               categories=categories,
                               product=None,
                               username=username)


@app.route('/grocerystore/<category_name>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_name):
    """Delete the given category and its connected products."""
    if 'username' not in login_session.keys():
        login_session['redirect_to'] = url_for('deleteCategory',
                                               category_name=category_name)
        return redirect(url_for('login'))

    deletedCategory = (session.query(Category).filter_by(
        name=category_name).one())
    if request.method == 'POST':
        # Delete all products of the category
        deletedProducts = (session.query(Product).filter_by(
            category_name=deletedCategory.name).all())
        for product in deletedProducts:
            session.delete(product)
        session.delete(deletedCategory)
        session.commit()
        return redirect(url_for('showGroceryStore'))
    else:
        # check whether the user is the owner
        if deletedCategory.user_id == login_session['user_id']:
            username = getUsername()
            return render_template('deleteCategory.html',
                                   category=deletedCategory,
                                   username=username)
        else:
            flash("You are not allowed to delete the category!")
            return redirect(url_for('showGroceryStore'))


@app.route('/grocerystore/<category_name>/<product_name>/delete/',
           methods=['GET', 'POST'])
def deleteProduct(category_name, product_name):
    """Delete a given product of a category."""
    if 'username' not in login_session.keys():
        login_session['redirect_to'] = url_for('deleteProduct')
        return redirect(url_for('login'))
    deletedProduct = (session.query(Product).filter_by(
        name=product_name, category_name=category_name).one())
    if request.method == 'POST':
        session.delete(deletedProduct)
        session.commit()
        return redirect(url_for('showCategory', category_name=category_name))
    else:
        # check whether the user is the owner
        if deletedProduct.user_id == login_session['user_id']:
            username = getUsername()
            return render_template('deleteProduct.html',
                                   product=deletedProduct,
                                   username=username,
                                   category_name=category_name)
        else:
            flash("You are not allowed to delete the product!")
            return redirect(url_for('showGroceryStore'))


@app.route('/grocerystore/<category_name>/edit/', methods=['GET', 'POST'])
def editCategory(category_name):
    """Edit a given category."""
    if 'username' not in login_session.keys():
        login_session['redirect_to'] = url_for('editCategory',
                                               category_name=category_name)
        return redirect(url_for('login'))
    editedCategory = session.query(
        Category).filter_by(name=category_name).one()
    if request.method == 'POST':
        if request.form['name']:
            # TODO do not create a category that is already existing
            editedCategory.name = request.form['name']
            return redirect(url_for('showGroceryStore'))
    else:
        if editedCategory.user_id == login_session['user_id']:
            products = (session.query(Product).filter_by(
                        category_name=editedCategory.name).all())
            username = getUsername()
            return render_template('editCategory.html',
                                   category=editedCategory,
                                   username=username,
                                   products=products)
        else:
            flash("You are not allowed to edit the category!")
            return redirect(url_for('showGroceryStore'))


@app.route('/grocerystore/editproduct/<product_name>/',
           methods=['GET', 'POST'])
def editProduct(product_name):
    """Edit a given product."""
    if 'username' not in login_session.keys():
        login_session['redirect_to'] = url_for('editProduct',
                                               product_name=product_name)
        return redirect(url_for('login'))
    editedProduct = session.query(
        Product).filter_by(name=product_name).one()
    if request.method == 'POST':
        if request.form['name']:
            # TODO do not create an product that is already existing
            editedProduct.name = request.form['name']
        if request.form['description']:
            editedProduct.description = request.form['description']
        if request.form['price']:
            editedProduct.price = request.form['price']
        if request.form['category']:
            editedProduct.category_name = request.form['category']

        return redirect(url_for('showCategory',
                                category_name=editedProduct.category_name))
    else:
        if editedProduct.user_id == login_session['user_id']:
            username = getUsername()
            categories = session.query(Category).order_by(asc(Category.name))
            return render_template('editProduct.html',
                                   product=editedProduct,
                                   categories=categories,
                                   username=username)
        else:
            flash("You are not allowed to edit the product!")
            return redirect(url_for('showGroceryStore'))


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Login the user by Google Sign In."""

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)

    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the credentials for later use.
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']

    # in case name is not set, use the email
    if not data['name']:
        login_session['username'] = data['email']

    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h2>Welcome!</h2>'
    output += '<h3>' + login_session['username'] + '</h3>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;'
    output += 'border-radius: 150px;-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;"> '
    flash('Welcome, ' + login_session['username'] + '!')
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """Revoke a current user's token and reset their login_session."""
    # Only disconnect a connected user.
    if login_session.get('credentials') is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    credentials = json.loads(login_session.get('credentials'))
    access_token = credentials['access_token']

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # maybe the access token expired,
    # revoke the refresh token then
    if result['status'] != '200':
        refresh_token = credentials['refresh_token']
        url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
               % refresh_token)
        result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
        flash('Logged out successfully!')
        return redirect(url_for('showGroceryStore'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def createUser(login_session):
    """Create a new user in the database."""
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Returns a user of the given user_id."""
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """Returns the user id connected to the given email
       or None if the email is not existing in the
       database yet."""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUsername():
    """Returns the username if already in the
       login_session, otherwise None."""
    username = None
    if 'username' in login_session.keys():
        username = login_session['username']
    return username


@app.before_request
def csrf_protect():
    """If a POST does not contain a csrf token
       or contains a wrong csrf token
       a Forbidden is raised."""
    if request.method == "POST":
        token = login_session.pop('state', None)
        if not token or(token != request.form.get('state')
                        and token != request.args.get('state')):
            response = make_response(json.dumps('Invalid state parameter.'),
                                     403)
            response.headers['Content-Type'] = 'application/json'
            return response


def generate_csrf_token():
    """Creates a csrf token."""
    if 'state' not in login_session:
        login_session['state'] = get_random_string()
    return login_session['state']


def get_random_string():
    """ Creates an uppercase random string"""
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for x in xrange(32))


app.jinja_env.globals['state'] = generate_csrf_token

if __name__ == '__main__':
    # this has to be changed in production...
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
