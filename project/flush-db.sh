rm project_database.sqlite3 -rf
echo "Done!"
python2 manage.py syncdb
