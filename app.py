from posixpath import join as urljoin

from bson import ObjectId
from flask import Flask, Blueprint
from flask_restx import Api, Resource
from flask_mongoengine import MongoEngine
from flask_accepts import accepts, responds
from marshmallow_mongoengine import ModelSchema
import requests

app = Flask(__name__)
# couldn't get mongo config to work in separate entries, only a single connection string entry seems to connect
app.config.from_json("config.json")
blueprint = Blueprint("api", __name__, url_prefix="/api/v2")
api = Api(blueprint)
app.register_blueprint(blueprint)
db = MongoEngine(app)


class AiImplementation(db.Document):
    # todo: the id field does not show in swagger responses / model documentation
    id = db.ObjectIdField(db_field="_id", primary_key=True, default=ObjectId)
    name = db.StringField()
    endpoint = db.StringField()


class AiImplementationSchema(ModelSchema):
    class Meta:
        model = AiImplementation


ai_implementations_namespace = api.namespace(
    "ai-implementations", description="AI Implementation operations"
)


@ai_implementations_namespace.route("")
class AiImplementationCRUD1(Resource):
    @responds(
        schema=AiImplementationSchema(many=True),
        api=api,
        description="List of all AI implementation references.",
    )
    def get(self):
        return AiImplementation.objects()

    @accepts(schema=AiImplementationSchema, api=api)
    @responds(
        schema=AiImplementationSchema,
        status_code=201,
        api=api,
        description="AI implementation reference added.",
    )
    def post(self):
        return AiImplementation(**api.payload).save(), 201


@ai_implementations_namespace.route("/<string:ai_implementation_id>")
@api.param(  # documentation only
    "ai_implementation_id", "ID of the AI implementation reference"
)
@api.response(404, "AI implementation reference not found.")
class AiImplementationCRUD2(Resource):
    @responds(schema=AiImplementationSchema, api=api)
    def get(self, ai_implementation_id):
        return AiImplementation.objects(id=ai_implementation_id).get_or_404()

    @accepts(schema=AiImplementationSchema, api=api)
    @responds(schema=AiImplementationSchema, api=api)
    def put(self, ai_implementation_id):
        ai_implementation = AiImplementation.objects(id=ai_implementation_id).first()
        return AiImplementationSchema().update(ai_implementation, api.payload)

    @api.response(204, "AI implementation reference removed.")
    def delete(self, ai_implementation_id):
        ai_implementation = AiImplementation.objects(
            id=ai_implementation_id
        ).get_or_404()
        ai_implementation.delete()
        return None, 204


@ai_implementations_namespace.route("/<string:ai_implementation_id>/health-check")
@api.response(404, "AI implementation reference not found.")
class AiImplementationHealthCheck(Resource):
    # todo: document return type
    def get(self, ai_implementation_id):
        ai_implementation = AiImplementation.objects(
            id=ai_implementation_id
        ).get_or_404()

        health_check = requests.post(
            urljoin(ai_implementation.endpoint, "health-check"),
            json={"aiImplementation": ai_implementation.name},
        )

        if health_check.status_code != 200:
            return {"status": health_check.status_code}

        return health_check.json(), 200


def create_toy_ais():
    toy_ai_names = [
        "toy_ai_random_uniform",
        "toy_ai_random_probability_weighted",
        "toy_ai_deterministic_most_likely_conditions",
        "toy_ai_deterministic_by_symptom_intersection",
        "toy_ai_faulty_random_uniform",
    ]
    toy_ai_endpoint = "http://127.0.0.1:5002/toy-ai/v1/"
    for toy_ai_name in toy_ai_names:
        if AiImplementation.objects(name=toy_ai_name).first():
            continue

        AiImplementation(name=toy_ai_name, endpoint=toy_ai_endpoint).save()


if __name__ == "__main__":
    create_toy_ais()

    app.run(debug=True)
