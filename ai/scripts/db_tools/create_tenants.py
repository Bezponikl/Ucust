import psycopg2
conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/ai_smm')
conn.autocommit = True
cur = conn.cursor()

try:
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tenants (
        tenant_id VARCHAR(255) PRIMARY KEY,
        email VARCHAR(255) UNIQUE,
        password_hash VARCHAR(255),
        plan VARCHAR(50) DEFAULT 'free',
        max_agents INTEGER DEFAULT 5,
        max_memories INTEGER DEFAULT 10000,
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        company VARCHAR(255),
        use_case VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        active BOOLEAN DEFAULT TRUE,
        verified INTEGER DEFAULT 1
    )''')
    print("Created tenants table")
except Exception as e:
    print("Error creating tenants:", e)
    
try:
    cur.execute('''
    CREATE TABLE IF NOT EXISTS api_keys (
        key_hash VARCHAR(255) PRIMARY KEY,
        tenant_id VARCHAR(255) REFERENCES tenants(tenant_id),
        active BOOLEAN DEFAULT TRUE,
        last_used TIMESTAMP
    )''')
    print("Created api_keys table")
except Exception as e:
    print("Error creating api_keys:", e)

# Insert dev tenant
try:
    cur.execute("INSERT INTO tenants (tenant_id, email, plan, max_agents, max_memories) VALUES ('dev', 'dev@localhost', 'pro', 100, 100000) ON CONFLICT DO NOTHING")
    print("Inserted dev tenant")
except Exception as e:
    print("Error inserting dev tenant:", e)
