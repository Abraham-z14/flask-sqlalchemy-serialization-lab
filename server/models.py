from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from marshmallow import Schema, fields


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # A customer can leave many reviews.
    reviews = db.relationship(
        'Review',
        back_populates='customer',
        cascade='all, delete-orphan'
    )

    # Gives direct access to items through the customer's reviews.
    items = association_proxy('reviews', 'item')

    def __repr__(self):
        return f'<Customer {self.id}, {self.name}>'


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)

    # An item can have many reviews.
    reviews = db.relationship(
        'Review',
        back_populates='item',
        cascade='all, delete-orphan'
    )

    # Gives direct access to customers through reviews.
    customers = association_proxy('reviews', 'customer')

    def __repr__(self):
        return f'<Item {self.id}, {self.name}, {self.price}>'


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey('customers.id')
    )

    item_id = db.Column(
        db.Integer,
        db.ForeignKey('items.id')
    )

    customer = db.relationship(
        'Customer',
        back_populates='reviews'
    )

    item = db.relationship(
        'Item',
        back_populates='reviews'
    )

    def __repr__(self):
        return f'<Review {self.id}, {self.comment}>'


# Marshmallow schemas turn SQLAlchemy model objects into
# JSON-friendly Python dictionaries.


class CustomerSchema(Schema):
    id = fields.Int()
    name = fields.Str()

    # Avoid circular recursion by removing Review's relationships
    # when Review is nested inside Customer.
    reviews = fields.Nested(
        'ReviewSchema',
        many=True,
        exclude=('customer', 'item')
    )

    # Association-proxy relationship.
    items = fields.Nested(
        'ItemSchema',
        many=True,
        exclude=('reviews', 'customers')
    )


class ItemSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    price = fields.Float()

    reviews = fields.Nested(
        'ReviewSchema',
        many=True,
        exclude=('customer', 'item')
    )

    customers = fields.Nested(
        'CustomerSchema',
        many=True,
        exclude=('reviews', 'items')
    )


class ReviewSchema(Schema):
    id = fields.Int()
    comment = fields.Str()

    # Foreign-key IDs are intentionally not serialized.
    # Instead, serialize the related model itself.
    customer = fields.Nested(
        'CustomerSchema',
        exclude=('reviews', 'items')
    )

    item = fields.Nested(
        'ItemSchema',
        exclude=('reviews', 'customers')
    )