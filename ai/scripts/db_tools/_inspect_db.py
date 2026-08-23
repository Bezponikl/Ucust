import sqlite3, json

db = sqlite3.connect(r'C:\Users\Metal\.synrix\data\synrix.db', timeout=5)
db.row_factory = sqlite3.Row

# Таблицы
tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('Tables:', [t['name'] for t in tables])

# Агенты
for tname in ['agents', 'agent_profiles', 'agent_registry']:
    try:
        rows = db.execute(f'SELECT * FROM {tname} LIMIT 5').fetchall()
        if rows:
            print(f'\n[{tname}] ({len(rows)} rows):')
            for r in rows:
                print(' ', dict(r))
        break
    except Exception as e:
        print(f'  [{tname}] skip: {e}')

# Памяти
for tname in ['memories', 'memory_nodes', 'memory', 'nodes']:
    try:
        rows = db.execute(f'SELECT * FROM {tname} LIMIT 10').fetchall()
        if rows:
            print(f'\n[{tname}] columns: {rows[0].keys()}')
            print(f'  count: {len(rows)}')
            for r in rows[:3]:
                print(' ', {k: str(v)[:50] for k, v in dict(r).items()})
        break
    except Exception as e:
        print(f'  [{tname}] skip: {e}')

db.close()
