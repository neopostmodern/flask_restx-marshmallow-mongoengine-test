from concurrent.futures import as_completed
from enum import Enum

from mongoengine import connect
from requests_futures.sessions import FuturesSession


from models.ai_implementation import AiImplementation
from models.benchmarking_session import BenchmarkingSession
from core.config import config
from models.case_set import CaseSet
from .celery import benchmark_tasks


class Status(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERRORED = "errored"


@benchmark_tasks.task(bind=True)
def run_benchmark(self, benchmark_id: str):
    print("Run benchmark: " + benchmark_id)
    connect(
        "flask-test", host=config["MONGODB_SETTINGS"]["host"],
    )

    self.update_state(state="RUNNING")
    benchmarking_session: BenchmarkingSession = BenchmarkingSession.objects(
        id=benchmark_id
    ).first()
    ai_implementations: [AiImplementation] = AiImplementation.objects(
        id__in=benchmarking_session.aiImplementationIds
    )
    case_set: CaseSet = CaseSet.objects(id=benchmarking_session.caseSetId).first()

    def response_template():
        template = {}

        for ai_implementation in ai_implementations:
            template[str(ai_implementation.id)] = {"status": Status.PENDING.name}

        return template

    responses = [
        {
            "caseId": case["caseData"]["caseId"],
            "caseIndex": case_index,
            "responses": response_template(),
        }
        for case_index, case in enumerate(case_set.cases)
    ]

    def update_response(case_index, ai_implementation_id, status: Status):
        responses[case_index]["responses"][str(ai_implementation_id)][
            "status"
        ] = status.name
        self.update_state(state="RUNNING", meta=responses)

    def response_hook_factory(case_index, ai_implementation_id):
        def response_hook(resp, *args, **kwargs):
            if resp.status_code != 200:
                update_response(case_index, ai_implementation_id, Status.ERRORED)

            ai_response = resp.json()

            update_response(case_index, ai_implementation_id, Status.COMPLETE)

            return {
                "case_index": case_index,
                "ai_implementation_id": ai_implementation_id,
                "ai_response": ai_response,
            }

        return response_hook

    session = FuturesSession(max_workers=len(ai_implementations))

    results = []
    for case_index, case in enumerate(case_set.cases):
        futures = []

        for ai_implementation in ai_implementations:
            update_response(case_index, ai_implementation.id, Status.PROCESSING)

            ai_endpoint = ai_implementation.endpoint + "solve-case"
            futures.append(
                session.post(
                    ai_endpoint,
                    json={
                        "caseData": case["caseData"],
                        "aiImplementation": ai_implementation.name,
                    },
                    hooks={
                        "response": response_hook_factory(
                            case_index, ai_implementation.id
                        )
                    },
                )
            )

        # wait for all to complete
        results.extend(as_completed(futures))

    # todo: store results? – ai_response["conditions"], ai_response["triage"]
    print(results)

    return responses
