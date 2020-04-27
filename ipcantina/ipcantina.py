from app import app, db
from app.models import User, Order, Meal, Company
from sqlalchemy import func


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Order': Order, 'Meal': Meal, 'func': func, 'Company': Company}


# if __name__ == "__main__":
#     app.run(debug=True)
