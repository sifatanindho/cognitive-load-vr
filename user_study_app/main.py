from flask import Flask, render_template, request, redirect, url_for, session
import time
import json
import os

app = Flask(__name__)
app.secret_key = 'secretkey'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['participant_id'] = request.form['participant_id']
        session['start_time'] = time.time()
        return redirect(url_for('experiment'))
    return render_template('index.html')

@app.route('/experiment')
def experiment():
    return render_template('experiment.html')

@app.route('/finish', methods=['POST'])
def finish():
    session['finish_time'] = time.time()
    return render_template('report.html', image='static/sample_image.jpg')

@app.route('/submit', methods=['POST'])
def submit():
    participant_id = session.get('participant_id')
    errors = request.form['errors']
    start_time = session.get('start_time')
    finish_time = session.get('finish_time')
    duration = finish_time - start_time
    report = {'participant_id': participant_id, 'errors': errors, 'duration': duration}
    if os.path.exists('reports.json'):
        with open('reports.json', 'r') as f:
            data = json.load(f)
    else:
        data = []
    data.append(report)
    with open('reports.json', 'w') as f:
        json.dump(data, f)
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
