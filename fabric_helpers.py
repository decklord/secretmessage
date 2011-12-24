from fabric.operations import local


import sys
import os

if "local" in sys.argv:
    from fabric.operations import local as run
    from fabric.context_managers import lcd as cd
    current_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(current_dir)
    

    def sudo(cmd):
        return local("sudo %s" % cmd)
else:
    from fabric.api import run, cd, sudo
#read function for add_db
def read(msg, default=None, options=None):
    if options is not None:
        msg = "%s [%s]" % (msg, ', '.join(options))
    if default is None:
        msg = "%s: " % msg
    else:
        msg = "%s (%s): " % (msg, default)

    user_input = raw_input(msg)
    if user_input == "" and default is not None:
        user_input = default

    if options is not None and user_input not in options:
        return read(msg, default=default, options=options)
    return user_input
#prepr function for add_db
def prepr(var):
    out = repr(var).replace("{","{\n").replace(",",",\n").replace("}","}\n")
    return out


