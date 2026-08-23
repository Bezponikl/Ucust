import psycopg2
conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/ai_smm')
conn.autocommit = True
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE nodes ADD COLUMN tenant_id VARCHAR(255) DEFAULT 'dev'")
    print("Added tenant_id to nodes")
except Exception as e:
    print(e)
    
try:
    cur.execute("ALTER TABLE platform_usage ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    print("Added updated_at to platform_usage")
except Exception as e:
    print(e)

try:
    cur.execute('''
    CREATE TABLE IF NOT EXISTS circuit_breaker_config (
        id VARCHAR(255) PRIMARY KEY,
        notify_email VARCHAR(255)
    )''')
    print("Created circuit_breaker_config")
except Exception as e:
    print(e)
