import os
import time
import requests
import concurrent.futures

agents = ["orchestrator", "Agent_Analyst", "Agent_Copywriter", "Agent_FactChecker", "Agent_Interviewer", "Agent_Visual_Director"]

def simulate_agent(agent_id):
    print(f"[{agent_id}] Starting simulation...")
    for i in range(5):
        key = f"task:test_run_{int(time.time())}_{i}"
        val = {
            "instruction": f"Генерация тестового промпта #{i} для {agent_id}", 
            "status": "processing", 
            "progress": i * 20,
            "complexity": "high"
        }
        
        try:
            resp = requests.post(
                f"http://localhost:8741/v1/agents/{agent_id}/remember",
                json={"key": key, "value": val, "tags": ["test", "simulation"]},
                headers={"Authorization": "Bearer local-dev"}
            )
            if resp.status_code == 200:
                print(f"  [{agent_id}] Added memory: {key}")
            else:
                print(f"  [{agent_id}] HTTP {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"  [{agent_id}] ERR: {e}")
            
        time.sleep(0.5)

print("Starting parallel prompt simulation (sending via REST API)...")
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    executor.map(simulate_agent, agents)

print("Simulation complete! Check the Atlas graph in the dashboard.")
