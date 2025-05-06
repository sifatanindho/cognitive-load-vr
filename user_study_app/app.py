from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import time
import json
import os
import sys
import os.path
import matplotlib
matplotlib.use('Agg')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import run_study
app = Flask(__name__)
app.secret_key = 'secretkey'
@app.route('/lego_images/<path:filename>')
def serve_lego_image(filename):
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return send_from_directory(os.path.join(parent_dir, 'lego_images'), filename)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['group_id'] = request.form['group_id']
        session['participant_id'] = request.form['participant_id']
        session['experiment_type'] = request.form['experiment_type']
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
    participant_id = session.get('participant_id')
    task_number = session.get('task_number', 1)
    image_path = '/static/dream.jpeg'   
    try:
        participant_num = int(participant_id)
        if participant_num == 1:
            image_path = f'/lego_images/task_{task_number}/back.png'
        elif participant_num == 2:
            image_path = f'/lego_images/task_{task_number}/front.png'
        elif participant_num == 3:
            image_path = f'/lego_images/task_{task_number}/left.png'
        elif participant_num == 4:
            image_path = f'/lego_images/task_{task_number}/right.png'
    except ValueError:
        pass
    return render_template('experiment.html', task_number=task_number, image_path=image_path)
@app.route('/finish', methods=['POST'])
def finish():
    if 'task_number' not in session:
        return redirect(url_for('index'))
    session['finish_time'] = time.time()
    participant_id = session.get('participant_id')
    task_number = session.get('task_number')
    image_path = '/static/dream.jpeg'
    try:
        participant_num = int(participant_id)
        if participant_num == 1:
            image_path = f'/lego_images/task_{task_number}/back.png'
        elif participant_num == 2:
            image_path = f'/lego_images/task_{task_number}/front.png'
        elif participant_num == 3:
            image_path = f'/lego_images/task_{task_number}/left.png'
        elif participant_num == 4:
            image_path = f'/lego_images/task_{task_number}/right.png'
    except ValueError:
        pass
    return render_template('report.html', task_number=task_number, image_path=image_path)
@app.route('/submit', methods=['POST'])
def submit():
    if 'task_number' not in session:
        return redirect(url_for('index'))
    group_id = session.get('group_id')
    participant_id = session.get('participant_id')
    experiment_type = session.get('experiment_type')
    task_number = session.get('task_number', 1)
    errors = request.form['errors']
    start_time = session.get('start_time')
    finish_time = session.get('finish_time')
    duration = finish_time - start_time
    report = {
        'group_id': group_id, 
        'participant_id': participant_id,
        'experiment_type': experiment_type,
        'task': task_number,
        'errors': errors, 
        'duration': duration
    }
    with open('last_report.json', 'w') as f:
        json.dump(report, f)
    run_study(report)
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