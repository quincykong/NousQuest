# app/routes/__init__.py
def register_blueprints(app):
    from app.routes.authorization_routes import auth_bp
    from app.routes.logging_routes import logging_bp
    from app.routes.tag_routes import tag_bp
    from app.routes.user_routes import user_bp
    from app.routes.usergroup_routes import usergroup_bp

    app.register_blueprint(auth_bp, strict_slashes=False)
    app.register_blueprint(logging_bp, strict_slashes=False)
    app.register_blueprint(tag_bp, strict_slashes=False)
    app.register_blueprint(user_bp, strict_slashes=False)
    app.register_blueprint(usergroup_bp, strict_slashes=False)
