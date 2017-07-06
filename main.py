import forum.database as db
engine = db.Engine()
con = engine.connect()
engine.create_users_profile_table()
con.close()
