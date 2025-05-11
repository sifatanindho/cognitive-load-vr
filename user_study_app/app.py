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
group_data_lock = threading.Lock()

def clear_lego_images_directory():
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
            clear_lego_images_directory()
            try:
                decision_maker_main()
            except Exception as e:
                print(f"Error running decision_maker: {e}")

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
            print(f"Completed Task {task_number} Report: {combined_report}")
            try:
                run_study(combined_report)
                print(f"Successfully ran study for group {group_id}, task {task_number}")
            except Exception as e:
                print(f"Error running study for group {group_id}, task {task_number}: {e}")
            try:
                with open(f'group_{group_id}_task_{task_number}_report.json', 'w') as f:
                    json.dump(combined_report, f)
                print(f"Successfully saved group report for group {group_id}, task {task_number}")
            except Exception as e:
                print(f"Error saving combined report for group {group_id}, task {task_number}: {e}")
            old_task_number = task_number
            group["task_number"] += 1
            group["pending_members"] = ["1", "2", "3", "4"]
            reset_ready_states(group_id, "ready_for_experiment")
            reset_ready_states(group_id, "ready_for_report")
            reset_ready_states(group_id, "ready_for_next_task")
            print(f"Advanced group {group_id} from task {old_task_number} to task {group['task_number']}")
            return combined_report
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        group_id = request.form['group_id']
        participant_id = request.form['participant_id']
        experiment_type = request.form['experiment_type']
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

@app.route('/wait_for_next_task')
def wait_for_next_task():
    if 'group_id' not in session or 'participant_id' not in session:
        return redirect(url_for('index'))
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
    ready_count = 0
    total_count = 4
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

@app.route('/check_all_ready_for_next_task')
def check_all_ready_for_next_task():
    if 'group_id' not in session:
        return jsonify({'error': 'No group ID in session'}), 400
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
        return jsonify({'error': 'Group not found'}), 404

@app.route('/proxy', methods=['GET', 'POST'])
def proxy():
    if 'task_number' not in session or 'group_id' not in session:
        return redirect(url_for('index'))
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
    if 'group_id' not in session or 'participant_id' not in session:
        return redirect(url_for('index'))
    group_id = session.get('group_id')
    participant_id = session.get('participant_id')
    with group_data_lock:
        if group_id in group_data and participant_id in group_data[group_id]["participants"]:
            group_data[group_id]["participants"][participant_id]["ready_for_experiment"] = True
    ready_count = 0
    total_count = 4
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
    if 'group_id' not in session:
        return jsonify({'error': 'No group ID in session'}), 400
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

@app.route('/wait_for_report')
def wait_for_report():
    if 'group_id' not in session or 'participant_id' not in session:
        return redirect(url_for('index'))
    group_id = session.get('group_id')
    participant_id = session.get('participant_id')
    with group_data_lock:
        if group_id in group_data and participant_id in group_data[group_id]["participants"]:
            group_data[group_id]["participants"][participant_id]["ready_for_report"] = True
    ready_count = 0
    total_count = 4
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

@app.route('/check_all_ready_for_report')
def check_all_ready_for_report():
    """AJAX endpoint to check if all participants are ready for the report"""
    if 'group_id' not in session:
        return jsonify({'error': 'No group ID in session'}), 400
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
        return jsonify({'error': 'Group not found'}), 404

