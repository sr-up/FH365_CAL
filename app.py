#  Copyright (c) 2021. fit&healthy 365

from flask import Flask, render_template, request, session, url_for, redirect, abort
from flask_bootstrap import Bootstrap

from FitCalender.FITCalender import calender_html
from Tools.DBcm import Connector

app = Flask(__name__.split('.')[0])

# use os.urandom(24) to generate
app.secret_key = b'\x15\xe9\xda\x94\x9c\xb7\x96\x19\x87[3\x95\xb2\xe6=f\xbe\x88\xc6\xf2\xa6\x8f\x02\x94'

bootstrap = Bootstrap(app)

app.config['database'] = {'host': '127.0.0.1',
                          'user': 'fit365',
                          'password': 'fit365',
                          'database': 'databank'}


@app.route('/calendar', methods=['POST'])
def challenge_calendar_submit():
    cid = request.form.get('cid')
    uid = request.form.get('uid')

    if session.get('uid') == uid:

        do_type = request.form.get('modify')
        date_id = (uid, cid, request.form.get('date'))
        control = Connector(app.config['database'])

        if do_type == 'delete':
            control.delete_challenge_event(*date_id)
        elif do_type == 'insert':
            control.insert_challenge_event(*date_id)

    if uid and cid:
        session['uid'] = uid

    return redirect(url_for('challenge_calendar', cid=cid))


@app.route('/calendar/challenge=<cid>', methods=['GET'])
def challenge_calendar(cid):
    uid = session.get('uid')
    if not uid:
        abort(401)
    receive = Connector(app.config['database'])
    
    header = receive.fetch_challenge_header(cid)
    habits = receive.fetch_challenge_habits(uid, cid)
    challenge_name, challenge_description = header \
        if header and habits \
        else abort(404)

    dates = receive.fetch_challenge_events(uid, cid)
    points = len(dates)

    cal = calender_html(events=dates)

    return render_template('index.html',
                           name=challenge_name,
                           description=challenge_description,
                           points=points,
                           calendar=cal,
                           uid=uid,
                           cid=cid, )


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html',
                           error=e.description), 404


@app.errorhandler(401)
def page_not_found(e):
    return render_template('error/401.html',
                           error=e.description), 401


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html',
                           error=e.description), 500


if __name__ == '__main__':
    app.run(debug="spooky ghosts")
