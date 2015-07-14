from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Product, User

engine = create_engine('sqlite:///grocery_store.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

user1 = User(name="Emma Kugler", email="emma.kugler@googlemail.com")
user2 = User(name="Paula Kugler", email="paula.kugler@googlemail.com")
user3 = User(name="Frida Kugler", email="frida.kugler@googlemail.com")

# Category Soccer
category1 = Category(name="fruits and vegetables",
                     description="fruits and vegetables",
                     user=user1)

session.add(category1)
session.commit()

product1 = Product(
    name="apple",
    description="an apple is an apple",
    price="2.50 EUR/KG",
    category=category1,
    user=user1)

session.add(product1)
session.commit()

product2 = Product(
    name="peach",
    description="a peach is a peach",
    price="3.00 EUR/KG",
    category=category1,
    user=user2)

session.add(product2)
session.commit()

# Category Tennis
category2 = Category(name="dairy products", user=user2)

session.add(category2)
session.commit()

product3 = Product(
    name="milk",
    description="milk is milk",
    price="1.20 EUR/l",
    category=category2,
    user=user3)

session.add(product3)
session.commit()

product4 = Product(
    name="butter",
    description="butter is butter",
    price="1.50 EUR",
    category=category2,
    user=user2)

session.add(product4)
session.commit()


print "User, Categories and Products added!"
