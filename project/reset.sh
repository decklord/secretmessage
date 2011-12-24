./mysql-create-djangouser
echo "no" | python manage.py syncdb
pyhon manage.py loaddata superuser
