from app import app
from simulator import seed_database

# Ensure database and demo baseline are seeded on cold start
seed_database(app)

if __name__ == '__main__':
    app.run()
