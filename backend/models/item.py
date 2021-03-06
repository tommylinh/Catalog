from marshmallow import Schema, fields

from db import db
from helpers.schemas import *
from helpers.errors import *


class ItemModel(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    description = db.Column(db.String(250))

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('UserModel')

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship('CategoryModel')

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, item_id):
        return cls.query.filter_by(id=item_id).first()

    def __init__(self, name, description, category_id, author_id):
        self.name = name
        self.description = description
        self.category_id = category_id
        self.author_id = author_id

    def represent(self):
        schema = ItemSchema()
        return schema.dump(self).data

    def save_to_db(self):
        try:
            db.session.add(self)
            db.session.commit()
        # except IntegrityError:
        except Exception:
            raise BadRequestError('Failed to save item')
            db.session.rollback()

    def delete_from_db(self):
        try:
            db.session.delete(self)
            db.session.commit()
        # except IntegrityError:
        except Exception:
            raise BadRequestError('Failed to delete item')
            db.session.rollback()
