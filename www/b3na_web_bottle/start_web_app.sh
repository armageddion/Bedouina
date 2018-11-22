echo "starting bena webapp"

echo "exporting env var"
export FLASK_APP=/opt/b3na/www/b3na_web_bottle/b3na.py

echo "starting app"
flask run
