"""Database setup for Lisa's Grocery Store.
   The database consists of three tables representing
   three objects:

   - User:
     A user is created after login and can
     create, update or delete categories and products.
   - Category:
     A category can be created, updated and deleted.
     It is always owned by one user.
   - Product:
     A product can be created, updated and deleted.
     It is always owned by one user and assigned
     to one category.

"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    """Class representing a user."""

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    """id (Column): the internal user id used as primary key."""

    name = Column(String(100), nullable=False)
    """name (Column): the user name."""

    email = Column(String(200), nullable=False)
    """email (Column): the email of the user."""

    picture = Column(String(250))
    """picture (Column): link to a picture of the user."""

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""

        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture
        }


class Category(Base):
    """Class representing a Category."""

    __tablename__ = 'category'

    name = Column(String(80), primary_key=True)
    """name (Column): the category name (primary key)."""

    description = Column(String(250))
    """description (Column): a description of the category."""

    user_id = Column(ForeignKey('user.id'))
    """user_id (Column): reference to the owner of the category."""

    user = relationship(User)
    """relation to the user who is the owner."""

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id
        }


class Product(Base):
    """Class representing an product."""

    __tablename__ = 'product'

    name = Column(String(80), primary_key=True)
    """name (Column): the product name, primary key."""

    description = Column(String(250))
    """description (Column): a description of the product."""

    price = Column(String(20))
    """price (Column): the price of the product."""

    image_file_name = Column(String(250))
    """image_file_name (str): file name of an image of the product.
            The image is stored in the upload folder.
    """

    category_name = Column(ForeignKey('category.name'))
    """category_name (Column): the category the product belongs to."""

    category = relationship(Category)

    user_id = Column(ForeignKey('user.id'))
    """user_id (Column): the id of the owner of the product."""

    user = relationship(User)
    """relation to the user who is the owner."""

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""

        return {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_file_name': self.image_file_name,
            'category_name': self.category_name,
            'user_id': self.user_id
        }

engine = create_engine('sqlite:///grocery_store.db')

Base.metadata.create_all(engine)
