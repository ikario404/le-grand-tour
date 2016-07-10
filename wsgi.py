import sys
sys.path.insert(0, "/home/ubuntu/velo/-le-grand-tour")

from app import app
application = app

if __name__ == "__main__":
    app.run()
