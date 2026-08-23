import sqlite3

DB_PATH = r'C:\Users\Metal\.synrix\data\synrix.db'
db = sqlite3.connect(DB_PATH)

agents_to_delete = [
    'test-agent', 'Agent_A_Test', 'connection-test', 
    'test', 'Agent_B_Test', 'my-assistant'
]

total_deleted = 0
for agent in agents_to_delete:
    # Удаляем ноды из базы
    cur = db.execute(
        "DELETE FROM nodes WHERE name LIKE ? OR name LIKE ? OR name LIKE ?",
        (f'%:{agent}:%', f'{agent}:%', f'%:{agent}')
    )
    total_deleted += cur.rowcount
    
    # Также пытаемся удалить через json_extract
    try:
        cur = db.execute(
            "DELETE FROM nodes WHERE json_extract(data, '$.metadata.agent_id') = ?",
            (agent,)
        )
        total_deleted += cur.rowcount
    except Exception as e:
        pass # Если json_extract не поддерживается старой версией sqlite

db.commit()
db.close()
print(f'Successfully deleted {total_deleted} nodes related to test agents.')
