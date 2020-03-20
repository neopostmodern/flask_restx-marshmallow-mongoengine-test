from datetime import datetime

from bson import ObjectId
from marshmallow_mongoengine import ModelSchema

from core import db


# todo: convert into a fully typed / field-based regular document once the cases structure is clear
class CaseSet(db.DynamicDocument):
    id = db.ObjectIdField(db_field="_id", primary_key=True, default=ObjectId)
    createdAt = db.DateTimeField(default=datetime.utcnow)
    name = db.StringField(required=True)
    # field 'cases' will be created dynamically


class CaseSetSchema(ModelSchema):
    class Meta:
        model = CaseSet
        model_fields_kwargs = {"createdAt": {"dump_only": True}}
