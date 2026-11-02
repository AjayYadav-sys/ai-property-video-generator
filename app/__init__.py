"""Flask application factory."""

from flask import Flask

from config import DEBUG, MAX_CONTENT_LENGTH, SECRET_KEY, STORAGE_DIR


def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["DEBUG"] = DEBUG
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    from app.routes import bp

    app.register_blueprint(bp)

    @app.errorhandler(413)
    def too_large(_error):
        from flask import flash, redirect, url_for

        flash("Upload is too large. Use up to 8 images, 10 MB each.", "error")
        return redirect(url_for("main.dashboard")), 413

    return app
