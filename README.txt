PROJECT 3 Catalog App - Version 1 - July 2015
------------------------------------------------------------------------------


PROJECT DESCRIPTION
------------------------------------------------------------------------------
General Description:

"Lisa's Grocery Store" is a web application that provides a list of products 
within a variety of product categories. It integrates user registration and 
authentication via Google or Facebook. Authenticated users have the ability to 
post, edit, or delete their own products.

Additional Functionality:
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
- Comments:      Comments are (hopefully ;-)) thorough and concise. Comments are
                 mainly presented as docstrings and are integrated in the 
                 documentation created using Sphinx 
                 (start with: /docs/_build/html/index.html).
------------------------------------------------------------------------------


GETTING STARTED
------------------------------------------------------------------------------
1. Install Vagrant and Virtual Box as described in the course materials of 
   "Full Stack Foundations".

2. Clone the repository from GitHub
   $ git clone https://github.com/LisaJK/grocerystore.git

3. Launch the Vagrant VM.

4. Move to the directory "/vagrant/catalog"

5. Run the application within the VM by typing "python application.py" in the
   console.

6. Access the application by visiting "http://localhost:8000" on your browser.

NOTE: The app was developed and tested with Chrome Version 43.0.2357.134 m.
      It was also tested with Firefox 39.0.
      In IE you might have to add https://accounts.google.com to your trusted
      sites to enable Google Login (Facebook resp.).

------------------------------------------------------------------------------


DESCRIPTION OF THE PROJECT FOLDERS AND FILES
------------------------------------------------------------------------------

1. README.txt
   This file (hopefully containing all necessary information to download and
   run the project, otherwise please contact: lisa.kugler@googlemail.com). 

2. application.py
   This python file contains the server-side implementation of the app.

3. database_setup.py
   This python file contains the setup of the database "grocery_store.db".

4. load_grocery_store.py
   Run this python file to add some initial users, product categories and 
   products to the database "grocery_store_db". 

5. templates folder
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

6. static folder
   - styles.css: CSS file containing the styles applied to the html files.
   - vegetables-752156_1280.jpg: background image.

7. uploads folder
   Empty folder used to store product images uploaded for products.

8. docs folder 
   This folder contains the documentation created using Sphinx.
   Start with: /docs/_build/html/index.html

9. JSON files containing OAuth2.0 parameters:
   - client_secret_fb.json
   - client_secret_g.json

------------------------------------------------------------------------------


CONTACT 
------------------------------------------------------------------------------
lisa.kugler@googlemail.com

