echo "starting bena webapp"

echo "exporting env var"
export FLASK_APP=b3na.py

echo "starting app"
flask run
