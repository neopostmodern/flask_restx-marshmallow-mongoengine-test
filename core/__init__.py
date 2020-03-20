import os.path

from flask import Flask

from core.config import config_path
from core.mongo import db
from core.benchmark.celery import benchmark_tasks
from apis import blueprint


def create_app():
    app = Flask(__name__)
    # couldn't get mongo config to work in separate entries, only a single connection string entry seems to connect
    app.config.from_json(config_path)
    db.init_app(app)

    benchmark_tasks.conf.update(app.config)

    app.register_blueprint(blueprint)

    return app
