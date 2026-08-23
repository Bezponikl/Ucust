import psycopg2
conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/ai_smm')
conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'nodes'")
for row in cur.fetchall():
    print(row)
