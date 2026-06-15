from app import app, db, seed_data, run_migrations
import os

with app.app_context():
    db.create_all()
    run_migrations()
    seed_data()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
