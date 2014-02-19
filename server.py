from app import app
from views import index

if __name__ == "__main__":
    print "Starting Application Process..."
    app.run('127.0.0.1', 8000)
