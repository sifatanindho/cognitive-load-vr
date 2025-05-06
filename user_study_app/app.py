from flask import Flask, render_template, request, redirect, url_for, session
import time
import json
import os

app = Flask(__name__)
app.secret_key = 'secretkey'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['group_id'] = request.form['group_id']
        session['participant_id'] = request.form['participant_id']
        session['task_number'] = 1 
        return redirect(url_for('proxy'))
    return render_template('index.html')

@app.route('/proxy', methods=['GET', 'POST'])
def proxy():
    if 'task_number' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        session['start_time'] = time.time()
        return redirect(url_for('experiment'))
    if session.get('task_number', 1) > 5:
        return render_template('complete.html')
    return render_template('proxy.html', task_number=session.get('task_number', 1))

@app.route('/experiment')
def experiment():
    if 'task_number' not in session:
        return redirect(url_for('index'))
        
    return render_template('experiment.html', task_number=session.get('task_number', 1))

@app.route('/finish', methods=['POST'])
def finish():
    if 'task_number' not in session:
        return redirect(url_for('index'))
    session['finish_time'] = time.time()
    return render_template('report.html', 
                          task_number=session.get('task_number', 1))

@app.route('/submit', methods=['POST'])
def submit():
    if 'task_number' not in session:
        return redirect(url_for('index'))
    group_id = session.get('group_id')
    participant_id = session.get('participant_id')
    task_number = session.get('task_number', 1)
    errors = request.form['errors']
    start_time = session.get('start_time')
    finish_time = session.get('finish_time')
    duration = finish_time - start_time
    report = {
        'group_id': group_id, 
        'participant_id': participant_id, 
        'task': task_number,
        'errors': errors, 
        'duration': duration
    }
    if os.path.exists('reports.json'):
        with open('reports.json', 'r') as f:
            data = json.load(f)
    else:
        data = []
    data.append(report)
    with open('reports.json', 'w') as f:
        json.dump(data, f)
    session['task_number'] = task_number + 1
    return redirect(url_for('proxy'))

if __name__ == '__main__':
    app.run(debug=True)