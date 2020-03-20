from datetime import datetime

from bson import ObjectId
from marshmallow_mongoengine import ModelSchema

from core import db


class BenchmarkingSession(db.Document):
    id = db.ObjectIdField(db_field="_id", primary_key=True, default=ObjectId)
    createdAt = db.DateTimeField(default=datetime.utcnow)
    aiImplementationIds = db.ListField(db.StringField(), required=True, min_length=1)
    caseSetId = db.StringField(required=True)
    taskId = db.StringField()


class BenchmarkingSessionSchema(ModelSchema):
    class Meta:
        model = BenchmarkingSession
        model_fields_kwargs = {"createdAt": {"dump_only": True}}
        exclude = ("taskId",)
