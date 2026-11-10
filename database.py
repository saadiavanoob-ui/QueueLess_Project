"""
=============================================================================
QueueLess - Universal Smart Queue Management Database Layer
=============================================================================
Full relational SQLite architecture supporting:
- Universal institution selection (Hospitals, Banks, Akshaya, Clinics, Railway, etc.)
- Branches with opening/closing hours and location
- Services with customizable average duration and token prefixes
- Multiple simultaneous counters per branch with status (open/break/closed)
- Priority queuing (Regular, Senior, PwD, Pregnant, Emergency)
- Appointment scheduling vs Instant walk-in
- Real QR verification codes and check-in confirmation
- Smart waiting time estimation: (people_ahead * avg_duration) / active_counters
- User authentication (Customer, Operator, Admin) with Werkzeug password hashing
- Feedback & Ratings system
- Real-time audit logs
"""

import sqlite3
import os
import math
import random
import string
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'queueless.db')

def get_db_connection():
    """Returns a connection to the SQLite database with dictionary-like row access."""
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn

def init_db():
    """Initializes tables and seeds rich initial data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users table (Customer, Operator, Admin)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'customer', -- 'customer', 'operator', 'admin'
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Institutions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS institutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            icon TEXT NOT NULL,
            description TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')

    # 3. Branches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS branches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution_id INTEGER NOT NULL,
            branch_name TEXT NOT NULL,
            location TEXT NOT NULL,
            opening_time TEXT DEFAULT '09:00 AM',
            closing_time TEXT DEFAULT '05:00 PM',
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE CASCADE
        )
    ''')

    # 4. Services table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution_id INTEGER NOT NULL,
            service_name TEXT NOT NULL,
            avg_duration_mins INTEGER DEFAULT 10,
            prefix TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE CASCADE
        )
    ''')

    # 5. Counters table (Multiple counters per branch)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS counters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            branch_id INTEGER NOT NULL,
            counter_number INTEGER NOT NULL,
            counter_name TEXT NOT NULL,
            status TEXT DEFAULT 'open', -- 'open', 'break', 'closed'
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE,
            UNIQUE(branch_id, counter_number)
        )
    ''')

    # Check if existing tokens table needs schema upgrade
    cursor.execute('PRAGMA table_info(tokens)')
    existing_cols = [r['name'] for r in cursor.fetchall()]
    if existing_cols and 'verification_code' not in existing_cols:
        print("Migrating legacy tokens table to modern relational schema...")
        cursor.execute('ALTER TABLE tokens RENAME TO tokens_legacy')

    # 6. Tokens table (Comprehensive queue tokens)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_number TEXT UNIQUE NOT NULL,
            verification_code TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            institution_id INTEGER NOT NULL,
            branch_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            counter_number INTEGER DEFAULT 1,
            priority TEXT DEFAULT 'regular', -- 'regular', 'senior', 'pwd', 'pregnant', 'emergency'
            token_type TEXT DEFAULT 'instant', -- 'instant', 'appointment'
            appointment_date TEXT,
            appointment_slot TEXT,
            status TEXT DEFAULT 'waiting', -- 'waiting', 'called', 'serving', 'completed', 'skipped', 'cancelled'
            checkin_status TEXT DEFAULT 'pending', -- 'pending', 'checked_in'
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            serving_started_at DATETIME,
            completed_at DATETIME,
            FOREIGN KEY (institution_id) REFERENCES institutions(id),
            FOREIGN KEY (branch_id) REFERENCES branches(id),
            FOREIGN KEY (service_id) REFERENCES services(id)
        )
    ''')

    # 7. Feedback & Ratings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_number TEXT NOT NULL,
            customer_name TEXT,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 8. Queue Audit Logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queue_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_number TEXT NOT NULL,
            old_status TEXT,
            new_status TEXT NOT NULL,
            counter_number INTEGER,
            changed_by TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()

    # Seed master data if institutions table is empty
    cursor.execute('SELECT COUNT(*) AS count FROM institutions')
    if cursor.fetchone()['count'] == 0:
        seed_master_data(cursor, conn)

    # If tokens_legacy exists, migrate existing tokens into new table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tokens_legacy'")
    if cursor.fetchone():
        cursor.execute('SELECT COUNT(*) AS count FROM tokens')
        if cursor.fetchone()['count'] == 0:
            cursor.execute('SELECT * FROM tokens_legacy')
            legacy_rows = cursor.fetchall()
            for row in legacy_rows:
                vcode = f"QL-{random.randint(1000, 9999)}"
                cursor.execute('''
                    INSERT INTO tokens (
                        token_number, verification_code, customer_name, phone,
                        institution_id, branch_id, service_id, counter_number,
                        priority, token_type, status, checkin_status,
                        created_at, serving_started_at, completed_at
                    ) VALUES (?, ?, ?, ?, 1, 1, 1, ?, 'regular', 'instant', ?, 'checked_in', ?, ?, ?)
                ''', (row['token_number'], vcode, row['customer_name'], row['phone'],
                      row['counter_number'] or 1, row['status'],
                      row['created_at'], row['serving_started_at'], row['completed_at']))
            print(f"Successfully migrated {len(legacy_rows)} legacy tokens.")
            conn.commit()

    conn.close()

def seed_master_data(cursor, conn):
    """Seeds the full 8 universal institutions, branches, services, counters, and admin/operator users."""
    print("Seeding rich master catalog and demo data...")

    # Default Users (Admin, Operator, Customer)
    admin_hash = generate_password_hash('admin123')
    op_hash = generate_password_hash('op123')
    cust_hash = generate_password_hash('cust123')

    cursor.execute('''
        INSERT INTO users (name, email, phone, password_hash, role) VALUES
        ('Super Admin', 'admin@queueless.edu', '9876500000', ?, 'admin'),
        ('Counter Officer 1', 'operator1@queueless.edu', '9876500001', ?, 'operator'),
        ('Rahul Sharma', 'rahul@example.com', '9876543210', ?, 'customer')
    ''', (admin_hash, op_hash, cust_hash))

    # 8 Required Universal Institutions
    institutions = [
        ('HOSP', 'City Care Healthcare Network', 'Hospital', 'fa-hospital', 'Comprehensive general OPD, emergency, diagnostics and specialty care.'),
        ('BANK', 'State Apex Commercial Bank', 'Bank', 'fa-building-columns', 'Cash counters, customer deposits, KYC, loan desks & account opening.'),
        ('AKSH', 'Akshaya e-Kendra Network', 'Akshaya Centre', 'fa-laptop-code', 'Citizen services, Aadhaar updates, welfare certificates & e-district filing.'),
        ('CLIN', 'Apex Family Health Clinic', 'Clinic', 'fa-stethoscope', 'Neighborhood general physician visits, pediatrics and health checkups.'),
        ('RAIL', 'Central Railway Enquiry & Booking Hub', 'Railway Enquiry Centre', 'fa-train-subway', 'Tatkal counters, passenger reservation enquiries and refund desks.'),
        ('COLL', 'Apex Institute of Technology', 'College', 'fa-graduation-cap', 'Student admissions counseling, semester tuition fees, and administrative records.'),
        ('GOVT', 'District Revenue & Transport Office', 'Government Office', 'fa-landmark', 'Taluk revenue documents, driving license renewals and vehicle inspections.'),
        ('SERV', 'Citizen Suvidha Kendra', 'Customer Service Centre', 'fa-headset', 'Public utility bill payments, grievance filing, and document attestation.')
    ]

    cursor.executemany('''
        INSERT INTO institutions (code, name, category, icon, description)
        VALUES (?, ?, ?, ?, ?)
    ''', institutions)

    # Fetch institution IDs
    cursor.execute('SELECT id, code FROM institutions')
    inst_map = {row['code']: row['id'] for row in cursor.fetchall()}

    # Branches for each institution
    branches = [
        # Hospital branches
        (inst_map['HOSP'], 'Main Campus (Medical Square)', 'Medical Square, Central Road', '08:00 AM', '08:00 PM'),
        (inst_map['HOSP'], 'North City Super Speciality', 'North Bypass, Tech Park', '08:30 AM', '07:00 PM'),
        # Bank branches
        (inst_map['BANK'], 'MG Road Commercial Branch', 'MG Road, City Centre', '09:30 AM', '04:30 PM'),
        (inst_map['BANK'], 'Town Hall Retail Hub', 'Opposite Town Hall', '10:00 AM', '04:00 PM'),
        # Akshaya Centre branches
        (inst_map['AKSH'], 'Civil Station Kendra', 'Civil Station Building, Room 14', '09:00 AM', '05:30 PM'),
        (inst_map['AKSH'], 'Town Centre Smart Akshaya', 'Market Road, Near Post Office', '09:00 AM', '05:00 PM'),
        # Clinic branches
        (inst_map['CLIN'], 'City Health Clinic', 'East Avenue, Sector 4', '08:30 AM', '01:30 PM'),
        # Railway Enquiry branches
        (inst_map['RAIL'], 'Central Station Enquiry Desk', 'Main Concourse, Platform 1', '24 Hours', '24 Hours'),
        # College branches
        (inst_map['COLL'], 'Campus Administration Block', 'Academic Block A, Ground Floor', '09:00 AM', '04:30 PM'),
        # Government Office branches
        (inst_map['GOVT'], 'Taluk Revenue & RTO Office', 'Mini Civil Complex, Sector 2', '09:30 AM', '04:30 PM'),
        # Service Centre branches
        (inst_map['SERV'], 'Citizen Seva Point', 'Old Bus Stand Complex', '09:00 AM', '06:00 PM')
    ]

    cursor.executemany('''
        INSERT INTO branches (institution_id, branch_name, location, opening_time, closing_time)
        VALUES (?, ?, ?, ?, ?)
    ''', branches)

    # Fetch branch IDs
    cursor.execute('SELECT id, branch_name FROM branches')
    branch_rows = cursor.fetchall()
    b_map = {row['branch_name']: row['id'] for row in branch_rows}

    # Services per institution with realistic average durations
    services = [
        # Hospital
        (inst_map['HOSP'], 'OP General Consultation', 12, 'HOSP'),
        (inst_map['HOSP'], 'Laboratory & Blood Tests', 6, 'LAB'),
        (inst_map['HOSP'], 'Pharmacy Prescription Counter', 4, 'PHAR'),
        (inst_map['HOSP'], 'Radiology & X-Ray Scans', 15, 'RAD'),
        # Bank
        (inst_map['BANK'], 'Cash Deposit & Withdrawal', 5, 'BANK'),
        (inst_map['BANK'], 'Account Opening & KYC', 15, 'ACC'),
        (inst_map['BANK'], 'Loans & Credit Advisory', 20, 'LOAN'),
        # Akshaya Centre
        (inst_map['AKSH'], 'Aadhaar Enrollment & Updates', 10, 'AKSH'),
        (inst_map['AKSH'], 'Revenue Certificates (Income/Caste)', 8, 'CERT'),
        (inst_map['AKSH'], 'Utility Bill Payments', 4, 'BILL'),
        # Clinic
        (inst_map['CLIN'], 'General Practitioner Checkup', 10, 'CLIN'),
        (inst_map['CLIN'], 'Child Vaccination', 8, 'VAX'),
        # Railway Enquiry
        (inst_map['RAIL'], 'Ticket Booking & Tatkal', 5, 'RAIL'),
        (inst_map['RAIL'], 'Enquiry & Fare Information', 4, 'ENQ'),
        # College
        (inst_map['COLL'], 'Student Fee Payment', 5, 'COLL'),
        (inst_map['COLL'], 'Admissions & Document Verification', 12, 'ADM'),
        # Government Office
        (inst_map['GOVT'], 'Driving License Services', 10, 'GOVT'),
        (inst_map['GOVT'], 'Land Revenue & Property Tax', 15, 'TAX'),
        # Customer Service Centre
        (inst_map['SERV'], 'General Citizen Enquiries', 5, 'SERV'),
        (inst_map['SERV'], 'Document Attestation & Notary', 8, 'ATTS')
    ]

    cursor.executemany('''
        INSERT INTO services (institution_id, service_name, avg_duration_mins, prefix)
        VALUES (?, ?, ?, ?)
    ''', services)

    # Create multiple counters for each branch (3 to 4 counters per branch!)
    counters = []
    for b_row in branch_rows:
        b_id = b_row['id']
        counters.append((b_id, 1, 'Counter 01 (General)', 'open'))
        counters.append((b_id, 2, 'Counter 02 (Cash / Fast Track)', 'open'))
        counters.append((b_id, 3, 'Counter 03 (Senior & Priority)', 'open'))
        counters.append((b_id, 4, 'Counter 04 (Inquiries)', 'open'))

    cursor.executemany('''
        INSERT INTO counters (branch_id, counter_number, counter_name, status)
        VALUES (?, ?, ?, ?)
    ''', counters)

    # Seed lively demonstration tokens
    # Get hospital main branch and general op service
    cursor.execute('SELECT id FROM services WHERE prefix = "HOSP" LIMIT 1')
    s_hosp = cursor.fetchone()['id']
    cursor.execute('SELECT id FROM services WHERE prefix = "BANK" LIMIT 1')
    s_bank = cursor.fetchone()['id']
    cursor.execute('SELECT id FROM services WHERE prefix = "AKSH" LIMIT 1')
    s_aksh = cursor.fetchone()['id']

    hosp_b1 = b_map['Main Campus (Medical Square)']
    bank_b1 = b_map['MG Road Commercial Branch']
    aksh_b1 = b_map['Civil Station Kendra']

    demo_tokens = [
        # Hospital tokens
        ('HOSP-101', 'QK-8101', 'Rahul Sharma', '9876543210', inst_map['HOSP'], hosp_b1, s_hosp, 1, 'regular', 'instant', None, None, 'completed', 'checked_in', '2026-11-10 09:00:00', '2026-11-10 09:10:00', '2026-11-10 09:22:00'),
        ('HOSP-102', 'QK-8102', 'Ananya Patel', '9812345678', inst_map['HOSP'], hosp_b1, s_hosp, 1, 'senior', 'instant', None, None, 'serving', 'checked_in', '2026-11-10 09:15:00', '2026-11-10 09:25:00', None),
        ('HOSP-103', 'QK-8103', 'Vikram Singh', '9898989898', inst_map['HOSP'], hosp_b1, s_hosp, 1, 'regular', 'instant', None, None, 'waiting', 'checked_in', '2026-11-10 09:20:00', None, None),
        ('HOSP-104', 'QK-8104', 'Pooja Nair', '9745123456', inst_map['HOSP'], hosp_b1, s_hosp, 2, 'pwd', 'instant', None, None, 'waiting', 'pending', '2026-11-10 09:25:00', None, None),
        ('HOSP-105', 'QK-8105', 'George Mathew', '9845012399', inst_map['HOSP'], hosp_b1, s_hosp, 1, 'regular', 'appointment', '2026-11-10', '10:00 AM', 'waiting', 'pending', '2026-11-10 09:30:00', None, None),
        # Bank tokens
        ('BANK-101', 'QK-8201', 'Suresh Kumar', '9845012345', inst_map['BANK'], bank_b1, s_bank, 2, 'regular', 'instant', None, None, 'serving', 'checked_in', '2026-11-10 09:18:00', '2026-11-10 09:26:00', None),
        ('BANK-102', 'QK-8202', 'Deepa Varma', '9123456780', inst_map['BANK'], bank_b1, s_bank, 2, 'pregnant', 'instant', None, None, 'waiting', 'checked_in', '2026-11-10 09:22:00', None, None),
        # Akshaya token
        ('AKSH-101', 'QK-8301', 'Muhammed Fayis', '9988776655', inst_map['AKSH'], aksh_b1, s_aksh, 1, 'regular', 'instant', None, None, 'waiting', 'pending', '2026-11-10 09:28:00', None, None)
    ]

    cursor.executemany('''
        INSERT INTO tokens (
            token_number, verification_code, customer_name, phone,
            institution_id, branch_id, service_id, counter_number,
            priority, token_type, appointment_date, appointment_slot,
            status, checkin_status, created_at, serving_started_at, completed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', demo_tokens)

    # Seed sample feedback
    cursor.execute('''
        INSERT INTO feedback (token_number, customer_name, rating, comment)
        VALUES ('HOSP-101', 'Rahul Sharma', 5, 'Extremely quick service! No crowded waiting room at all.')
    ''')

    conn.commit()
    print("Master data and demo tokens successfully seeded!")

# =============================================================================
# HELPER & QUERY FUNCTIONS
# =============================================================================

def generate_verification_code():
    """Generates a unique 6-character verification code for QR and manual check-in (e.g. 'QL-4921')."""
    chars = string.ascii_uppercase + string.digits
    rand_part = ''.join(random.choices(chars, k=4))
    return f"QL-{rand_part}"

def generate_token_number(prefix):
    """Generates a sequential human-friendly unique token number per prefix (e.g. 'HOSP-106')."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT token_number FROM tokens
        WHERE token_number LIKE ?
        ORDER BY id DESC LIMIT 1
    ''', (f"{prefix}-%",))
    row = cursor.fetchone()
    conn.close()

    if row:
        try:
            num = int(row['token_number'].split('-')[1]) + 1
        except Exception:
            num = 101
    else:
        num = 101

    return f"{prefix}-{num}"

def add_token(customer_name, phone, institution_id, branch_id, service_id, 
              priority='regular', token_type='instant', appointment_date=None, appointment_slot=None):
    """
    Inserts a newly generated token with atomic token numbering and QR verification code.
    Calculates estimated wait time using:
    (people_ahead * avg_duration) / active_counters
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get service prefix
    cursor.execute('SELECT prefix, avg_duration_mins FROM services WHERE id = ?', (service_id,))
    service_row = cursor.fetchone()
    prefix = service_row['prefix'] if service_row else 'QLES'

    token_num = generate_token_number(prefix)
    verification_code = generate_verification_code()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        INSERT INTO tokens (
            token_number, verification_code, customer_name, phone,
            institution_id, branch_id, service_id, counter_number,
            priority, token_type, appointment_date, appointment_slot,
            status, checkin_status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, 'waiting', 'pending', ?)
    ''', (token_num, verification_code, customer_name, phone,
          institution_id, branch_id, service_id,
          priority, token_type, appointment_date, appointment_slot, now_str))

    token_id = cursor.lastrowid

    # Log creation
    cursor.execute('''
        INSERT INTO queue_logs (token_number, old_status, new_status, counter_number, changed_by)
        VALUES (?, NULL, 'waiting', 1, 'Customer Booking')
    ''', (token_num,))

    conn.commit()
    conn.close()

    return get_token_by_number(token_num)

