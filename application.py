from flask import Flask, render_template, request, redirect, url_for
from flask import session as login_session
from flask import make_response, flash, jsonify, send_from_directory
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
from werkzeug import secure_filename
import os


app = Flask(__name__)

# client id given by Google
GOOGLE_CLIENT_ID = json.loads(
    open('client_secret_g.json', 'r').read())['web']['client_id']

FB_APP_ID = json.loads(
    open('client_secret_fb.json', 'r').read())['app_id']

FB_APP_SECRET = json.loads(
    open('client_secret_fb.json', 'r').read())['client_secret']

# TODO URLs schoen machen
URL_FB_LTT = "https://graph.facebook.com/oauth/access_token"

XML_VERSION = '<?xml version="1.0" encoding="UTF-8"?>'

# Used for the product image uploads
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'JPG'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


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
    return createXMLResponse(categories)


@app.route('/grocerystore/products/XML')
def productsXML():
    """XML API to get info about all products."""
    allProducts = session.query(Product).all()
    products = ET.Element('products')
    for product in allProducts:
        prod = buildProductXML(product)
        products.append(prod)
    return createXMLResponse(products)


@app.route('/grocerystore/<category_name>/products/XML')
def categoryXML(category_name):
    """XML API to get info about a given category."""
    session.query(Category).filter_by(name=category_name).one()
    allProducts = session.query(Product).filter_by(
        category_name=category_name).all()
    products = ET.Element('products')
    for product in allProducts:
        prod = buildProductXML(product)
        products.append(prod)
    return createXMLResponse(products)


@app.route('/grocerystore/<category_name>/<product_name>/XML')
def productXML(category_name, product_name):
    """XML API to get info about a given product and category."""
    product = session.query(Product).filter_by(name=product_name).one()
    prod = buildProductXML(product)
    return createXMLResponse(prod)


def buildProductXML(product):
    """ Builds up the XML tree for a product."""
    prod = ET.Element('product')
    name = ET.SubElement(prod, 'name')
    name.text = product.name
    description = ET.SubElement(prod, 'description')
    description.text = product.description
    price = ET.SubElement(prod, 'price')
    price.text = product.price
    image = ET.SubElement(prod, 'image')
    image.text = product.image_file_name,
    category = ET.SubElement(prod, 'category')
    category.text = product.category_name
    user_id = ET.SubElement(prod, 'user_id')
    user_id.text = str(product.user_id)
    return prod


def createXMLResponse(tree):
    """Creates the xml response out of the given tree."""
    output = XML_VERSION + ET.tostring(tree)
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
                           CLIENT_ID=GOOGLE_CLIENT_ID,
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
        filename = None
        file = request.files['image']
        # check if the file is one of the allowed types/extensions
        if file and allowed_file(file.filename):
            # remove unsupported chars
            filename = secure_filename(file.filename)
            # save the file
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        newProduct = Product(name=name,
                             description=description,
                             price=price,
                             category_name=category_name,
                             image_file_name=filename,
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
            # delete all images of the products
            if product.image_file_name:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'],
                          product.image_file_name))
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
        # delete the image of the product
        if deletedProduct.image_file_name:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'],
                                   deleteProduct.image_file_name))
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
        # delete old image if existing ...
        if editedProduct.image_file_name:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'],
                                   editedProduct.image_file_name))
            editedProduct.image_file_name = None
        # ... and save the new one
        if request.files['image']:
            filename = None
            file = request.files['image']
            # check if the image file is one of the allowed types/extensions
            if allowed_file(file.filename):
                # remove unsupported chars
                filename = secure_filename(file.filename)
                # save the image file
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                editedProduct.image_file_name = filename

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


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Login the user by Facebook Sign In."""

    # Obtain the long-term access token
    params = {'fb_exchange_token': request.data,
              'client_id': FB_APP_ID,
              'client_secret': FB_APP_SECRET,
              'grant_type': 'fb_exchange_token'}
    answer = requests.get(URL_FB_LTT, params=params)
    access_token = answer.content
    access_token = access_token.strip("access_token=")
    access_token = access_token.split("&")[0]

    print access_token

    # Get user info
    userinfo_url = "https://graph.facebook.com/me"
    params = {'access_token': access_token,
              'fields': 'name,email',
              'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    name = data['name']
    ext_user_id = data['id']
    email = data['email']

    # Get the picture
    # TODO URL JOIN
    picture_url = "https://graph.facebook.com/v2.4/" + ext_user_id + "/picture"
    print picture_url
    params = {'access_token': access_token,
              'alt': 'json',
              'redirect': 'false',
              'size': 'large'}
    answer = requests.get(picture_url, params=params)
    data = answer.json()
    picture = data['data']['url']

    storeUserData(username=name,
                  email=email,
                  picture=picture,
                  fb_access_token=access_token,
                  ext_user_id=ext_user_id)

    return createLoginOutput()


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Login the user by Google Sign In."""
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret_g.json', scope='')
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
    ext_user_id = credentials.id_token['sub']
    if result['user_id'] != ext_user_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != GOOGLE_CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if the user is already connected.
    stored_credentials = login_session.get('credentials')
    stored_user_id = login_session.get('ext_user_id')
    if stored_credentials is not None and ext_user_id == stored_user_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    storeUserData(username=data['name'],
                  email=data['email'],
                  picture=data['picture'],
                  google_credentials=credentials,
                  ext_user_id=ext_user_id)

    return createLoginOutput()


