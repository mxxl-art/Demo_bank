from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = "elite_global_wealth_secret_key"

    from app.routes import main
    app.register_blueprint(main)

    return app
