from posixpath import join as urljoin

from flask_accepts import accepts, responds
from flask_restx import Resource, Namespace

from core.benchmark.run_benchmark import run_benchmark
from models.ai_implementation import AiImplementation
from models.benchmarking_session import BenchmarkingSessionSchema, BenchmarkingSession

api = Namespace("benchmarking-sessions", description="Benchmarking session operations")


@api.route("")
class CollectionCRUD(Resource):
    @responds(
        schema=BenchmarkingSessionSchema(many=True),
        api=api,
        description="List of all benchmarking sessions.",
    )
    def get(self):
        return BenchmarkingSession.objects()

    @accepts(schema=BenchmarkingSessionSchema, api=api)
    @responds(
        schema=BenchmarkingSessionSchema,
        status_code=201,
        api=api,
        description="Benchmarking session created.",
    )
    # todo: flask_accepts suppresses the 400 response!
    # @responds(
    #    status_code=400, description="Unresolved references in object to be created."
    # )
    def post(self):
        for ai_implementation_id in api.payload["aiImplementationIds"]:
            if AiImplementation.objects(id=ai_implementation_id).first() is None:
                return (
                    {"error": f"No such AI implementation: {ai_implementation_id}"},
                    400,
                )

        return BenchmarkingSession(**api.payload).save(), 201


@api.route("/<string:benchmarking_session_id>")
@api.param(  # documentation only
    "benchmarking_session_id", "ID of the benchmarking session"
)
@api.response(404, "Benchmarking session not found.")
class EntityCRUD(Resource):
    @responds(schema=BenchmarkingSessionSchema, api=api)
    def get(self, benchmarking_session_id):
        return BenchmarkingSession.objects(id=benchmarking_session_id).get_or_404()

    @accepts(schema=BenchmarkingSessionSchema, api=api)
    @responds(schema=BenchmarkingSessionSchema, api=api)
    def put(self, benchmarking_session_id):
        ai_implementation = BenchmarkingSession.objects(
            id=benchmarking_session_id
        ).first()
        return BenchmarkingSessionSchema().update(ai_implementation, api.payload)

    @api.response(204, "Benchmarking session deleted.")
    def delete(self, benchmarking_session_id):
        benchmarking_session = BenchmarkingSession.objects(
            id=benchmarking_session_id
        ).get_or_404()
        benchmarking_session.delete()
        return None, 204


@api.route("/<string:benchmarking_session_id>/run")
@api.response(404, "Benchmarking session not found.")
class BenchmarkingSessionHealthCheck(Resource):
    @responds(status_code=202)
    def post(self, benchmarking_session_id):
        benchmarking_session = BenchmarkingSession.objects(
            id=benchmarking_session_id
        ).get_or_404()

        print(f"Calling task for {benchmarking_session_id}...")

        task = run_benchmark.delay(benchmarking_session_id)
        benchmarking_session.taskId = task.id
        benchmarking_session.save()

        return f"/benchmarking_session/{benchmarking_session_id}/status", 202


@api.route("/<string:benchmarking_session_id>/status")
@api.response(404, "Benchmarking session not found.")
class BenchmarkingSessionHealthCheck(Resource):
    # todo: document return type
    @responds(status_code=200)
    def get(self, benchmarking_session_id):
        benchmarking_session = BenchmarkingSession.objects(
            id=benchmarking_session_id
        ).get_or_404()

        print(f"Checking status of benchmarking session '{benchmarking_session_id}'.")

        # check if task id set
        result = run_benchmark.AsyncResult(benchmarking_session.taskId)
        print(result, result.state, result.info)

        return result, 200