@app.route('/report')
def report():
    if 'task_number' not in session or 'group_id' not in session:
        return redirect(url_for('index'))
    group_id = session.get('group_id')
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
    if 'task_number' not in session or 'group_id' not in session:
        return redirect(url_for('index'))
    group_id = session.get('group_id')
    participant_id = session.get('participant_id')
    experiment_type = session.get('experiment_type')
    current_task = session.get('task_number')
    errors = request.form['errors']
    start_time = session.get('start_time')
    finish_time = session.get('finish_time')
    duration = finish_time - start_time
    report = {'group_id': group_id, 'participant_id': participant_id, 'experiment_type': experiment_type, 'task': current_task, 'errors': errors, 'duration': duration}
    with open(f'participant_{participant_id}_task_{current_task}_report.json', 'w') as f:
        json.dump(report, f)
    print(f"Participant {participant_id} submitted report for task {current_task}")
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
                    print(f"Removed participant {participant_id} from pending_members for task {current_task}")
                    print(f"Pending members for group {group_id}, task {current_task}: {group_data[group_id]['pending_members']}")
                if all_participants_completed(group_id):
                    print(f"All participants in group {group_id} have completed task {current_task}")
                    combined_report = process_group_task_completion(group_id)
                if participant_id in group_data[group_id]["participants"]:
                    group_data[group_id]["participants"][participant_id]["ready_for_next_task"] = False
    if os.path.exists('reports.json'):
        try:
            with open('reports.json', 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
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
    total_count = 4
    pending_members = []
    with group_data_lock:
        if group_id in group_data:
            pending_members = group_data[group_id]["pending_members"].copy()
            submissions_count = 4 - len(pending_members)
            total_count = 4
    print(f"Group {group_id}, task {task_number}: {submissions_count}/{total_count} reports submitted")
    print(f"Pending members: {pending_members}")
    return render_template('wait_for_task_completion.html', task_number=task_number, submissions_count=submissions_count, total_count=total_count)

@app.route('/check_task_completion/<int:task_number>')
def check_task_completion(task_number):
    if 'group_id' not in session:
        return jsonify({'error': 'No group ID in session'}), 400
    group_id = session.get('group_id')
    with group_data_lock:
        if group_id in group_data:
            current_task = group_data[group_id]["task_number"]
            task_completed = current_task > task_number
            pending_members = group_data[group_id]["pending_members"]
            submissions_count = 4 - len(pending_members)
            if task_number < current_task:
                submissions_count = 4
            total_count = 4
            print(f"check_task_completion: Group {group_id}, task {task_number}")
            print(f"  Current task: {current_task}, Task completed: {task_completed}")
            print(f"  Submissions: {submissions_count}/{total_count}")
            print(f"  Pending members: {pending_members}")
            return jsonify({
                'task_completed': task_completed,
                'current_task': current_task,
                'submissions_count': submissions_count,
                'total_count': total_count,
                'pending_members': pending_members
            })
        return jsonify({'error': 'Group not found'}), 404
@app.route('/group_status/<group_id>')
def group_status(group_id):
    with group_data_lock:
        if group_id in group_data:
            return jsonify({
                'task_number': group_data[group_id]["task_number"],
                'pending_members': group_data[group_id]["pending_members"],
                'completed_tasks': len(group_data[group_id]["completed_tasks"]),
                'participant_count': sum(1 for p_id, p_data in group_data[group_id]["participants"].items() 
                                       if len(p_data["reports"]) > 0),
                'ready_for_experiment': {
                    'count': count_ready_participants(group_id, "ready_for_experiment"),
                    'total': len(group_data[group_id]["participants"])
                },
                'ready_for_report': {
                    'count': count_ready_participants(group_id, "ready_for_report"),
                    'total': len(group_data[group_id]["participants"])
                },
                'ready_for_next_task': {
                    'count': count_ready_participants(group_id, "ready_for_next_task"),
                    'total': len(group_data[group_id]["participants"])
                }
            })
        else:
            return jsonify({'error': 'Group not found'}), 404
        
@app.route('/debug')
def debug():
    debug_info = {
        'lego_images_dir_exists': os.path.exists(LEGO_IMAGES_DIR),
        'lego_images_dir_path': LEGO_IMAGES_DIR,
        'lego_images_dir_readable': os.access(LEGO_IMAGES_DIR, os.R_OK),
        'lego_images_dir_writable': os.access(LEGO_IMAGES_DIR, os.W_OK),
        'current_working_dir': os.getcwd(),
        'app_dir': os.path.dirname(os.path.abspath(__file__)),
        'group_data': {k: {
            'task_number': v['task_number'],
            'pending_members': v['pending_members'],
            'completed_tasks_count': len(v['completed_tasks']),
            'participants_count': len(v['participants']),
            'ready_states': {
                'ready_for_experiment': count_ready_participants(k, "ready_for_experiment"),
                'ready_for_report': count_ready_participants(k, "ready_for_report"),
                'ready_for_next_task': count_ready_participants(k, "ready_for_next_task")
            }
        } for k, v in group_data.items()}
    }
    debug_info['task_dirs'] = {}
    for i in range(1, 6):
        task_dir = os.path.join(LEGO_IMAGES_DIR, f'task_{i}')
        debug_info['task_dirs'][f'task_{i}'] = {
            'exists': os.path.exists(task_dir),
            'readable': os.access(task_dir, os.R_OK) if os.path.exists(task_dir) else False
        }
    return debug_info

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')