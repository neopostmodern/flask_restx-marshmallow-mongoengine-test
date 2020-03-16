from flask import Flask

from core import db
from apis import blueprint
from models.ai_implementation import AiImplementation


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
    app = Flask(__name__)
    # couldn't get mongo config to work in separate entries, only a single connection string entry seems to connect
    app.config.from_json("config.json")
    db.init_app(app)

    app.register_blueprint(blueprint)

    create_toy_ais()

    app.run(debug=True)
