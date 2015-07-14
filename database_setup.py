# Database setup for Catalog App
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    """Class representing a user"""

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture
        }


class Category(Base):
    """Class representing a Category"""

    __tablename__ = 'category'

    name = Column(String(80), primary_key=True)
    description = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id
        }


class Product(Base):
    """Class representing an product"""

    __tablename__ = 'product'

    name = Column(String(80), primary_key=True)
    description = Column(String(250))
    price = Column(String(20))
    category_name = Column(Integer,
                           ForeignKey('category.name'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category_name': self.category_name,
            'user_id': self.user_id
        }


engine = create_engine('sqlite:///grocery_store.db')

Base.metadata.create_all(engine)
