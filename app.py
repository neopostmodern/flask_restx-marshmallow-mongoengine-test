import json

from core import create_app
from models.ai_implementation import AiImplementation
from models.case_set import CaseSet


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


def store_london_case_set():
    if CaseSet.objects(name="London Model Cases").first():
        return

    with open("./data/london-cases.json", "r") as london_cases_json_file:
        london_cases = json.load(london_cases_json_file)

    london_case_set = CaseSet(name="London Model Cases")
    london_case_set["cases"] = london_cases
    london_case_set.save()


if __name__ == "__main__":
    app = create_app()

    create_toy_ais()
    store_london_case_set()

    app.run(debug=True)
