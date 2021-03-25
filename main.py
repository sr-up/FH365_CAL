#  Copyright (c) 2021. fit&healthy 365

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

from FitCalender.FITCalender import calender_html

app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route('/calendar', methods=['GET'])
def challenge_calendar() -> 'html':
    cal = calender_html()
    return render_template('index.html',
                           calendar=cal)


@app.route('/calendar')
def index() -> 'html':
    cal = calender_html()
    return render_template('index.html',
                           calendar=cal)


@app.errorhandler(404)
def page_not_found(e) -> 'html':
    return render_template('error/404.html', error=e.description), 404


@app.errorhandler(500)
def internal_server_error(e) -> 'html':
    return render_template('error/500.html', error=e.description), 500


if __name__ == '__main__':
    app.run(debug="spooky ghosts")
