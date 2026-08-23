import psycopg2
conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/ai_smm')
conn.autocommit = True
cur = conn.cursor()
cur.execute("UPDATE nodes SET collection = 'dev'")
print(cur.rowcount, 'rows updated')
