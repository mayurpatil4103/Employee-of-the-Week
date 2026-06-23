from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, timedelta
import json, os, uuid
from functools import wraps

app = Flask(__name__)
app.secret_key = 'eotw_secret_key_change_in_production'

DB_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

def load():
    if not os.path.exists(DB_FILE):
        return {"employees": [], "votes": [], "winner": None, "manager": {"username": "admin", "password": "admin123"}}
    with open(DB_FILE) as f:
        data = json.load(f)
    if "manager" not in data:
        data["manager"] = {"username": "admin", "password": "admin123"}
    return data

def save(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def current_week():
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return f"{monday.strftime('%d %b')} – {sunday.strftime('%d %b %Y')}"

def current_week_key():
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return monday.strftime('%Y-%W')

def manager_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('manager'):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# ─── PUBLIC ROUTES ───
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/public/data')
def public_data():
    data = load()
    wk = current_week_key()
    voted_ids = [v['voter_emp_id'] for v in data['votes'] if v.get('week_key') == wk]
    return jsonify({
        "employees": data['employees'],
        "week": current_week(),
        "week_key": wk,
        "voted_ids": voted_ids
    })

@app.route('/api/vote', methods=['POST'])
def submit_vote():
    body = request.json
    voter_emp_id = body.get('voter_emp_id')
    nominee_emp_id = body.get('nominee_emp_id')
    reason = body.get('reason', '').strip()

    if not voter_emp_id or not nominee_emp_id or not reason:
        return jsonify({"error": "All fields are required"}), 400

    data = load()
    wk = current_week_key()

    voter = next((e for e in data['employees'] if e['id'] == voter_emp_id), None)
    nominee = next((e for e in data['employees'] if e['id'] == nominee_emp_id), None)

    if not voter:
        return jsonify({"error": "Voter not found"}), 404
    if not nominee:
        return jsonify({"error": "Nominee not found"}), 404

    if any(v for v in data['votes'] if v['voter_emp_id'] == voter_emp_id and v.get('week_key') == wk):
        return jsonify({"error": "already_voted"}), 400

    vote = {
        "id": str(uuid.uuid4()),
        "voter_emp_id": voter_emp_id,
        "voter_name": voter['name'],
        "voter_designation": voter['designation'],
        "voter_department": voter.get('department', ''),
        "nominee_emp_id": nominee_emp_id,
        "nominee_name": nominee['name'],
        "nominee_designation": nominee['designation'],
        "reason": reason,
        "submitted_at": datetime.now().strftime('%d %b %Y, %I:%M %p'),
        "week_key": wk,
        "week_label": current_week()
    }
    data['votes'].append(vote)
    save(data)
    return jsonify({"success": True, "voter_name": voter['name'], "nominee_name": nominee['name']})

# ─── MANAGER AUTH ───
@app.route('/api/manager/login', methods=['POST'])
def manager_login():
    body = request.json
    data = load()
    mgr = data.get('manager', {})
    if body.get('username') == mgr.get('username') and body.get('password') == mgr.get('password'):
        session['manager'] = True
        return jsonify({"success": True})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/manager/logout', methods=['POST'])
def manager_logout():
    session.pop('manager', None)
    return jsonify({"success": True})

@app.route('/api/manager/change-password', methods=['POST'])
@manager_required
def change_password():
    body = request.json
    new_username = body.get('username', '').strip()
    new_password = body.get('password', '').strip()
    if not new_username or not new_password:
        return jsonify({"error": "Username and password required"}), 400
    data = load()
    data['manager'] = {"username": new_username, "password": new_password}
    save(data)
    return jsonify({"success": True})

# ─── MANAGER DASHBOARD ───
@app.route('/api/manager/dashboard')
@manager_required
def manager_dashboard():
    data = load()
    wk = current_week_key()
    votes = [v for v in data['votes'] if v.get('week_key') == wk]
    voted_emp_ids = set(v['voter_emp_id'] for v in votes)
    not_voted = [e for e in data['employees'] if e['id'] not in voted_emp_ids]

    # tally votes per nominee
    tally = {}
    for v in votes:
        nid = v['nominee_emp_id']
        if nid not in tally:
            nom = next((e for e in data['employees'] if e['id'] == nid), None)
            tally[nid] = {"emp_id": nid, "name": v['nominee_name'],
                          "designation": v['nominee_designation'],
                          "vote_count": 0, "votes_detail": []}
        tally[nid]['vote_count'] += 1
        tally[nid]['votes_detail'].append(v)

    nominees = sorted(tally.values(), key=lambda x: x['vote_count'], reverse=True)
    w = data.get('winner')
    winner = w if w and w.get('week_key') == wk else None

    return jsonify({
        "employees": data['employees'],
        "nominees": nominees,
        "votes": votes,
        "not_voted": not_voted,
        "winner": winner,
        "week": current_week(),
        "week_key": wk,
        "total_employees": len(data['employees']),
        "total_votes": len(votes),
        "total_not_voted": len(not_voted)
    })

# ─── EMPLOYEE MANAGEMENT ───
@app.route('/api/manager/employees', methods=['POST'])
@manager_required
def add_employee():
    body = request.json
    name = body.get('name', '').strip()
    designation = body.get('designation', '').strip()
    department = body.get('department', '').strip()
    if not name or not designation:
        return jsonify({"error": "Name and designation required"}), 400
    data = load()
    if any(e for e in data['employees'] if e['name'].lower() == name.lower()):
        return jsonify({"error": f"{name} already exists"}), 400
    emp = {"id": str(uuid.uuid4()), "name": name, "designation": designation,
           "department": department, "added_at": datetime.now().strftime('%d %b %Y')}
    data['employees'].append(emp)
    save(data)
    return jsonify({"success": True, "employee": emp})

@app.route('/api/manager/employees/<emp_id>', methods=['DELETE'])
@manager_required
def delete_employee(emp_id):
    data = load()
    data['employees'] = [e for e in data['employees'] if e['id'] != emp_id]
    save(data)
    return jsonify({"success": True})

# ─── WINNER ───
@app.route('/api/manager/winner', methods=['POST'])
@manager_required
def declare_winner():
    body = request.json
    emp_id = body.get('emp_id')
    data = load()
    wk = current_week_key()
    emp = next((e for e in data['employees'] if e['id'] == emp_id), None)
    if not emp:
        return jsonify({"error": "Employee not found"}), 404
    votes = [v for v in data['votes'] if v.get('nominee_emp_id') == emp_id and v.get('week_key') == wk]
    data['winner'] = {**emp, "id": emp_id, "vote_count": len(votes), "week_key": wk,
                  "week_label": current_week(),
                  "declared_at": datetime.now().strftime('%d %b %Y, %I:%M %p')}
    save(data)
    return jsonify({"success": True})

# ─── RESET WEEK ───
@app.route('/api/manager/reset', methods=['POST'])
@manager_required
def reset_week():
    data = load()
    wk = current_week_key()
    data['votes'] = [v for v in data['votes'] if v.get('week_key') != wk]
    data['winner'] = None
    save(data)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
