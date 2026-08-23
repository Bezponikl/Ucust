import psycopg2
conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/ai_smm')
conn.autocommit = True
cur = conn.cursor()
try:
    cur.execute("INSERT INTO nodes (tenant_id, name, valid_from, valid_until) VALUES ('dev', 'metrics:test', 0, 0)")
    print("Insert succeeded!")
except Exception as e:
    print("Insert failed:", e)
