import api.engine
import datetime

engine = api.engine.Engine()
con = engine.connect()
m1 = con.get_message(1)
m2 = con.get_message(2)
con.create_message(10000, 1, 'Hello from the otter side.')
#con.get_message(m3)
print('m1: ', m1)
print('m2: ', m2)
print('time_m1:', int(m1['created']))

con.close()
