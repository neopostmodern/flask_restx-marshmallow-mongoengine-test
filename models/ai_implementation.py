from bson import ObjectId
from marshmallow_mongoengine import ModelSchema

from core import db


class AiImplementation(db.Document):
    id = db.ObjectIdField(db_field="_id", primary_key=True, default=ObjectId)
    name = db.StringField()
    endpoint = db.StringField()


class AiImplementationSchema(ModelSchema):
    class Meta:
        model = AiImplementation