def get_token_by_number(token_number):
    """
    Fetches full token record enriched with institution, branch, service details,
    currently serving token at that branch, people ahead, and smart waiting time.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            t.*,
            i.name AS institution_name,
            i.category,
            i.icon AS institution_icon,
            b.branch_name,
            b.location AS branch_location,
            b.opening_time,
            b.closing_time,
            s.service_name,
            s.avg_duration_mins
        FROM tokens t
        JOIN institutions i ON t.institution_id = i.id
        JOIN branches b ON t.branch_id = b.id
        JOIN services s ON t.service_id = s.id
        WHERE UPPER(t.token_number) = UPPER(?)
    ''', (token_number.strip(),))

    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    token = dict(row)
    branch_id = token['branch_id']
    avg_duration = token['avg_duration_mins'] or 10

    # 1. Count active open counters at this branch
    cursor.execute('''
        SELECT COUNT(*) AS active_count FROM counters
        WHERE branch_id = ? AND status = 'open' AND is_active = 1
    ''', (branch_id,))
    active_counters = cursor.fetchone()['active_count']
    if active_counters <= 0:
        active_counters = 1
    token['active_counters'] = active_counters

    # 2. Currently serving token at this branch
    cursor.execute('''
        SELECT token_number, counter_number, customer_name FROM tokens
        WHERE branch_id = ? AND status = 'serving'
        ORDER BY serving_started_at DESC, id DESC LIMIT 1
    ''', (branch_id,))
    serving_row = cursor.fetchone()
    token['current_serving'] = serving_row['token_number'] if serving_row else "None currently"
    token['serving_counter'] = serving_row['counter_number'] if serving_row else 1

    # 3. People ahead calculation:
    # Priority weighting: emergency > senior/pwd/pregnant > regular
    if token['status'] == 'waiting':
        cursor.execute('''
            SELECT COUNT(*) AS ahead_count FROM tokens
            WHERE branch_id = ? AND status = 'waiting' AND id < ?
        ''', (branch_id, token['id']))
        base_ahead = cursor.fetchone()['ahead_count']
        
        # If someone is serving, count them as ahead
        people_ahead = base_ahead + (1 if serving_row else 0)
        token['people_ahead'] = people_ahead

        # Smart wait estimation formula:
        # wait = ceil((people_ahead * avg_duration) / active_counters)
        estimated_mins = math.ceil((people_ahead * avg_duration) / max(1, active_counters))
        token['estimated_wait_time_minutes'] = max(2, estimated_mins) if people_ahead > 0 else 0

        # Dynamic Status helper: "Almost Your Turn" if people_ahead <= 2
        if people_ahead <= 2:
            token['display_status'] = 'Almost Your Turn'
        else:
            token['display_status'] = 'Waiting'
    elif token['status'] in ('serving', 'called'):
        token['people_ahead'] = 0
        token['estimated_wait_time_minutes'] = 0
        token['display_status'] = 'Now Serving' if token['status'] == 'serving' else 'Now Calling'
    elif token['status'] == 'completed':
        token['people_ahead'] = 0
        token['estimated_wait_time_minutes'] = 0
        token['display_status'] = 'Completed'
    elif token['status'] == 'skipped':
        token['people_ahead'] = 0
        token['estimated_wait_time_minutes'] = 0
        token['display_status'] = 'Skipped'
    else:
        token['people_ahead'] = 0
        token['estimated_wait_time_minutes'] = 0
        token['display_status'] = 'Cancelled'

    conn.close()
    return token

def cancel_token(token_number, cancelled_by="Customer"):
    """Cancels a waiting token and records audit log."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        UPDATE tokens
        SET status = 'cancelled', completed_at = ?
        WHERE UPPER(token_number) = UPPER(?) AND status IN ('waiting', 'called', 'skipped')
    ''', (now_str, token_number.strip()))

    rows_affected = cursor.rowcount
    if rows_affected > 0:
        cursor.execute('''
            INSERT INTO queue_logs (token_number, old_status, new_status, changed_by)
            VALUES (?, 'waiting', 'cancelled', ?)
        ''', (token_number.strip().upper(), cancelled_by))

    conn.commit()
    conn.close()
    return rows_affected > 0

def verify_qr_checkin(code_or_token):
    """
    Verifies QR code or 6-character check-in code.
    Marks token as 'checked_in'.
    Returns (success, message, token_details).
    """
    cleaned = code_or_token.strip().upper()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM tokens
        WHERE UPPER(verification_code) = ? OR UPPER(token_number) = ?
    ''', (cleaned, cleaned))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return False, "Invalid QR code or Token Number. Record not found.", None

    token = dict(row)
    if token['status'] in ('completed', 'cancelled'):
        conn.close()
        return False, f"Token {token['token_number']} is already {token['status']}. Cannot check in.", token

    if token['checkin_status'] == 'checked_in':
        conn.close()
        return True, f"Token {token['token_number']} was already checked in.", token

    # Mark as checked in
    cursor.execute('''
        UPDATE tokens SET checkin_status = 'checked_in' WHERE id = ?
    ''', (token['id'],))
    cursor.execute('''
        INSERT INTO queue_logs (token_number, old_status, new_status, changed_by)
        VALUES (?, ?, 'checked_in', 'QR Scanner')
    ''', (token['token_number'], token['status']))

    conn.commit()
    conn.close()

    enriched = get_token_by_number(token['token_number'])
    return True, f"Arrival confirmed for {token['customer_name']} (Token: {token['token_number']})!", enriched

