from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey, Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Customer(db.Model, SerializerMixin):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    reviews = db.relationship('Review', back_populates='customer')

    # Association proxy to get items through reviews
    items = association_proxy('reviews', 'item', creator=lambda item: Review(item=item))

    def to_dict(self):
        customer_dict = super().to_dict()
        if 'reviews' in customer_dict:
            for review in customer_dict['reviews']:
                review.pop('customer', None)  # Exclude the customer from the review
        return customer_dict

    def __repr__(self):
        return f'<Customer {self.id}, {self.name}>'

class Item(db.Model, SerializerMixin):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    reviews = db.relationship('Review', back_populates='item')

    # Custom to_dict method to exclude reviews.item and avoid recursion
    def to_dict(self):
        item_dict = super().to_dict()
        if 'reviews' in item_dict:
            for review in item_dict['reviews']:
                review.pop('item', None)  # Exclude the item from the review
        return item_dict

    def __repr__(self):
        return f'<Item {self.id}, {self.name}, {self.price}>'


class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'

    # Composite primary key with customer_id and item_id
    customer_id = Column(Integer, ForeignKey('customers.id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), primary_key=True)

    # Regular columns
    comment = Column(String)

    # Relationships
    customer = relationship('Customer', back_populates='reviews')
    item = relationship('Item', back_populates='reviews')

    # Serialization rules to avoid recursion
    serialize_rules = ('-customer.reviews', '-item.reviews',)

    def __repr__(self):
        return f'<Review Customer: {self.customer_id}, Item: {self.item_id}>'