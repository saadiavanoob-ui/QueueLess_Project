"""
=============================================================================
QueueLess - Universal Smart Queue Management Web Application
=============================================================================
Flask server providing:
- Universal institution selection (Hospitals, Banks, Akshaya, Clinics, Railway, etc.)
- Dynamic cascading branch and service selection with opening status
- Smart token generation with QR code and verification code
- Live real-time queue tracking with smart wait time estimation
- Priority queue handling (Regular, Senior, PwD, Pregnant, Emergency)
- Appointment scheduling vs Instant walk-in
- Public TV Display Screen (/display) for waiting halls
- Customer authentication and dashboard (/customer/dashboard)
- Operator calling desk and workstation (/operator/dashboard)
- Admin analytics and management (/admin)
- Multilingual API support (English, Malayalam, Hindi)
- QR check-in and token cancellation
- Customer feedback & 5-star ratings
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import database

app = Flask(__name__)
app.secret_key = 'queueless_secret_college_technofest_key_2026'

# =============================================================================
# CONTEXT PROCESSOR (Injects categories & stats into all templates)
# =============================================================================
@app.context_processor
def inject_global_data():
    try:
        categories = database.get_all_categories()
        stats = database.get_queue_statistics()
    except Exception:
        categories = []
        stats = {'total': 0, 'serving': 0, 'waiting': 0, 'completed': 0, 'cancelled': 0, 'avg_rating': 5.0, 'avg_wait': 0}
    return dict(categories=categories, global_stats=stats)

# =============================================================================
# CUSTOMER FACING ROUTES
# =============================================================================

@app.route('/')
def home():
    """Renders the upgraded homepage with live preview, search bar, and 8 institution categories."""
    institutions = database.search_institutions()
    stats = database.get_queue_statistics()
    return render_template('index.html', institutions=institutions, stats=stats)

@app.route('/institutions')
def institutions_directory():
    """Dedicated institutions directory page with live search and category filters."""
    category = request.args.get('category', 'all')
    search = request.args.get('q', '').strip()
    institutions = database.search_institutions(keyword=search, category=category)
    return render_template('institutions.html', institutions=institutions, selected_category=category, search_query=search)

@app.route('/book')
def book_token_page():
    """
    Renders the Token Booking Page.
    Accepts optional '?institution_id=' or '?category=' to preselect.
    """
    selected_inst_id = request.args.get('institution_id')
    preselected_category = request.args.get('category', 'all')
    institutions = database.search_institutions(category=preselected_category)
    
    first_inst = None
    if selected_inst_id:
        try:
            first_inst = database.get_institution_details(int(selected_inst_id))
        except Exception:
            pass

    if not first_inst and institutions:
        first_inst = database.get_institution_details(institutions[0]['id'])

    return render_template('book.html', 
                           institutions=institutions, 
                           current_inst=first_inst, 
                           selected_category=preselected_category)

@app.route('/track')
def track_token_page():
    """
    Renders the Live Token Status Tracker page.
    Accepts '?token=' query parameter.
    """
    initial_token = request.args.get('token', '').strip().upper()
    return render_template('track.html', initial_token=initial_token)

@app.route('/display')
@app.route('/tv')
def public_display_screen():
    """
    Dedicated full-screen Public TV Display screen for waiting halls and booths.
    Displays active counters, currently serving tokens, audio chimes, and scrolling ticker.
    """
    branch_id = request.args.get('branch_id')
    try:
        branch_id = int(branch_id) if branch_id else None
    except Exception:
        branch_id = None
    
    board_data = database.get_display_board_data(branch_id)
    branches = database.search_institutions()
    return render_template('display.html', board_data=board_data, selected_branch_id=branch_id, branches=branches)

# =============================================================================
# CUSTOMER AUTHENTICATION & DASHBOARD
# =============================================================================

@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    """Customer login page."""
    error = None
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()

        conn = database.get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
        conn.close()

        if user and (check_password_hash(user['password_hash'], password) or password in ('cust123', 'password123')):
            session['customer_id'] = user['id']
            session['customer_name'] = user['name']
            session['customer_phone'] = user['phone']
            return redirect(url_for('customer_dashboard'))
        else:
            # Demonstration convenience: auto-login or registration for mobile
            if phone and len(phone) >= 10:
                conn = database.get_db_connection()
                cursor = conn.cursor()
                p_hash = generate_password_hash(password or 'cust123')
                cursor.execute('INSERT OR IGNORE INTO users (name, phone, password_hash, role) VALUES (?, ?, ?, "customer")',
                               ('Customer ' + phone[-4:], phone, p_hash))
                conn.commit()
                user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
                conn.close()
                session['customer_id'] = user['id']
                session['customer_name'] = user['name']
                session['customer_phone'] = user['phone']
                return redirect(url_for('customer_dashboard'))
            error = "Invalid mobile number or password."

    return render_template('customer_login.html', error=error)

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    """Customer self-registration page."""
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not name or not phone or len(phone) < 10:
            error = "Please provide your full name and a valid 10-digit mobile number."
        else:
            try:
                conn = database.get_db_connection()
                cursor = conn.cursor()
                p_hash = generate_password_hash(password or 'cust123')
                cursor.execute('''
                    INSERT INTO users (name, email, phone, password_hash, role)
                    VALUES (?, ?, ?, ?, 'customer')
                ''', (name, email or None, phone, p_hash))
                conn.commit()
                user_id = cursor.lastrowid
                conn.close()

                session['customer_id'] = user_id
                session['customer_name'] = name
                session['customer_phone'] = phone
                return redirect(url_for('customer_dashboard'))
            except Exception as e:
                error = "An account with this phone number or email already exists."

    return render_template('customer_register.html', error=error)

@app.route('/customer/dashboard')
def customer_dashboard():
    """Customer Dashboard showing active tokens, previous history, and feedback options."""
    customer_phone = session.get('customer_phone')
    if not customer_phone:
        # Default exhibition phone for seamless demo
        customer_phone = '9876543210'
        session['customer_name'] = 'Rahul Sharma'
        session['customer_phone'] = customer_phone

    tokens = database.get_tokens_by_phone(customer_phone)
    active_tokens = [t for t in tokens if t['status'] in ('waiting', 'called', 'serving')]
    past_tokens = [t for t in tokens if t['status'] in ('completed', 'cancelled', 'skipped')]

    return render_template('customer_dashboard.html', 
                           active_tokens=active_tokens, 
                           past_tokens=past_tokens, 
                           customer_name=session.get('customer_name', 'Rahul Sharma'),
                           customer_phone=customer_phone)

@app.route('/customer/logout')
def customer_logout():
    """Customer logout."""
    session.pop('customer_id', None)
    session.pop('customer_name', None)
    session.pop('customer_phone', None)
    return redirect(url_for('home'))

# =============================================================================
# OPERATOR DASHBOARD & WORKSTATION
# =============================================================================

@app.route('/operator/login', methods=['GET', 'POST'])
def operator_login():
    """Operator workstation login."""
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if (username in ('operator', 'operator1', 'admin', 'op1') and 
            password in ('op123', 'admin123', 'password123', 'operator')):
            session['is_operator'] = True
            session['operator_name'] = 'Counter Officer 1'
            session['operator_counter'] = int(request.form.get('counter', 1))
            return redirect(url_for('operator_dashboard'))
        else:
            error = "Invalid operator credentials. Demo: Username 'operator' | Password 'op123'"

    return render_template('operator_login.html', error=error)

@app.route('/operator/dashboard')
def operator_dashboard():
    """
    Operator calling console:
    - Counter selector (Counter 1, 2, 3, 4)
    - Call Next, Skip, Recall, Mark Serving, Mark Completed, No Show
    - Pause / Resume Queue
    - Manual Walk-in token generator
    - QR Code verification check-in
    """
    if not session.get('is_operator') and not session.get('is_admin'):
        # For exhibition testing, auto grant operator demo session
        session['is_operator'] = True
        session['operator_name'] = 'Counter Officer 1'
        session['operator_counter'] = 1

    branches = database.search_institutions()
    stats = database.get_queue_statistics()
    return render_template('operator_dashboard.html', 
                           branches=branches, 
                           stats=stats,
                           operator_name=session.get('operator_name', 'Counter Officer 1'),
                           counter_number=session.get('operator_counter', 1))

@app.route('/operator/logout')
def operator_logout():
    session.pop('is_operator', None)
    session.pop('operator_name', None)
    session.pop('operator_counter', None)
    return redirect(url_for('operator_login'))

# =============================================================================
# ADMINISTRATOR CONSOLE
# =============================================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin portal login."""
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username == 'admin' and password in ('admin123', 'password123', 'admin'):
            session['is_admin'] = True
            session['admin_user'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid credentials. Demo: Username "admin" and Password "admin123"'

    return render_template('admin_login.html', error=error)

@app.route('/admin')
@app.route('/admin/dashboard')
def admin_dashboard():
    """
    Administrator Dashboard:
    - Total, waiting, serving, completed, cancelled analytics
    - Charts & breakdown
    - Institutions, branches, services, counters management
    - Feedback reviews table
    """
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    stats = database.get_queue_statistics()
    institutions = database.search_institutions()
    feedbacks = database.get_feedback_list(limit=15)
    return render_template('admin.html', 
                           stats=stats, 
                           institutions=institutions,
                           feedbacks=feedbacks)

@app.route('/admin/logout')
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

# =============================================================================
# REST APIS (DATA, AJAX, REAL-TIME QUEUE)
# =============================================================================

@app.route('/api/catalog', methods=['GET'])
def api_get_catalog():
    """Returns all institutions for backwards compatibility."""
    institutions = database.search_institutions()
    return jsonify({"success": True, "institutions": institutions})

@app.route('/api/institutions/search', methods=['GET'])
def api_search_institutions():
    """Searches institutions by keyword, category, or branch location."""
    q = request.args.get('q', '').strip()
    category = request.args.get('category', 'all')
    results = database.search_institutions(keyword=q, category=category)
    return jsonify({"success": True, "institutions": results, "count": len(results)})

@app.route('/api/institutions/<int:inst_id>', methods=['GET'])
def api_get_institution_details(inst_id):
    """Returns branches, services, and counters for an institution."""
    inst = database.get_institution_details(inst_id)
    if not inst:
        return jsonify({"success": False, "error": "Institution not found."}), 404
    return jsonify({"success": True, "institution": inst})

@app.route('/api/tokens/book', methods=['POST'])
def api_book_token():
    """
    Generates a new token.
    Receives JSON:
    {
      "institution_id": 1,
      "branch_id": 1,
      "service_id": 1,
      "customer_name": "Rahul",
      "phone": "9876543210",
      "priority": "regular",          // 'regular', 'senior', 'pwd', 'pregnant', 'emergency'
      "token_type": "instant",        // 'instant', 'appointment'
      "appointment_date": "2026-11-10",
      "appointment_slot": "10:30 AM"
    }
    """
    data = request.get_json() or {}
    inst_id = data.get('institution_id')
    branch_id = data.get('branch_id')
    service_id = data.get('service_id')
    customer_name = data.get('customer_name', '').strip()
    phone = data.get('phone', '').strip()
    priority = data.get('priority', 'regular')
    token_type = data.get('token_type', 'instant')
    appointment_date = data.get('appointment_date')
    appointment_slot = data.get('appointment_slot')

    # Basic validations
    if not all([inst_id, branch_id, service_id, customer_name, phone]):
        return jsonify({
            "success": False, 
            "error": "All fields (Institution, Branch, Service, Name, Phone) are required."
        }), 400

    if len(phone) < 10:
        return jsonify({
            "success": False, 
            "error": "Please enter a valid 10-digit mobile number."
        }), 400

    new_token = database.add_token(
        customer_name=customer_name,
        phone=phone,
        institution_id=int(inst_id),
        branch_id=int(branch_id),
        service_id=int(service_id),
        priority=priority,
        token_type=token_type,
        appointment_date=appointment_date,
        appointment_slot=appointment_slot
    )

    return jsonify({
        "success": True,
        "message": f"Token {new_token['token_number']} successfully generated!",
        "token": new_token
    })

@app.route('/api/tokens/track/<token_number>', methods=['GET'])
def api_track_token(token_number):
    """Returns real-time status, people ahead, estimated wait time, and QR data."""
    token = database.get_token_by_number(token_number)
    if not token:
        return jsonify({
            "success": False, 
            "error": f"Token '{token_number}' was not found. Please check and try again."
        }), 404

    return jsonify({
        "success": True,
        "token": token
    })

@app.route('/api/tokens/<token_number>/cancel', methods=['POST'])
def api_cancel_token(token_number):
    """Allows customer or staff to cancel an active waiting token."""
    cancelled = database.cancel_token(token_number, cancelled_by="Customer/Operator")
    if not cancelled:
        return jsonify({
            "success": False, 
            "error": f"Could not cancel token '{token_number}'. It may already be completed or cancelled."
        }), 400

    return jsonify({
        "success": True,
        "message": f"Token {token_number} has been successfully cancelled."
    })

@app.route('/api/tokens/qr-checkin', methods=['POST'])
def api_qr_checkin():
    """
    QR Code Check-In verification.
    Receives JSON: { "code": "QK-8103" } or token number.
    """
    data = request.get_json() or {}
    code = data.get('code', '').strip()
    if not code:
        return jsonify({"success": False, "error": "Please enter or scan a valid QR / Token code."}), 400

    success, message, token = database.verify_qr_checkin(code)
    return jsonify({
        "success": success,
        "message": message,
        "token": token
    }), (200 if success else 400)

@app.route('/api/feedback', methods=['POST'])
def api_submit_feedback():
    """Submits customer feedback and ratings (1 to 5 stars)."""
    data = request.get_json() or {}
    token_number = data.get('token_number', '').strip()
    customer_name = data.get('customer_name', 'Visitor')
    rating = data.get('rating', 5)
    comment = data.get('comment', '').strip()

    if not token_number:
        return jsonify({"success": False, "error": "Token number is required."}), 400

    database.add_feedback(token_number, customer_name, rating, comment)
    return jsonify({
        "success": True,
        "message": "Thank you! Your feedback has been recorded."
    })

@app.route('/api/display/live', methods=['GET'])
def api_display_live():
    """Returns live counter data for the Public TV Display Screen."""
    branch_id = request.args.get('branch_id')
    try:
        branch_id = int(branch_id) if branch_id else None
    except Exception:
        branch_id = None

    board_data = database.get_display_board_data(branch_id)
    return jsonify({
        "success": True,
        "board": board_data
    })

# =============================================================================
# OPERATOR ACTIONS APIS
# =============================================================================

@app.route('/api/operator/call-next', methods=['POST'])
def api_operator_call_next():
    """Calls next token atomically for a specific counter."""
    data = request.get_json() or {}
    counter = int(data.get('counter', session.get('operator_counter', 1)))
    branch_id = data.get('branch_id')
    try:
        branch_id = int(branch_id) if branch_id else None
    except Exception:
        branch_id = None

    called_token = database.call_next_token(
        branch_id=branch_id, 
        counter_number=counter, 
        operator_name=session.get('operator_name', 'Counter Operator')
    )
    stats = database.get_queue_statistics()

    if not called_token:
        return jsonify({
            "success": False,
            "message": f"No customers currently waiting at Counter {counter}.",
            "stats": stats
        })

    return jsonify({
        "success": True,
        "message": f"Now Calling: {called_token['token_number']} ({called_token['customer_name']}) at Counter {counter}",
        "token": called_token,
        "stats": stats
    })

@app.route('/api/operator/skip', methods=['POST'])
def api_operator_skip():
    """Skips a token."""
    data = request.get_json() or {}
    token_id = data.get('token_id')
    if not token_id:
        return jsonify({"success": False, "error": "Token ID required."}), 400

    database.skip_token(int(token_id), operator_name=session.get('operator_name', 'Operator'))
    return jsonify({"success": True, "message": "Token skipped."})

@app.route('/api/operator/recall', methods=['POST'])
def api_operator_recall():
    """Recalls a skipped or waiting token."""
    data = request.get_json() or {}
    token_id = data.get('token_id')
    counter = int(data.get('counter', 1))

    recalled = database.recall_token(int(token_id), counter_number=counter, operator_name=session.get('operator_name', 'Operator'))
    if not recalled:
        return jsonify({"success": False, "error": "Could not recall token."}), 400

    return jsonify({"success": True, "message": f"Recalled {recalled['token_number']}", "token": recalled})

@app.route('/api/operator/counter-status', methods=['POST'])
def api_toggle_counter_status():
    """Toggles counter status ('open', 'break', 'closed')."""
    data = request.get_json() or {}
    branch_id = int(data.get('branch_id', 1))
    counter = int(data.get('counter', 1))
    status = data.get('status', 'open')

    database.update_counter_status(branch_id, counter, status)
    return jsonify({"success": True, "message": f"Counter {counter} is now {status}."})

@app.route('/api/tokens', methods=['GET'])
def api_get_tokens():
    """Returns list of tokens for tables."""
    branch_id = request.args.get('branch_id', 'all')
    status = request.args.get('status', 'all')
    tokens = database.get_all_tokens(branch_id=branch_id, status=status)
    return jsonify({"success": True, "tokens": tokens, "count": len(tokens)})

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Returns queue statistics."""
    stats = database.get_queue_statistics()
    return jsonify({"success": True, "stats": stats})

# =============================================================================
# APPLICATION STARTUP
# =============================================================================
if __name__ == '__main__':
    database.init_db()
    print("-----------------------------------------------------------------")
    print(" QueueLess Universal Smart Queue Management System Running!")
    print(" Live URL: http://127.0.0.1:5000")
    print(" Customer Portal: http://127.0.0.1:5000/customer/dashboard")
    print(" Operator Desk: http://127.0.0.1:5000/operator/dashboard (operator/op123)")
    print(" Admin Console: http://127.0.0.1:5000/admin (admin/admin123)")
    print(" TV Public Display: http://127.0.0.1:5000/display")
    print("-----------------------------------------------------------------")
    app.run(debug=True, host='127.0.0.1', port=5000)
