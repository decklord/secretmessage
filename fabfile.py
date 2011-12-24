import sys
from fabric_helpers import sudo, cd, run, read, prepr
from fabric.api import settings

def local():
    print "Running in local mode."

def remote():
    print "Running in remote mode."

def info():
    import project.settings as django_settings
    if django_settings.DEBUG:
        print "Server is in development mode."
    else:
        print "Server is in production mode."

def test(module="",verbose=0):
    verbose = int(verbose)
    if verbose == 1:
        grep_filter = ""
    else:
        grep_filter = "| grep '\(Assertion\)\|\(\.\.\.\.\)\|\(Ran\)'"
    with cd("project"):
        run("python manage.py test %s 2>&1 %s " % (module, grep_filter))

def init_submodules():
    run("git submodule init")
    run("git submodule update")

def install_nodejs():
    NODE_VERSION = "v0.6.5"

    with settings(warn_only=True):
        result = run("node --version")
        
    if result.failed:
        with cd("lib/node"):
            run("git checkout %s" % NODE_VERSION)
            sudo("apt-get install libssl-dev openssl")
            run("./configure")
            run("make")
            sudo("make install")
    else:
        print "Node.js already installed"

    install_npm()

def install_npm():
    with settings(warn_only=True):
        result = run("npm --version")

    if result.failed:
        sudo("apt-get install curl")
        run("curl http://npmjs.org/install.sh | sh")
    else:
        print "npm already installed"

def install_coffee():
    with settings(warn_only=True):
        result = run("coffee --version")

    if result.failed:
        sudo("npm install -g coffee-script")
    else:
        print "Coffeescript already installed"


def install_tastypie():
    try:
        import tastypie
        print "tastypie is installed - version %s." % str(tastypie.__version__)
    except ImportError, e:
        sudo("pip install mimeparse")
        with cd('lib/django-tastypie'):
            sudo("python setup.py install")

def install_jsonrpc():
    try:
        import jsonrpc
        print "jsonrpc is installed."
    except ImportError, e:
        if e.message == "No module named jsonrpc":
            with cd('lib/django-json-rpc'):
                sudo("python setup.py install")

def install_django():
    try:
        import django
        print "django is installed - version %s." % str(django.VERSION)

    except ImportError, e:
        if e.message == "No module named django":
            with cd('lib/Django-1.3.1'):
                sudo("python setup.py install")

def install():
    init_submodules()
    install_django()
    install_jsonrpc()
    install_tastypie()
    install_nodejs()
    #test()

def configure_mysql():
    sudo("apt-get install mysql-server python-mysqldb")
    with cd("project"):
        run("rm -rf local*")
        run("./django-create-local-settings")
        run("./django-add-db")
        run("./mysql-create-djangouser")
        run("python manage.py syncdb")

def quickstart():
    install()
    configure_mysql()
    run_development()


def run_development():
    with cd("project"):
        run("python manage.py runserver 0.0.0.0:8000") 
def say_hello():
    print "Hello!"
def django_add_db():
    import os
    from settings import DATABASES
    from pprint import pprint
    project_name = os.getcwd().split("/")[-1]

    config_name = read("Configuration name","default")
    engine = read("Database Engine",
        options=['postgresql_psycopg2', 'postgresql', 'sqlite3', 'oracle', 'mysql'],
        default="mysql")

    if engine == "sqlite3":
        name_msg = "Path to database"
        name_default = "./%s_database.sqlite3" % project_name
        user = ""
        password = ""
        host = ""
        port = ""
    else:
        name_msg = "Database name"
        name_default = project_name

    name = read(name_msg, default=name_default)

    if engine != "sqlite3":
        user = read("Database user", default=project_name)
        password = read("Database password", default=project_name)
        host = read("Database host (localhost)")
        port = read("Database port (use default)")

    db_config = {
            'ENGINE' : "django.db.backends.%s" % engine,
            'NAME' : name,
            'USER' : user,
            'PASSWORD' : password,
            'HOST' : host,
            'PORT' : port,
    }

    DATABASES[config_name] = db_config
    f = file("./local_databases.py","w")
    f.write("DATABASES = "+prepr(DATABASES))
    f.close()

def django_create_local_settings():
    pass

def mysql_create_dbuser(name,user,password):
    q1 = "GRANT USAGE ON "+name+".* TO '"+user+"'@'localhost';"
    q2 = "CREATE USER '"+user+"'@'localhost' IDENTIFIED BY '"+password+"';"
    q3 = "FLUSH PRIVILEGES;"
    root_password = input("Please, enter root password")
    run("mysql --user=root --password="+root_password+" -e \""+q1+" "+q2+" "+q3+"\" mysql")

def mysql_create_djangouser():
    import project.settings as settings 
    dbname = settings.DATABASES['default']['NAME']
    dbuser = settings.DATABASES['default']['USER']
    dbpass = settings.DATABASES['default']['PASSWORD']
    mysql_create_djangouser(dbname, dbuser, dbpass)

def db_drop_djangouser():
    import project.settings as settings 
    dbname = settings.DATABASES['default']['NAME']
    dbuser = settings.DATABASES['default']['USER']
    dbpass = settings.DATABASES['default']['PASSWORD']
    q1 = "GRANT USAGE ON "+dbname+".* TO '"+dbuser+"'@'localhost';"
    q2 = "DROP USER "+dbuser+"@localhost;"
    q3 = "FLUSH PRIVILEGES;"
    sql = q1+" "+q2+" "+q3
    password = input("Please, enter root password")
    run("mysql --user=root --password="+password+" -e \""+sql+"\" mysql")

def db_create():
    import project.settings as settings 
    dbname = settings.DATABASES['default']['NAME']
    dbuser = settings.DATABASES['default']['USER']
    dbpass = settings.DATABASES['default']['PASSWORD']
    q1 = "GRANT USAGE ON "+dbname+".* TO '"+dbuser+"'@'localhost';"
    q2="CREATE DATABASE "+dbname+";"
    q3="GRANT ALL ON $dbname.* TO '$dbuser'@'localhost' WITH GRANT OPTION;"
    q4="FLUSH PRIVILEGES;"
    sql = q1+" "+q2+" "+q3+" "+q4
    password = input("Please, enter root password")
    run("mysql --user=root --password="+password+" -e \""+sql+"\" mysql")

def load_superuser():
    with cd("project"):
        run("python manage.py loaddata superuser")

def db_flush():
    import project.settings as settings 
    dbconfig = settings.DATABASES['default']
    dbengine = dbconfig['ENGINE'].split(".")[-1]

    if dbengine == 'sqlite3':
        dbfile = settings.DATABASES['default']['NAME'].split("/")
        dbfile = dbfile[1]
        with cd("project"):
            run("rm "+dbfile+" -rf")
    elif dbengine == 'mysql':
        cmd = "mysqldump -u%s -p%s --add-drop-table --no-data %s | grep ^DROP | mysql -u%s -p%s %s"
        cmd %= (dbconfig['USER'], dbconfig['PASSWORD'], dbconfig['NAME'],
                dbconfig['USER'], dbconfig['PASSWORD'], dbconfig['NAME'])
        run(cmd)

    with cd("project"):
        run("echo 'no' | python manage.py syncdb")
    load_superuser()

def install_klooff_lib():
    with cd("lib/klooff"):
        sudo("python setup.py install")
