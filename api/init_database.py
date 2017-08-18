import api.engine

engine = api.engine.Engine()

try:
    engine.remove_database()
    print ('Removing existing database.')
except OSError:
    print ('No existing database found.')

engine.create_tables()
print ('Created database and tables based on db/chirrup_schema_dump.sql')

engine.populate_tables()
print ('Inserted fake data based on db/chirrup_data_dump.sql.')

print ('Database creation ready.')