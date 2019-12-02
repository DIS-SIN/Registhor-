from flask import Blueprint, render_template

# Instantiate blueprint
main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
def splash():
	return render_template('splash.html')


@main.route('/en', methods=['GET'])
def index_en():
	return render_template('index_en.html')


@main.route('/fr', methods=['GET'])
def index_fr():
	return render_template('index_en.html')
