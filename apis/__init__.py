from flask import Blueprint
from flask_restx import Api

from .ai_implementations import api as ai_implementations_namespace

blueprint = Blueprint("api", __name__, url_prefix="/api/v2")
api = Api(blueprint)

api.add_namespace(ai_implementations_namespace, path="/ai-implementations")
