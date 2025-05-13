from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify # type: ignore
import sys
import os
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import run_study
from src.decision_maker import main as decision_maker_main
import time
import json
import shutil
import threading
import matplotlib # type: ignore
matplotlib.use('Agg')
app = Flask(__name__)
app.secret_key = 'cogntiive-load-deez-nuts'
LEGO_IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lego_images'))

# Dictionary to store group data across all users
# Structure: {
#   "group_id": {
#     "task_number": 1,
#     "pending_members": ["1", "2", "3", "4"],  
#     "completed_tasks": [],  
#     "experiment_type": "AI",
#     "participants": {
#       "1": { "reports": [...], "ready_for_experiment": False, "ready_for_report": False, "ready_for_next_task": False },
#       "2": { "reports": [...], "ready_for_experiment": False, "ready_for_report": False, "ready_for_next_task": False },
#       ...
#     }
#   }
# }
group_data = {}
group_data_lock = threading.Lock() # i don't really think we actually need this but this is what all the cool people on stackoverflow are doing

def clear_lego_images_directory(): # this might not work on some people's machines due to permission issues
    if os.path.exists(LEGO_IMAGES_DIR):
        for item in os.listdir(LEGO_IMAGES_DIR):
            item_path = os.path.join(LEGO_IMAGES_DIR, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    else:
        os.makedirs(LEGO_IMAGES_DIR, exist_ok=True)

@app.route('/lego_images/<path:filename>')
def serve_lego_image(filename):
    return send_from_directory(LEGO_IMAGES_DIR, filename)

def initialize_group(group_id, experiment_type):
    with group_data_lock:
        if group_id not in group_data:
            group_data[group_id] = {
                "task_number": 1,
                "pending_members": ["1", "2", "3", "4"],
                "completed_tasks": [],
                "experiment_type": experiment_type,
                "participants": {
                    "1": {
                        "reports": [], 
                        "ready_for_experiment": False, 
                        "ready_for_report": False, 
                        "ready_for_next_task": False
                    },
                    "2": {
                        "reports": [], 
                        "ready_for_experiment": False, 
                        "ready_for_report": False, 
                        "ready_for_next_task": False
                    },
                    "3": {
                        "reports": [], 
                        "ready_for_experiment": False, 
                        "ready_for_report": False, 
                        "ready_for_next_task": False
                    },
                    "4": {
                        "reports": [], 
                        "ready_for_experiment": False, 
                        "ready_for_report": False, 
                        "ready_for_next_task": False
                    }
                }
            }
            clear_lego_images_directory() ## comment this shii out if it gives you access issues, it did with maxi (just delete them manually)
            decision_maker_main()
  

def all_participants_completed(group_id):
    # this must be called with the lock already held
    if group_id in group_data:
        return len(group_data[group_id]["pending_members"]) == 0
    return False

def all_participants_ready_for(group_id, state_key):
    # this must be called with the lock already held
    if group_id in group_data:
        for participant_id, data in group_data[group_id]["participants"].items():
            if not data.get(state_key, False):
                return False
        return True
    return False

def reset_ready_states(group_id, state_key):
    # this must be called with the lock already held
    if group_id in group_data:
        for participant_id, data in group_data[group_id]["participants"].items():
            data[state_key] = False

def count_ready_participants(group_id, state_key):
    # this must be called with the lock already held
    if group_id in group_data:
        count = 0
        for participant_id, data in group_data[group_id]["participants"].items():
            if data.get(state_key, False):
                count += 1
        return count
    return 0

def process_group_task_completion(group_id):
    print(f"Running process_group_task_completion() for group {group_id}")
    if group_id in group_data:
        group = group_data[group_id]
        task_number = group["task_number"]
        total_duration = 0
        total_errors = 0
        participant_count = 0
        for participant_id, data in group["participants"].items():
            if len(data["reports"]) >= task_number and data["reports"][task_number - 1] is not None:
                latest_report = data["reports"][task_number - 1]
                total_duration += latest_report.get("duration", 0)
                total_errors += int(latest_report.get("errors", 0))
                participant_count += 1
        if participant_count > 0:
            avg_duration = total_duration / participant_count
            avg_errors = total_errors / participant_count
            combined_report = {
                "group_id": group_id,
                "task": task_number,
                "experiment_type": group["experiment_type"],
                "avg_duration": avg_duration,
                "avg_errors": avg_errors,
                "participant_count": participant_count
            }
            group["completed_tasks"].append(combined_report)
            run_study(combined_report)
            with open(f'group_{group_id}_task_{task_number}_report.json', 'w') as f:
                json.dump(combined_report, f)
            old_task_number = task_number
            group["task_number"] += 1
            group["pending_members"] = ["1", "2", "3", "4"]
            reset_ready_states(group_id, "ready_for_experiment")
            reset_ready_states(group_id, "ready_for_report")
            reset_ready_states(group_id, "ready_for_next_task")
            print("DOES IT GET PAST RESET")
            return combined_report
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        group_id = request.form['group_id']
        experiment_type = request.form['experiment_type']
        participant_id = request.form['participant_id']
        session['group_id'] = group_id
        session['participant_id'] = participant_id
        session['experiment_type'] = experiment_type
        initialize_group(group_id, experiment_type)
        with group_data_lock:
            if group_id in group_data and participant_id in group_data[group_id]["participants"]:
                group_data[group_id]["participants"][participant_id]["ready_for_next_task"] = True
            if group_id in group_data:
                session['task_number'] = group_data[group_id]["task_number"]
            else:
                session['task_number'] = 1
        return redirect(url_for('wait_for_next_task'))
    return render_template('index.html')


@app.route('/check_all_ready_for_next_task')
def check_all_ready_for_next_task():
    group_id = session.get('group_id')
    with group_data_lock:
        if group_id in group_data:
            all_ready = all_participants_ready_for(group_id, "ready_for_next_task")
            ready_count = count_ready_participants(group_id, "ready_for_next_task")
            total_count = len(group_data[group_id]["participants"])
            return jsonify({
                'all_ready': all_ready,
                'ready_count': ready_count,
                'total_count': total_count
            })
        return jsonify({'error': 'group where?'}, 404)

@app.route('/wait_for_next_task')
def wait_for_next_task():
    group_id = session.get('group_id')
    participant_id = session.get('participant_id')
    with group_data_lock:
        if group_id in group_data:
            current_task = group_data[group_id]["task_number"]
            session['task_number'] = current_task
            if current_task > 5:
                return render_template('complete.html')
            if participant_id in group_data[group_id]["participants"]:
                group_data[group_id]["participants"][participant_id]["ready_for_next_task"] = True
    total_count = 4
    ready_count = 0
    with group_data_lock:
        if group_id in group_data:
            ready_count = count_ready_participants(group_id, "ready_for_next_task")
            total_count = len(group_data[group_id]["participants"])
    return render_template(
        'wait_for_next_task.html',
        task_number=session.get('task_number', 1),
        ready_count=ready_count,
        total_count=total_count
    )

@app.route('/proxy', methods=['GET', 'POST'])
def proxy():
    group_id = session.get('group_id')
    participant_id = session.get('participant_id')
    with group_data_lock:
        if group_id in group_data:
            session['task_number'] = group_data[group_id]["task_number"]
            if group_data[group_id]["task_number"] > 5:
                return render_template('complete.html')
    if request.method == 'POST':
        with group_data_lock:
            if group_id in group_data and participant_id in group_data[group_id]["participants"]:
                group_data[group_id]["participants"][participant_id]["ready_for_experiment"] = True
        session['start_time'] = time.time()
        return redirect(url_for('wait_for_experiment'))
    return render_template('proxy.html', task_number=session.get('task_number', 1))

@app.route('/wait_for_experiment')
def wait_for_experiment():
    group_id = session.get('group_id')
    participant_id = session.get('participant_id')
    with group_data_lock:
        if group_id in group_data and participant_id in group_data[group_id]["participants"]:
            group_data[group_id]["participants"][participant_id]["ready_for_experiment"] = True
    total_count = 4
    ready_count = 0
    with group_data_lock:
        if group_id in group_data:
            ready_count = count_ready_participants(group_id, "ready_for_experiment")
            total_count = len(group_data[group_id]["participants"])
    return render_template(
        'wait_for_experiment.html',
        task_number=session.get('task_number', 1),
        ready_count=ready_count,
        total_count=total_count
    )

@app.route('/check_all_ready_for_experiment')
def check_all_ready_for_experiment():
    group_id = session.get('group_id')
    with group_data_lock:
        if group_id in group_data:
            all_ready = all_participants_ready_for(group_id, "ready_for_experiment")
            ready_count = count_ready_participants(group_id, "ready_for_experiment")
            total_count = len(group_data[group_id]["participants"])
            return jsonify({
                'all_ready': all_ready,
                'ready_count': ready_count,
                'total_count': total_count
            })
        return jsonify({'error': 'Group not found'}), 404

@app.route('/experiment')
def experiment():
    if 'task_number' not in session or 'group_id' not in session:
        return redirect(url_for('index'))
    group_id = session.get('group_id')
    with group_data_lock:
        if group_id in group_data:
            session['task_number'] = group_data[group_id]["task_number"]
    participant_id = session.get('participant_id')
    task_number = session.get('task_number', 1)
    image_path = '/static/dream.jpeg' 
    participant_num = int(participant_id)
    if participant_num == 1:
        image_path = f'/lego_images/task_{task_number}/back.png'
    elif participant_num == 2:
        image_path = f'/lego_images/task_{task_number}/front.png'
    elif participant_num == 3:
        image_path = f'/lego_images/task_{task_number}/left.png'
    elif participant_num == 4:
        image_path = f'/lego_images/task_{task_number}/right.png'
    return render_template('experiment.html', task_number=task_number, image_path=image_path)

@app.route('/wait_for_report')
def wait_for_report():
    if 'group_id' not in session or 'participant_id' not in session:
        return redirect(url_for('index'))
    group_id = session.get('group_id')
    participant_id = session.get('participant_id')
    with group_data_lock:
        if group_id in group_data and participant_id in group_data[group_id]["participants"]:
            group_data[group_id]["participants"][participant_id]["ready_for_report"] = True
    total_count = 4
    ready_count = 0
    with group_data_lock:
        if group_id in group_data:
            ready_count = count_ready_participants(group_id, "ready_for_report")
            total_count = len(group_data[group_id]["participants"])
    return render_template(
        'wait_for_report.html',
        task_number=session.get('task_number', 1),
        ready_count=ready_count,
        total_count=total_count
    )

@app.route('/finish', methods=['POST'])
def finish():
    if 'task_number' not in session or 'group_id' not in session:
        return redirect(url_for('index'))
    session['finish_time'] = time.time()
    group_id = session.get('group_id')
    participant_id = session.get('participant_id')
    with group_data_lock:
        if group_id in group_data:
            if participant_id in group_data[group_id]["participants"]:
                group_data[group_id]["participants"][participant_id]["ready_for_report"] = True
            session['task_number'] = group_data[group_id]["task_number"]
    return redirect(url_for('wait_for_report'))

@app.route('/check_all_ready_for_report')
def check_all_ready_for_report(): #ajax
    group_id = session.get('group_id')
    with group_data_lock:
        if group_id in group_data:
            all_ready = all_participants_ready_for(group_id, "ready_for_report")
            ready_count = count_ready_participants(group_id, "ready_for_report")
            total_count = len(group_data[group_id]["participants"])
            return jsonify({
                'all_ready': all_ready,
                'ready_count': ready_count,
                'total_count': total_count
            })
        return jsonify({'error': 'group where?'}, 404)

@app.route('/report')
def report():
    if 'task_number' not in session or 'group_id' not in session:
        return redirect(url_for('index'))
    # group_id = session.get('group_id')
    participant_id = session.get('participant_id')
    task_number = session.get('task_number')
    image_path = '/static/dream.jpeg'
    participant_num = int(participant_id)
    if participant_num == 1:
        image_path = f'/lego_images/task_{task_number}/back.png'
    elif participant_num == 2:
        image_path = f'/lego_images/task_{task_number}/front.png'
    elif participant_num == 3:
        image_path = f'/lego_images/task_{task_number}/left.png'
    elif participant_num == 4:
        image_path = f'/lego_images/task_{task_number}/right.png'
    return render_template('report.html', task_number=task_number, image_path=image_path)

@app.route('/submit', methods=['POST'])
def submit():
    group_id = session.get('group_id')
    participant_id = session.get('participant_id')
    experiment_type = session.get('experiment_type')
    current_task = session.get('task_number')
    errors = request.form['errors']
    start_time = session.get('start_time')
    finish_time = session.get('finish_time')
    duration = finish_time - start_time
    report = {'group_id': group_id, 'participant_id': participant_id, \
              'experiment_type': experiment_type, 'task': current_task, 'errors': errors, 'duration': duration}
    with open(f'participant_{participant_id}_task_{current_task}_report.json', 'w') as f:
        json.dump(report, f)
    with group_data_lock:
        if group_id in group_data:
            if current_task == group_data[group_id]["task_number"]:
                if participant_id in group_data[group_id]["participants"]:
                    while len(group_data[group_id]["participants"][participant_id]["reports"]) < current_task:
                        group_data[group_id]["participants"][participant_id]["reports"].append(None)
                    if len(group_data[group_id]["participants"][participant_id]["reports"]) >= current_task:
                        group_data[group_id]["participants"][participant_id]["reports"][current_task - 1] = report
                    else:
                        group_data[group_id]["participants"][participant_id]["reports"].append(report)
                if participant_id in group_data[group_id]["pending_members"]:
                    group_data[group_id]["pending_members"].remove(participant_id)
                if all_participants_completed(group_id):
                    combined_report = process_group_task_completion(group_id)
                if participant_id in group_data[group_id]["participants"]:
                    group_data[group_id]["participants"][participant_id]["ready_for_next_task"] = False
    if os.path.exists('reports.json'):
        with open('reports.json', 'r') as f:
            data = json.load(f)
    else:
        data = []
    data.append(report)
    with open('reports.json', 'w') as f:
        json.dump(data, f)
    return redirect(url_for('wait_for_task_completion', task_number=current_task))

@app.route('/wait_for_task_completion/<int:task_number>')
def wait_for_task_completion(task_number):
    if 'task_number' not in session or 'group_id' not in session:
        return redirect(url_for('index'))
    group_id = session.get('group_id')
    participant_id = session.get('participant_id')
    current_group_task = 1
    with group_data_lock:
        if group_id in group_data:
            current_group_task = group_data[group_id]["task_number"]
            print(f"Group {group_id} current task: {current_group_task}, waiting for task: {task_number}")
    if current_group_task > task_number:
        with group_data_lock:
            if group_id in group_data and participant_id in group_data[group_id]["participants"]:
                group_data[group_id]["participants"][participant_id]["ready_for_next_task"] = True
            session['task_number'] = current_group_task
        return redirect(url_for('wait_for_next_task'))
    submissions_count = 0
    pending_participants = []
    total_count = 4
    with group_data_lock:
        if group_id in group_data:
            pending_participants = group_data[group_id]["pending_members"].copy()
            submissions_count = 4 - len(pending_participants)
            total_count = 4
    return render_template('wait_for_task_completion.html', task_number=task_number, submissions_count=submissions_count, total_count=total_count)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')