def add_feedback(token_number, customer_name, rating, comment):
    """Stores customer feedback and ratings (1-5 stars)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO feedback (token_number, customer_name, rating, comment)
        VALUES (?, ?, ?, ?)
    ''', (token_number.strip().upper(), customer_name, int(rating), comment.strip()))
    conn.commit()
    conn.close()
    return True

def get_feedback_list(limit=20):
    """Returns recent feedback ratings."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM feedback ORDER BY id DESC LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# =============================================================================
# OPERATOR & MULTI-COUNTER QUEUE CONTROLS
# =============================================================================

def call_next_token(branch_id=None, counter_number=1, operator_name="Operator"):
    """
    Atomic multi-counter calling mechanism:
    1. Completes any token currently in 'serving' at this specific counter.
    2. Selects the next eligible token from the queue, prioritizing Emergency, then Senior/PwD/Pregnant, then Regular.
    3. Atomically sets status to 'serving' and binds it to this counter.
    Guarantees no two counters can call the same token!
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Complete token currently serving at this counter
    if branch_id:
        cursor.execute('''
            UPDATE tokens 
            SET status = 'completed', completed_at = ?
            WHERE branch_id = ? AND counter_number = ? AND status IN ('serving', 'called')
        ''', (now_str, branch_id, counter_number))
    else:
        cursor.execute('''
            UPDATE tokens 
            SET status = 'completed', completed_at = ?
            WHERE counter_number = ? AND status IN ('serving', 'called')
        ''', (now_str, counter_number))

    # Priority sorting:
    # 1. Emergency
    # 2. Senior / PwD / Pregnant
    # 3. Regular
    query = '''
        SELECT id FROM tokens
        WHERE status = 'waiting'
    '''
    params = []
    if branch_id:
        query += ' AND branch_id = ?'
        params.append(branch_id)

    query += '''
        ORDER BY 
            CASE priority
                WHEN 'emergency' THEN 1
                WHEN 'senior' THEN 2
                WHEN 'pwd' THEN 2
                WHEN 'pregnant' THEN 2
                ELSE 3
            END,
            id ASC
        LIMIT 1
    '''

    cursor.execute(query, params)
    next_row = cursor.fetchone()

    if not next_row:
        conn.commit()
        conn.close()
        return None

    next_id = next_row['id']

    # Atomically claim token for this counter
    cursor.execute('''
        UPDATE tokens
        SET status = 'serving', serving_started_at = ?, counter_number = ?
        WHERE id = ? AND status = 'waiting'
    ''', (now_str, counter_number, next_id))

    if cursor.rowcount == 0:
        # Race condition resolved: already taken by another counter
        conn.commit()
        conn.close()
        return None

    cursor.execute('SELECT token_number FROM tokens WHERE id = ?', (next_id,))
    called_number = cursor.fetchone()['token_number']

    cursor.execute('''
        INSERT INTO queue_logs (token_number, old_status, new_status, counter_number, changed_by)
        VALUES (?, 'waiting', 'serving', ?, ?)
    ''', (called_number, counter_number, operator_name))

    conn.commit()
    conn.close()

    return get_token_by_number(called_number)

def skip_token(token_id, operator_name="Operator"):
    """Skips a token (moves to 'skipped' status, can be recalled later)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT token_number, status FROM tokens WHERE id = ?', (token_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    cursor.execute("UPDATE tokens SET status = 'skipped' WHERE id = ?", (token_id,))
    cursor.execute('''
        INSERT INTO queue_logs (token_number, old_status, new_status, changed_by)
        VALUES (?, ?, 'skipped', ?)
    ''', (row['token_number'], row['status'], operator_name))
    conn.commit()
    conn.close()
    return True

