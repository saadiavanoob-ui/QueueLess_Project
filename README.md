# QueueLess – Digital Token & Queue Management System

A beginner-friendly, attractive, and functional full-stack web application designed by first-year B.Tech Computer Science and Engineering students for college project exhibitions and practical queue orchestration.

---

## 🌟 1. Project Overview & Problem Statement

In public service areas such as **Hospitals, Banks, Akshaya Centres, Government Revenue Offices, and College Administration Desks**, physical lines waste hours of productive citizen time, lead to hallway overcrowding, and generate anxiety for visitors.

**QueueLess** solves this challenge by digitizing the queue experience:
- **Instant Token Generation:** Visitors select their institution and required service to receive a unique token number.
- **Real-Time Live Tracking:** Monitor current serving tokens, see how many people are ahead, and get dynamic wait-time estimation on your smartphone.
- **Admin Calling Counter:** Counter officers can call the next token with one click, triggering screen updates and realistic browser voice announcements.
- **No Complex Frameworks:** Built with standard **HTML, CSS, JavaScript, Python Flask, and SQLite**, keeping the code simple, readable, and 100% understandable for first-year CSE students.

---

## 🎨 2. Visual Design & Theme

- **Dark Green & Emerald Palette:**
  - Dark Green: `#064e3b` (Primary brand color)
  - Emerald Green: `#059669` / `#10b981` (Call-to-action & active states)
  - Light Mint Green: `#ecfdf5` (Gentle backgrounds and badges)
  - Clean Whites & Light Greys: `#ffffff`, `#f8fafc`
- **Modern UI Elements:** Soft shadows, rounded card containers (`16px-24px`), smooth hover lift animations, and clean vector illustrations.
- **Responsive:** Fluid layout adaptable to mobile devices, tablets, and exhibition laptops.

---

## 🛠️ 3. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript | Responsive user interface, interactive category switching, live polling, and voice chimes |
| **Icons** | Font Awesome 6.5 & Custom SVG | High-definition icons for hospitals, banks, kiosks, and stopwatches |
| **Backend** | Python Flask | Lightweight web framework handling routing and RESTful JSON APIs |
| **Database** | SQLite3 (Built into Python) | Relational database storing tokens, customer details, and timestamps |

---

## 📁 4. Project File Structure & Explanation

```
queueless/
├── app.py                     # Main Flask backend application (routes and API logic)
├── database.py                # SQLite database helper functions & query handlers
├── requirements.txt           # Python dependency file (Flask)
├── README.md                  # Comprehensive documentation and exhibition presentation guide
├── static/
│   ├── css/
│   │   └── style.css          # Modern stylesheet with green theme, cards, and responsive CSS
│   ├── js/
│   │   ├── main.js            # Global utilities: mobile menu, toast alerts, Web Speech API
│   │   ├── booking.js         # Token booking form, service cascading, and receipt modal
│   │   ├── tracking.js        # Live queue tracker with 4-second auto-poll and stepper
│   │   └── admin.js           # Admin counter controls: call next, complete, cancel tokens
│   └── images/
│       ├── logo.svg           # Green stopwatch QueueLess logo
│       └── hero-illustration.svg # High-definition vector art showing kiosk and waiting room
└── templates/
    ├── base.html              # Shared website layout: navigation bar, footer, and scripts
    ├── index.html             # Homepage: Hero section, 6 institution cards, features, about
    ├── book.html              # Token booking page with dynamic categories and services
    ├── track.html             # Real-time token tracker page with live status stepper
    ├── admin_login.html       # Demonstration login page with pre-filled credentials
    └── admin.html             # Counter staff queue management dashboard
```

### Purpose of Every Important File

1. **`app.py`**:
   - Central backend hub.
   - Defines page routes (`/`, `/book`, `/track`, `/admin/login`, `/admin`).
   - Defines REST endpoints (`/api/tokens/book`, `/api/tokens/track/<token>`, `/api/tokens/call-next`, `/api/tokens/<id>/status`).
   - Stores the catalog of institution categories and service departments.

2. **`database.py`**:
   - Manages SQLite connection and `tokens` table creation.
   - Automatically seeds realistic sample tokens on first run so the project looks active immediately.
   - Implements helper functions: `add_token()`, `get_token_by_number()`, `call_next_waiting_token()`, and `get_queue_statistics()`.

3. **`templates/index.html`**:
   - The primary landing page.
   - Features the two-column hero section with heading, tagline, description, and modern SVG waiting room illustration.
   - Features the six requested institution cards: Hospital (red cross), Bank (blue bank), Akshaya Centre (purple icon), Government Office (orange icon), Laboratory (green flask), and Service Centre (teal headset).

4. **`templates/book.html` & `booking.js`**:
   - Provides category tabs to choose Hospital, Bank, etc.
   - Dynamically updates sample branches and departmental services.
   - Submits booking via AJAX and displays a modal receipt with a big token badge and print option.

5. **`templates/track.html` & `tracking.js`**:
   - Allows users to search any token number (e.g. `HOSP-102`).
   - Features a 4-step progress stepper: Token Issued ➔ In Queue ➔ At Counter ➔ Completed.
   - Auto-refreshes every 4 seconds so users can see the queue moving live without manual reloading.

6. **`templates/admin.html` & `admin.js`**:
   - Demonstration workstation for counter operators.
   - Shows active serving token and has a prominent **"Call Next Token"** button.
   - Uses the browser's `SpeechSynthesis` Web API to speak the announcement aloud: *"Token HOSP-103, please proceed to Counter 1"*.

---

## 🚀 5. How to Run the Project Locally

### Prerequisites
- Python 3.8 or higher installed on your computer.

### Step 1: Open Terminal / PowerShell
Navigate to the project directory:
```bash
cd "C:\Users\Admin\.gemini\antigravity\scratch\queueless"
```

### Step 2: Install Flask
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python app.py
```

### Step 4: Open in Web Browser
Open your browser (Chrome, Edge, or Firefox) and visit:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 6. Demonstration Admin Credentials

For college project evaluation and demo purposes:
- **URL:** `http://127.0.0.1:5000/admin/login`
- **Username:** `admin`
- **Password:** `admin123`

---

## 🎤 7. College Exhibition Presentation Guide

Follow this 5-minute demonstration script during your project exhibition to impress evaluators:

1. **Introduction (1 min):**
   - *"Respected teachers and evaluators, we present QueueLess – an intelligent digital token management platform developed using Python Flask, SQLite, HTML5, CSS3, and JavaScript."*
   - Show the Homepage: explain the clean green palette, the two-column hero section with the service centre illustration, and the live queue statistics strip.

2. **Selecting Institution & Booking (1.5 mins):**
   - Click on the **Hospital** card.
   - Show how the category tabs and services dynamically update without page reloads.
   - Enter your name and phone number, then click **Generate Token**.
   - Show the generated confirmation receipt with token number (e.g., `HOSP-105`), number of people ahead, and estimated wait time.

3. **Live Tracking (1 min):**
   - Click **"Track Live Queue Status"**.
   - Show the 4-stage stepper: highlight that the token is currently in **"In Queue"** status.

4. **Admin Calling & Voice Announcement (1.5 mins):**
   - Open a new tab or window and navigate to `/admin`.
   - Log in with `admin` / `admin123`.
   - Click **"Call Next Token"**.
   - Listen to the browser speak the announcement aloud: *"Token HOSP-103, please proceed to Counter 1"*.
   - Switch back to the tracking tab and watch the status update in real time to **"At Counter"** with the green pulsing badge!
