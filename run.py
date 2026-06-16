import os
from app import app, db, seed_data, run_migrations

with app.app_context():
    db.create_all()
    run_migrations()
    seed_data()

# Exposed for gunicorn: gunicorn run:app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
