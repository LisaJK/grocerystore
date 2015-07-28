.. Lisa's Grocery Store documentation master file, created by
   sphinx-quickstart on Fri Jul 24 10:24:56 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Lisa's Grocery Store's documentation!
================================================

Lisa's Grocery Store is an implementation of the Item Catalog project specified in the Udacity Full
Stack Web Developer Nanodegree. 

.. seealso:: https://github.com/LisaJK/grocerystore/blob/master/README.txt
.. seealso:: https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004

General Description
---------------------------

"Lisa's Grocery Store" is a web application that provides a list of products 
within a variety of product categories. 
It integrates user registration and authentication via Google or Facebook. 
Authenticated users have the ability to post, edit, or delete their own products.

**Additional Functionality:**

- API Endpoints: Apart from the required JSON endpoints, the app has also an 
                 implementation of XML and Atom endpoints.
- CRUD: Read:    A product image field is added which can be read from the 
                 database and displayed on the page.
- CRUD: Create:  A product image field can be included when a new product is 
                 created in the database.
- CRUD: Update:  For already existing products, product images can be added, 
                 changed and deleted.
- CRUD: Delete:  The function is implemented using POST requests and nonces to
                 prevent cross-site request forgeries (CSRF).
- Comments:      Comments are (hopefully ;-)) thorough and concise.


Getting Started
---------------
1. Install Vagrant and Virtual Box as described in the course materials of the 
   "Full Stack Foundations".

2. Clone the repository from GitHub
   $ git clone https://github.com/LisaJK/grocerystore.git

3. Launch the Vagrant VM.

4. Move to the directory "/vagrant/catalog"

5. Run the application within the VM by typing "python application.py" in the
   console.

6. Access the application by visiting "http://localhost:8000" on your browser.

.. note:: 
   The app was developed and tested with Chrome Version 43.0.2357.134 m. 
   It was also tested with Firefox 39.0.
   In IE you might have to add https://accounts.google.com to your trusted sites 
   to enable Google Login (Facebook resp.).


Project Folders and Files
-------------------------

1. README.txt: 
   	File containing all necessary information how to download and run the project.

2. application.py:
   	This python file contains the server-side implementation of the app.

3. database_setup.py:
   	This python file contains the setup of the database "grocery_store.db".

4. load_grocery_store.py:
   	Run this python file to add some initial users, product categories and 
   	products to the database "grocery_store_db". 

5. templates folder:
   	This folder contains all Flask templates of the app. 

   - category.html	
   - deleteCategory.html	
   - deleteProduct.html	
   - editCategory.html	
   - editProduct.html	
   - layout.html	
   - login.html	
   - newCategory.html	
   - newProduct.html	
   - product.html	
   - products.html	
   - showCategory.html	
   - showGroceryStore.html	
   - showProduct.html
|
6. static folder:

   - styles.css: CSS file containing the styles applied to the html files.
   - vegetables-752156_1280.jpg: background image.
|
7. uploads folder:
   	Empty folder used to store product images uploaded for products.

8. docs folder:
   	A folder docs containing the documentation created using Sphinx.

9. JSON files containing OAuth2.0 parameters:
   - client_secret_fb.json
   - client_secret_g.json


Python modules
--------------

.. toctree::
    :maxdepth: 2

    modules

API Endpoints
-------------

JSON:

- http://localhost:8000/grocerystore/categories/JSON
- http://localhost:8000/grocerystore/products/JSON
- http://localhost:8000/grocerystore/<category_name>/products/JSON
- http://localhost:8000/grocerystore/<category_name>/<product_name>/JSON

XML:

- http://localhost:8000/grocerystore/categories/XML
- http://localhost:8000/grocerystore/products/XML
- http://localhost:8000/grocerystore/<category_name>/products/XML
- http://localhost:8000/grocerystore/<category_name>/<product_name>/XML

Atom:

- http://localhost:8000/grocerystore/categories/Atom
- http://localhost:8000/grocerystore/products/Atom
- http://localhost:8000/grocerystore/<category_name>/products/Atom
- http://localhost:8000/grocerystore/<category_name>/<product_name>/Atom


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Contact
-------
lisa.kugler@googlemail.com