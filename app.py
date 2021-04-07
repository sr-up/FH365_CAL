#  Copyright (c) 2021. fit&healthy 365
from itertools import chain

from flask import Flask, render_template, request, session, url_for, redirect, abort
from flask_bootstrap import Bootstrap

from FitCalender.FITCalender import calender_html
from Tools.DBcm import ConnectDatabase, BeginDatabase

app = Flask(__name__.split('.')[0])

# use os.urandom(24) to generate
app.secret_key = b'\x15\xe9\xda\x94\x9c\xb7\x96\x19\x87[3\x95\xb2\xe6=f\xbe\x88\xc6\xf2\xa6\x8f\x02\x94'

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


def delete_challenge_event(cid: int, uid: int, date: str):
    with BeginDatabase(app.config['database']) as cursor:
        _SQL = 'DELETE FROM challenge_event ' \
               'WHERE person_id = %s' \
               ' AND challenge_id = %s' \
               ' AND event_date = %s'
        cursor.execute(_SQL, (uid, cid, date))


def insert_challenge_event(cid: int, uid: int, date: str):
    with BeginDatabase(app.config['database']) as cursor:
        _SQL = 'INSERT INTO challenge_event ' \
               '(person_id, challenge_id, event_date)' \
               'VALUES (%s, %s , %s)'
        cursor.execute(_SQL, (uid, cid, date))


def flatten(not_flat):
    flat = list(chain.from_iterable(not_flat))
    return flat


@app.route('/calendar', methods=['POST'])
def challenge_calendar_submit() -> 'html':
    cid = request.form.get('cid')
    uid = request.form.get('uid')

    if session.get('uid') == uid:
        do_type = request.form.get('modify')
        if do_type == 'delete':
            delete_challenge_event(cid, uid, request.form.get('date'))
        elif do_type == 'insert':
            insert_challenge_event(cid, uid, request.form.get('date'))

    if cid and uid:
        session['uid'] = uid

    return redirect(url_for('challenge_calendar', cid=cid))


@app.route('/calendar/<cid>', methods=['GET'])
def challenge_calendar(cid) -> 'html':
    uid = session.get('uid')
    if not uid:
        abort(401)

    header = fetch_challenge_header(cid)
    habits = fetch_challenge_habits(cid, uid)
    challenge_name, challenge_description = header if header and habits else abort(404)

    dates = fetch_challenge_events(cid, uid)
    points = len(dates)

    cal = calender_html(events=dates)

    return render_template('index.html',
                           name=challenge_name,
                           description=challenge_description,
                           points=points,
                           calendar=cal,
                           cid=cid, uid=uid)


@app.errorhandler(404)
def page_not_found(e) -> 'html':
    return render_template('error/404.html',
                           error=e.description), 404


@app.errorhandler(401)
def page_not_found(e) -> 'html':
    return render_template('error/401.html',
                           error=e.description), 401


@app.errorhandler(500)
def internal_server_error(e) -> 'html':
    return render_template('error/500.html',
                           error=e.description), 500


if __name__ == '__main__':
    app.run(debug="spooky ghosts")
