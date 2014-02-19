from app import app, env
from tools.apps import installed_apps_loader
## import urls from list of <config>.INSTALLED_APPS
installed_apps_loader(app, app.config['INSTALLED_APPS'])

print "=========\nLoaded URLs: %s\n==========" % app.url_map

if __name__ == "__main__":
    print "Starting Application Process..."
    app.run('127.0.0.1', 8000)
