from flask import Flask, render_template, redirect, url_for, request, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # 🔐 Replace with env var in production

# 🔧 TEMPORARY IN-MEMORY STORAGE
talent_requests = []
submissions = []  # Each item = { request_id, recruiter, candidates }

# ---------- ROUTES ----------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signals')
def recruiter_signals():
    if session.get('user_type') != 'recruiter':
        return redirect(url_for('login_recruiter'))
    return render_template('recruiter_signals.html', talent_requests=talent_requests)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/login/hirer', methods=['GET', 'POST'])
def login_hirer():
    if request.method == 'POST':
        session['user_type'] = 'hirer'
        return redirect(url_for('dashboard_hirer'))
    return render_template('login_hirer.html')

@app.route('/sign-up')
def sign_up():
    return render_template('sign_up.html')

@app.route('/login/recruiter', methods=['GET', 'POST'])
def login_recruiter():
    if request.method == 'POST':
        session['user_type'] = 'recruiter'
        print("Login successful — user_type set to:", session['user_type'])
        return redirect(url_for('dashboard_recruiter'))
    return render_template('login_recruiter.html')

@app.route('/signup/recruiter', methods=['GET', 'POST'])
def recruiter_sign_up():
    return render_template('recruiter_signup.html')

@app.route('/dashboard/hirer')
def dashboard_hirer():
    if session.get('user_type') != 'hirer':
        return redirect(url_for('login_hirer'))
    return render_template('dashboard_hirer.html', talent_requests=talent_requests)

@app.route('/dashboard/recruiter')
def dashboard_recruiter():
    if session.get('user_type') != 'recruiter':
        return redirect(url_for('login_recruiter'))
    return render_template('dashboard_recruiter.html')


@app.route('/talent-request', methods=['GET', 'POST'])
def talent_request():
    if session.get('user_type') != 'hirer':
        return redirect(url_for('login_hirer'))

    if request.method == 'POST':
        new_request = {
            'id': len(talent_requests),  # Add this
            'role_title': request.form['role_title'],
            'skills': request.form['skills'],
            'location': request.form['location'],
            'salary_range': request.form['salary_range'],
            'num_openings': request.form['num_openings'],
            'notes': request.form['notes']
        }
        talent_requests.append(new_request)
        return redirect(url_for('dashboard_hirer'))

    return render_template('talent_request.html')

# ---------- RUN ----------

@app.route('/submit/<int:request_id>', methods=['GET', 'POST'])
def submit_candidate(request_id):
    if session.get('user_type') != 'recruiter':
        return redirect(url_for('login_recruiter'))

    # Load the correct talent request
    try:
        request_data = talent_requests[request_id]
    except IndexError:
        return "Request not found", 404

    if request.method == 'POST':
        candidates = []

        try:
            count = int(request.form.get('candidate_count', 0))
        except ValueError:
            count = 0

        for i in range(1, count + 1):
            first_name = request.form.get(f'first_name{i}')
            last_name = request.form.get(f'last_name{i}')
            email = request.form.get(f'email{i}')
            rtr = request.form.get(f'rtr{i}') == 'on'

            # Optional fields (not required for submission)
            prefix = request.form.get(f'prefix{i}')
            gender = request.form.get(f'gender{i}')
            location = request.form.get(f'location{i}')
            salary = request.form.get(f'salary{i}')
            relocate = request.form.get(f'relocate{i}')
            work_rights = request.form.get(f'work_rights{i}')

            # Skip if mandatory fields are missing
            if not first_name or not last_name or not email or not rtr:
                continue

            # Check for duplicates
            duplicate = any(
                s['request_id'] == request_id and
                any(c['email'].lower() == email.lower() for c in s['candidates'])
                for s in submissions
            )
            if duplicate:
                return f"Candidate {email} already submitted for this role.", 400

            candidates.append({
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'rtr': rtr,
                'prefix': prefix,
                'gender': gender,
                'location': location,
                'salary': salary,
                'relocate': relocate,
                'work_rights': work_rights
            })

        if candidates:
            submissions.append({
                'request_id': request_id,
                'recruiter': 'anonymous',  # Will change once user system is built
                'candidates': candidates,
                'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

        return redirect(url_for('recruiter_signals'))

    return render_template('submit_candidate.html', request_data=request_data, request_id=request_id)

@app.route('/submissions')
def recruiter_submissions():
    if session.get('user_type') != 'recruiter':
        return redirect(url_for('login_recruiter'))

    recruiter_subs = [s for s in submissions if s['recruiter'] == 'anonymous']

    return render_template('recruiter_submissions.html', submissions=recruiter_subs, talent_requests=talent_requests)


if __name__ == '__main__':
    app.run(debug=True)