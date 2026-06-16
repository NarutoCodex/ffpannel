===========================================
       FF PANELS - WEBSITE SETUP GUIDE
===========================================

REQUIREMENTS:
  Python 3.8+

INSTALL & RUN:
  1. Install dependencies:
     pip install flask flask-sqlalchemy werkzeug

  2. Run the website:
     python run.py

  3. Open browser:
     http://localhost:5000

===========================================
LOGIN CREDENTIALS:
===========================================

  ADMIN LOGIN:
    URL: http://localhost:5000/admin
    Username: admin
    Password: admin123

  USER LOGIN:
    URL: http://localhost:5000/login
    (Create new account from register page)

===========================================
FEATURES:
===========================================

  USER SIDE:
    - Register / Login / Logout
    - Home dashboard with balance & stats
    - Store with categories + price plans
    - Buy Key (auto-generates key code)
    - My Keys / Order history
    - Profile + Change Password

  ADMIN PANEL (/admin):
    - Dashboard with stats & recent orders
    - Add / Edit / Delete categories
    - Upload video for each category
    - Set tags (Non Root, Root, Android, iOS, User)
    - Add unlimited price plans per category
    - View all users with balance management
    - Add / Remove / Set user balance
    - Delete users
    - View all orders with key codes

===========================================
DEPLOY ON RAILWAY / RENDER:
===========================================

  Set environment variable:
    DATABASE_URL = your_postgres_url (optional)

  Or just use SQLite (default) - works fine!

===========================================
FOLDER STRUCTURE:
===========================================

  ffpanels/
    app.py          - Main Flask application
    run.py          - Start script
    requirements.txt
    templates/
      login.html
      register.html
      home.html
      store.html
      keys.html
      profile.html
      base.html
      admin/
        base.html
        dashboard.html
        categories.html
        category_form.html
        users.html
        orders.html
    static/
      uploads/      - Video files stored here

===========================================
