from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # 🔐 Replace with env var in production

# 🔧 TEMPORARY IN-MEMORY STORAGE
talent_requests = []

# ---------- ROUTES ----------
@app.route('/')
def home():
    return render_template('index.html')

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

@app.route('/login/recruiter', methods=['GET', 'POST'])
def login_recruiter():
    if request.method == 'POST':
        session['user_type'] = 'recruiter'
        return redirect(url_for('dashboard_recruiter'))
    return render_template('login_recruiter.html')

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
if __name__ == '__main__':
    app.run(debug=True)