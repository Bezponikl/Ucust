import psycopg2
conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/ai_smm')
conn.autocommit = True
cur = conn.cursor()
cur.execute("DELETE FROM nodes WHERE name LIKE 'runtime:agents:%:state' AND data::text LIKE '%\"agent_id\"%'")
print(cur.rowcount)
