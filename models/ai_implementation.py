from bson import ObjectId
from marshmallow_mongoengine import ModelSchema

from core import db


class AiImplementation(db.Document):
    # todo: the id field does not show in swagger responses / model documentation
    id = db.ObjectIdField(db_field="_id", primary_key=True, default=ObjectId)
    name = db.StringField()
    endpoint = db.StringField()


class AiImplementationSchema(ModelSchema):
    class Meta:
        model = AiImplementation
