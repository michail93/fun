echo "The running of app"
sleep 3
python manage.py migrate
python manage.py test
python manage.py runserver 0.0.0.0:8000