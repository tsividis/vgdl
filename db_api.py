import psycopg2
from vgdl import core

config = {'dbname'  : 'd9ahikn1rs4equ',
					'user'    : 'smcgqgjzpgenik',
					'host'    : 'ec2-54-235-85-65.compute-1.amazonaws.com',
					'password': 'mlKsdNWIVGgGEbO9-VwQ1S74c_'}

client = psycopg2.connect("dbname='{dbname}' user='{user}' host='{host}' password='{password}'".format(**config))

cur = client.cursor()
cur.execute('select * from games')
