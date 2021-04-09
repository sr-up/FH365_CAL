#  Copyright (c) 2021. fit&healthy 365

from datetime import datetime

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


@app.route('/calendar/submit', methods=['POST'])
def challenge_calendar_submit():
    uid, cid, year, month = session['uid'], \
                            session['cid'], \
                            session['year'], \
                            session['month']
    day, action = request.form.get('day'), request.form.get('action')

    date_string = '-'.join(str(date_part) for date_part in (year, month, day))

    date_id = (uid, cid, date_string)
    control = Connector(app.config['database'])

    if action == 'delete':
        control.delete_challenge_event(*date_id)
    elif action == 'insert':
        control.insert_challenge_event(*date_id)

    return redirect(url_for('challenge_calendar_show', cid=cid))


@app.route('/calendar', methods=['POST'])
def challenge_calendar_startup():
    cid = request.form.get('cid')
    uid = request.form.get('uid')

    if uid and cid:
        session['uid'] = uid

    return redirect(url_for('challenge_calendar_show', cid=cid))


@app.route('/calendar/<cid>', methods=['GET'])
def challenge_calendar_show(cid):
    uid = session.get('uid')
    if not uid:
        abort(401)
    channel = Connector(app.config['database'])
    wid = channel.fetch_workplace_id(uid)
    header = channel.fetch_challenge_header(cid)
    habits = channel.fetch_challenge_habits(uid, cid)
    challenge_name, challenge_description = header \
        if header and habits \
        else abort(404)

    dates = channel.fetch_challenge_events(uid, cid)
    points = len(dates)

    year = maybe_year(request.args.get('year'))
    if not year:
        year = session.get('year', datetime.today().year)

    month = maybe_month(request.args.get('month'))
    if not month:
        month = session.get('month', datetime.today().month)

    session['year'] = year
    session['month'] = month
    session['cid'] = cid

    cal = calender_html(events=dates, year=year, month=month)

    return render_template('index.html',
                           name=challenge_name,
                           description=challenge_description,
                           points=points,
                           calendar=cal,
                           uid=uid,
                           cid=cid,
                           wid=wid, )


def maybe_year(to_test):
    """
    returns year number if valid, None if empty
    aborts with 404 if not valid
    """
    if not to_test:
        return None

    if to_test.isdigit():
        year = int(to_test)
    else:
        abort(404)

    if year <= 0:
        abort(404)

    return year


def maybe_month(to_test):
    """
    returns month number if valid, None if empty
    aborts with 404 if not valid
    """
    if not to_test:
        return None

    if to_test.isdigit():
        month = int(to_test)
    else:
        abort(404)

    if month < 1 or month > 12:
        abort(404)

    return month


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


@app.context_processor
def external_linker():
    def leader_board_link(wid, cid):
        link = '<a href="http://localhost/LeaderBoard.php?wid=%s&cid=%s">Leader Board</a>' % (wid, cid)
        return link

    def landing_page_link():
        return '<a href="http://localhost/landingPage.php">Main Page</a>'

    def challenge_page_link():
        return '<a href="http://localhost/Challenges.php">Challenge</a>'

    def habit_page_link():
        return '<a href="http://localhost/Habit.php">Habit</a>'

    return dict(leader_board_link=leader_board_link,
                landing_page_link=landing_page_link,
                challenge_page_link=challenge_page_link,
                habit_page_link=habit_page_link, )


if __name__ == '__main__':
    app.run(debug="spooky ghosts")
