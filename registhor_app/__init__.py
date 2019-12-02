from flask import Flask
from flask_cors import CORS
from registhor_app.config import Config


# Application factory
def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(config_class)
	
	# CORS: Allow all origins to hit API routes via AJAX
	cors = CORS(app, resources={r'/api/*': {'origins': '*'}})
	
	# Register database
	from registhor_app import db
	db.init_app(app)
	
	# Register blueprints
	# from registhor_app.comments_routes.routes import comments
	from registhor_app.departments_routes.routes import departments
	from registhor_app.evalhalla_routes.routes import evalhalla
	from registhor_app.main_routes.routes import main
	from registhor_app.offerings_routes.routes import offerings
	from registhor_app.registrations_routes.routes import registrations
	from registhor_app.tombstone_routes.routes import tombstone
	# app.register_blueprint(comments)
	app.register_blueprint(departments)
	app.register_blueprint(evalhalla)
	app.register_blueprint(main)
	app.register_blueprint(offerings)
	app.register_blueprint(registrations)
	app.register_blueprint(tombstone)
	return app