def storeUserData(username,
                  email,
                  picture,
                  ext_user_id,
                  google_credentials=None,
                  fb_access_token=None):
    """Validates and stores the user data
       given by Google or Facebook."""
    login_session['username'] = username

    # in case name is not set, use the email
    if not username:
        login_session['username'] = email

    login_session['picture'] = picture
    login_session['email'] = email

    if google_credentials:
        login_session['google_credentials'] = google_credentials.to_json()
    elif fb_access_token:
        login_session['fb_access_token'] = fb_access_token

    login_session['ext_user_id'] = ext_user_id

    # Check if a user exists and if not make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id


def createLoginOutput():
    """Creates the login output."""
    output = ''
    output += '<h2>Welcome!</h2>'
    output += '<h3>' + login_session['username'] + '</h3>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; height: 100px;'
    output += 'border-radius: 150px;-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;"> '
    flash('Welcome, ' + login_session['username'] + '!')
    return output


@app.route('/logout')
def logout():
    """Logout a user (Google or Facebook)"""
    if login_session.get('google_credentials'):
        return gdisconnect()
    else:
        return fbdisconnect()


@app.route('/fbdisconnect')
def fbdisconnect():
    """Revoke a current fb access token and reset the login_session."""
    # Only disconnect a connected user.
    if login_session.get('fb_access_token') is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # revoke the access token
    url = "https://graph.facebook.com/v2.4/"
    url += str(login_session.get('ext_user_id'))
    url += "/permissions?access_token="
    url += str(login_session.get('fb_access_token'))
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[0]

    return resetUserSession(result)


@app.route('/gdisconnect')
def gdisconnect():
    """Revoke a current google access token and reset the login_session."""
    # Only disconnect a connected user.
    if login_session.get('google_credentials') is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    credentials = json.loads(login_session.get('google_credentials'))
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

    return resetUserSession(result)


def resetUserSession(result):
    if result['status'] == '200':
        # Reset the user's session.
        if login_session.get('google_credentials'):
            del login_session['google_credentials']
        if login_session.get('fb_access_token'):
            del login_session['fb_access_token']
        if login_session.get('ext_user_id'):
            del login_session['ext_user_id']
        if login_session.get('user_id'):
            del login_session['user_id']
        if login_session.get('username'):
            del login_session['username']
        if login_session.get('email'):
            del login_session['email']
        if login_session.get('picture'):
            del login_session['picture']

        flash('Logged out successfully!')
        return redirect(url_for('showGroceryStore'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/disconnectTest')
def disconnectTest():
    """TODO REMOVE THIS METHOD"""
    # Reset the user's session.
    if login_session.get('google_credentials'):
        del login_session['google_credentials']
    if login_session.get('fb_access_token'):
        del login_session['fb_access_token']
    if login_session.get('ext_user_id'):
        del login_session['ext_user_id']
    if login_session.get('user_id'):
        del login_session['user_id']
    if login_session.get('username'):
        del login_session['username']
    if login_session.get('email'):
        del login_session['email']
    if login_session.get('picture'):
        del login_session['picture']

    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response
    flash('Logged out successfully!')
    return redirect(url_for('showGroceryStore'))


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


def allowed_file(filename):
    """Returns True if the filename has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/uploads/<path:filename>')
def uploads(filename):
    """Locates the given file in the upload directory and shows
       it in the browser."""
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


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
