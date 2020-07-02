import os
import sys
from app import create_app, login_manager
import click
# from app.models import User, Order, Meal, Company

# sys.path.append('C:\\Users\\brako\\Desktop\\Work\\pergamon\\ip\\ipdb')
# sys.path.append('/mnt/c/Users/brako/Desktop/Work/pergamon/ip/ipdb')

paths = os.environ.get('DATABASE_MODULE_PATH')

if paths:
    paths = paths.split('~')
    for p in paths:
        sys.path.append(p)



from db.models import User, Company, Order, Meal
from db.database import session


app = create_app()


@app.cli.command("daily-job")
def daily_job():
    from app.main.jobs import send_daily_summary
    send_daily_summary(app)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


@app.shell_context_processor
def make_shell_context():
    return {'session': session, 'User': User, 'Order': Order, 'Meal': Meal, 'Company': Company}

