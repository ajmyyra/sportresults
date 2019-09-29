from wsgi import db

print("Checking database for existing database schema")
if not db.engine.dialect.has_table(db.engine, 'contestant'):
    db.create_all()