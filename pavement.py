import os
from paver.easy import *

def run(script):
    for line in script.strip().split("\n"):
        print("\n[SYSTEM] %s" % line.strip())
    os.system(script)

@task
def test():
    """
    Run tests using unittest disccover.
    """
    run("python -m unittest discover")

@task
def setup_virtualenv():
    """Setup virtualenv in: ~/.envs/data/"""
    run("""
        mkdir -p ~/.envs
        virtualenv -p /usr/bin/python3.4 ~/.envs/data
        source ~/.envs/data/bin/activate
        pip install -r requirements.txt
    """)

@task
def freeze_requirements():
    """Freeze requirements."""
    run("pip freeze > requirements.txt")

