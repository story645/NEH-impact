import sqlite3
from app import app
from flask import flash, redirect, render_template
from flask import request, session, url_for, jsonify
from app.forms import ZipForm

# This lets us import dictionaries from the database instead of tuples
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def db_connect(db_name):
    """Connect to named database and returns cursor object."""
    conn = sqlite3.connect(db_name)
    conn.row_factory = dict_factory
    return conn


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('404.html'), 500


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    form = ZipForm(request.form)
    if request.method == 'POST' and form.validate():

        zip_input = request.form['zip']

        if 'distance' in request.form:
            distance = request.form['distance']
        else:
            distance = 2.0

        conn = sqlite3.connect('grants.db')
        cur = conn.cursor()
        distance_query = 'SELECT end_zip from distances WHERE start_zip=? AND distance<?;'

        zips_to_return = [zipcode[0] for zipcode in cur.execute(distance_query, (zip_input, distance,)).fetchall()]
        
        query = 'SELECT Institution, \
InstCity, \
InstState, \
InstCountry, \
YearAwarded, \
ProjectTitle, \
Program, \
ProjectDesc, \
ToSupport, \
PrimaryDiscipline \
FROM grants WHERE ShortPostal=? \
AND (ProjectDesc is not null OR ToSupport is not null);'
        conn2 = db_connect('grants.db')
        cur = conn2.cursor()
        grants = cur.execute(query, (zip_input,)).fetchall()

        return render_template('results.html', grants=grants, form=form, jquery=True)
        
    else:
        return render_template('index.html', form=form, jquery=True)

    
    form = ZipForm(request.form)
    return render_template('index.html', form=form, jquery=True)


