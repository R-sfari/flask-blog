import os
from flask_migrate import upgrade
from app import fixtures, create_app, db, socket_io
from app.models import User, Role, Permission
from flask_sqlalchemy import get_debug_queries
from flask import current_app


app = create_app(os.getenv('FLASK_CONFIG', 'DEFAULT'))


@app.cli.command()
def migrate_database():
    upgrade()


@app.cli.command()
def load_fixtures():
    fixtures.exec_fixtures()


@app.cli.command()
def run_tests():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.shell_context_processor
def shell_context():
    return dict(db=db, Role=Role, User=User, Permission=Permission)

if __name__ == "__main__":
    app.run()