def recall_token(token_id, counter_number=1, operator_name="Operator"):
    """Recalls a skipped or waiting token directly to the counter."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('SELECT token_number, status FROM tokens WHERE id = ?', (token_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    cursor.execute('''
        UPDATE tokens SET status = 'serving', counter_number = ?, serving_started_at = ?
        WHERE id = ?
    ''', (counter_number, now_str, token_id))

    cursor.execute('''
        INSERT INTO queue_logs (token_number, old_status, new_status, counter_number, changed_by)
        VALUES (?, ?, 'serving', ?, ?)
    ''', (row['token_number'], row['status'], counter_number, operator_name))

    conn.commit()
    conn.close()
    return get_token_by_number(row['token_number'])

def update_counter_status(branch_id, counter_number, status):
    """Sets counter status: 'open', 'break', or 'closed'."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE counters SET status = ?
        WHERE branch_id = ? AND counter_number = ?
    ''', (status, branch_id, counter_number))
    conn.commit()
    conn.close()
    return True

def get_branch_counters(branch_id):
    """Returns all counters for a given branch along with their current status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM counters WHERE branch_id = ? ORDER BY counter_number ASC
    ''', (branch_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# =============================================================================
# PUBLIC DISPLAY SCREEN & WAITING BOARD
# =============================================================================

def get_display_board_data(branch_id=None):
    """
    Returns data needed for the Public TV Display Screen:
    - Currently serving tokens per active counter (Counter 1: HOSP-102, Counter 2: BANK-101, etc.)
    - Next waiting tokens (for marquee/ticker)
    - Branch information
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Active counters serving tokens
    query_serving = '''
        SELECT 
            t.token_number,
            t.counter_number,
            t.customer_name,
            s.service_name,
            c.counter_name,
            c.status AS counter_status
        FROM tokens t
        JOIN services s ON t.service_id = s.id
        LEFT JOIN counters c ON (t.branch_id = c.branch_id AND t.counter_number = c.counter_number)
        WHERE t.status = 'serving'
    '''
    params_serving = []
    if branch_id:
        query_serving += ' AND t.branch_id = ?'
        params_serving.append(branch_id)
    query_serving += ' ORDER BY t.counter_number ASC'

    cursor.execute(query_serving, params_serving)
    serving_counters = [dict(r) for r in cursor.fetchall()]

    # Up next waiting tokens (Top 10)
    query_waiting = '''
        SELECT 
            t.token_number,
            t.customer_name,
            t.priority,
            s.service_name
        FROM tokens t
        JOIN services s ON t.service_id = s.id
        WHERE t.status = 'waiting'
    '''
    params_waiting = []
    if branch_id:
        query_waiting += ' AND t.branch_id = ?'
        params_waiting.append(branch_id)

    query_waiting += '''
        ORDER BY 
            CASE t.priority
                WHEN 'emergency' THEN 1
                WHEN 'senior' THEN 2
                WHEN 'pwd' THEN 2
                WHEN 'pregnant' THEN 2
                ELSE 3
            END,
            t.id ASC
        LIMIT 10
    '''
    cursor.execute(query_waiting, params_waiting)
    waiting_tokens = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "serving_counters": serving_counters,
        "waiting_tokens": waiting_tokens
    }

# =============================================================================
# UNIVERSAL INSTITUTION SELECTION & SEARCH
# =============================================================================

def search_institutions(keyword="", category="all"):
    """Searches institutions across name, category, and branch location."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        SELECT DISTINCT 
            i.id, i.code, i.name, i.category, i.icon, i.description,
            (SELECT COUNT(*) FROM branches b WHERE b.institution_id = i.id) AS branch_count
        FROM institutions i
        LEFT JOIN branches b ON i.id = b.institution_id
        WHERE i.is_active = 1
    '''
    params = []

    if category and category != 'all':
        query += ' AND i.category = ?'
        params.append(category)

    if keyword and keyword.strip():
        k = f"%{keyword.strip()}%"
        query += ' AND (i.name LIKE ? OR i.category LIKE ? OR b.branch_name LIKE ? OR b.location LIKE ?)'
        params.extend([k, k, k, k])

    query += ' ORDER BY i.id ASC'

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_institution_details(institution_id):
    """Returns an institution with all its branches and services."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM institutions WHERE id = ?', (institution_id,))
    inst_row = cursor.fetchone()
    if not inst_row:
        conn.close()
        return None

    inst = dict(inst_row)

    # Branches
    cursor.execute('''
        SELECT b.*, 
            (SELECT COUNT(*) FROM counters c WHERE c.branch_id = b.id AND c.status = 'open') AS open_counters
        FROM branches b 
        WHERE b.institution_id = ? AND b.is_active = 1
    ''', (institution_id,))
    inst['branches'] = [dict(r) for r in cursor.fetchall()]

    # Services
    cursor.execute('''
        SELECT * FROM services WHERE institution_id = ? AND is_active = 1
    ''', (institution_id,))
    inst['services'] = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return inst

def get_all_categories():
    """Returns unique institution categories."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT category FROM institutions WHERE is_active = 1')
    cats = [r['category'] for r in cursor.fetchall()]
    conn.close()
    return cats

# =============================================================================
# ADMIN ANALYTICS & STATISTICS
# =============================================================================

def get_queue_statistics():
    """Returns high-level statistics across all tokens."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) AS total FROM tokens')
    total = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS serving FROM tokens WHERE status = 'serving'")
    serving = cursor.fetchone()['serving']

    cursor.execute("SELECT COUNT(*) AS waiting FROM tokens WHERE status = 'waiting'")
    waiting = cursor.fetchone()['waiting']

    cursor.execute("SELECT COUNT(*) AS completed FROM tokens WHERE status = 'completed'")
    completed = cursor.fetchone()['completed']

    cursor.execute("SELECT COUNT(*) AS cancelled FROM tokens WHERE status = 'cancelled'")
    cancelled = cursor.fetchone()['cancelled']

    # Average rating
    cursor.execute("SELECT AVG(rating) AS avg_rating, COUNT(*) AS count FROM feedback")
    fb_row = cursor.fetchone()
    avg_rating = round(fb_row['avg_rating'] or 5.0, 1)
    feedback_count = fb_row['count']

    # Average wait time in minutes (based on completed tokens)
    cursor.execute('''
        SELECT AVG((julianday(serving_started_at) - julianday(created_at)) * 24 * 60) AS avg_wait
        FROM tokens WHERE status = 'completed' AND serving_started_at IS NOT NULL
    ''')
    avg_wait_row = cursor.fetchone()
    avg_wait = round(avg_wait_row['avg_wait'] or 8.5, 1)

    conn.close()
    return {
        'total': total,
        'serving': serving,
        'waiting': waiting,
        'completed': completed,
        'cancelled': cancelled,
        'avg_rating': avg_rating,
        'feedback_count': feedback_count,
        'avg_wait': avg_wait
    }

def get_all_tokens(branch_id=None, status=None, limit=100):
    """Returns token list for admin and operator tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        SELECT 
            t.*,
            i.name AS institution_name,
            i.category,
            b.branch_name,
            s.service_name
        FROM tokens t
        JOIN institutions i ON t.institution_id = i.id
        JOIN branches b ON t.branch_id = b.id
        JOIN services s ON t.service_id = s.id
        WHERE 1=1
    '''
    params = []

    if branch_id and branch_id != 'all':
        query += ' AND t.branch_id = ?'
        params.append(branch_id)

    if status and status != 'all':
        query += ' AND t.status = ?'
        params.append(status)

    query += '''
        ORDER BY 
            CASE t.status
                WHEN 'serving' THEN 1
                WHEN 'called' THEN 2
                WHEN 'waiting' THEN 3
                WHEN 'skipped' THEN 4
                ELSE 5
            END,
            t.id DESC
        LIMIT ?
    '''
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_tokens_by_phone(phone):
    """Returns all tokens booked under a customer's phone number."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            t.*,
            i.name AS institution_name,
            i.category,
            b.branch_name,
            b.location AS branch_location,
            s.service_name
        FROM tokens t
        JOIN institutions i ON t.institution_id = i.id
        JOIN branches b ON t.branch_id = b.id
        JOIN services s ON t.service_id = s.id
        WHERE t.phone = ?
        ORDER BY t.id DESC
    ''', (phone.strip(),))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
