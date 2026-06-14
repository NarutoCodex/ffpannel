# FF PANELS - Complete Website

## Setup & Run

### Local (PC/Termux)
```bash
pip install -r requirements.txt
python app.py
```
Open: http://localhost:5000

### Railway Deploy
1. Upload all files to GitHub
2. Connect repo to Railway
3. Set start command: `python app.py`
4. Done!

---

## Login Credentials

### User Login: http://localhost:5000/login
- Register karo naya account ya pehle se jo create ho

### Admin Panel: http://localhost:5000/admin/login
- Username: `admin`
- Password: `admin123`

---

## Features

### User Side
- ✅ Register / Login / Logout
- ✅ Home - Balance, Orders stats
- ✅ Store - Categories with video/placeholder
- ✅ Buy Key button → price plans expand
- ✅ Auto key generation on purchase
- ✅ My Keys - All orders with key codes
- ✅ Profile - Change password

### Admin Panel
- ✅ Dashboard - Stats + recent orders
- ✅ Categories - Add/Edit/Delete with:
  - Tags (Non Root, Root, Android, iOS, User)
  - Features list
  - Notice text
  - Video URL
  - Price plans (unlimited)
  - Show/Hide toggle
- ✅ Users - Balance add/remove/set
- ✅ Orders - All orders table

---

## Change Admin Password
In `app.py`, find `init_db()` and change `admin123` to your password.
Or update directly in SQLite: `ffpanels.db`
