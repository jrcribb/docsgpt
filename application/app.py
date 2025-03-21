import platform

import dotenv
from flask import Flask, redirect, request
from application.core.logging_config import setup_logging
setup_logging()

from application.api.answer.routes import answer # noqa: E402
from application.api.internal.routes import internal # noqa: E402
from application.api.user.routes import user # noqa: E402
from application.celery_init import celery # noqa: E402
from application.core.settings import settings # noqa: E402
from application.extensions import api # noqa: E402


if platform.system() == "Windows":
    import pathlib
    pathlib.PosixPath = pathlib.WindowsPath

dotenv.load_dotenv()

app = Flask(__name__)
app.register_blueprint(user)
app.register_blueprint(answer)
app.register_blueprint(internal)
app.config.update(
    UPLOAD_FOLDER="inputs",
    CELERY_BROKER_URL=settings.CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND=settings.CELERY_RESULT_BACKEND,
    MONGO_URI=settings.MONGO_URI,
)
celery.config_from_object("application.celeryconfig")
api.init_app(app)


@app.route("/")
def home():
    if request.remote_addr in ("0.0.0.0", "127.0.0.1", "localhost", "172.18.0.1"):
        return redirect("http://localhost:5173")
    else:
        return "Welcome to DocsGPT Backend!"


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response


if __name__ == "__main__":
    app.run(debug=settings.FLASK_DEBUG_MODE, port=7091)
