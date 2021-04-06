#  Copyright (c) 2021. fit&healthy 365
from itertools import chain

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

from FitCalender.FITCalender import calender_html
from Tools.DBcm import ConnectDatabase

app = Flask(__name__.split('.')[0])

bootstrap = Bootstrap(app)


app.config['database'] = {'host': '127.0.0.1',
                          'user': 'fit365',
                          'password': 'fit365',
                          'database': 'databank'}


def fetch_challenge_header(cid: int) -> tuple:
    with ConnectDatabase(app.config['database']) as cursor:
        _SQL = 'SELECT name, description FROM challenge WHERE id = %s'
        cursor.execute(_SQL, (cid,))
        return cursor.fetchone()


def fetch_challenge_habits(cid: int, uid: int) -> tuple:
    with ConnectDatabase(app.config['database']) as cursor:
        _SQL = 'SELECT habit1, habit2 ' \
               'FROM person_challenge ' \
               'WHERE person_id = %s AND challenge_id = %s'
        cursor.execute(_SQL, (uid, cid))
        return cursor.fetchone()


def fetch_challenge_events(cid: int, uid: int) -> list:
    with ConnectDatabase(app.config['database']) as cursor:
        _SQL = 'SELECT event_date ' \
               'FROM challenge_event ' \
               'WHERE person_id = %s AND challenge_id = %s'
        cursor.execute(_SQL, (uid, cid))
        rows = cursor.fetchall()
        dates = flatten(rows)
        return dates


def flatten(not_flat):
    flat = list(chain.from_iterable(not_flat))
    return flat


@app.route('/calendar', methods=['POST'])
def challenge_calendar() -> 'html':
    cid = request.form.get('cid')
    uid = request.form.get('uid')

    challenge_name, challenge_description = fetch_challenge_header(cid)
    dates = fetch_challenge_events(cid, uid)
    points = len(dates)

    cal = calender_html(events=dates)

    return render_template('index.html',
                           name=challenge_name,
                           description=challenge_description,
                           points=points,
                           calendar=cal, )


@app.errorhandler(404)
def page_not_found(e) -> 'html':
    return render_template('error/404.html',
                           error=e.description), 404


@app.errorhandler(500)
def internal_server_error(e) -> 'html':
    return render_template('error/500.html',
                           error=e.description), 500


if __name__ == '__main__':
    app.run(debug="spooky ghosts")
