from posixpath import join as urljoin

from flask_accepts import accepts, responds
from flask_restx import Resource, Namespace
import requests

from models.ai_implementation import AiImplementation, AiImplementationSchema

api = Namespace("ai-implementations", description="AI Implementation operations")


@api.route("")
class CollectionCRUD(Resource):
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


@api.route("/<string:ai_implementation_id>")
@api.param(  # documentation only
    "ai_implementation_id", "ID of the AI implementation reference"
)
@api.response(404, "AI implementation reference not found.")
class EntityCRUD(Resource):
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


@api.route("/<string:ai_implementation_id>/health-check")
@api.response(404, "AI implementation reference not found.")
class AiImplementationHealthCheck(Resource):
    # todo: document return type
    def get(self, ai_implementation_id):
        ai_implementation = AiImplementation.objects(
            id=ai_implementation_id
        ).get_or_404()

        try:
            health_check = requests.post(
                urljoin(ai_implementation.endpoint, "health-check"),
                json={"aiImplementation": ai_implementation.name},
            )
        except requests.exceptions.ConnectionError:
            return (
                {
                    "status": "Error",
                    "error": "Couldn't connect to AI health check endpoint",
                },
                200,
            )

        if health_check.status_code != 200:
            return (
                {
                    "status": "Error",
                    "error": f"Bad response code from AI health check: {health_check.status_code}",
                },
                200,
            )

        return health_check.json(), 200
