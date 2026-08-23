import re
with open(r'C:\Python314\Lib\site-packages\synrix_runtime\dashboard\static\assets\index-DTLPD_iM.js', 'r', encoding='utf-8') as f:
    content = f.read()
matches = re.findall(r'[\"\'\`](/v1/[a-zA-Z0-9_/-]+|/api/[a-zA-Z0-9_/-]+)[\"\'\`]', content)
print("Routes:", list(set(matches)))

# Look for how base URL is defined
idx = content.find('api_key')
if idx != -1: print('api_key around:', content[max(0, idx-100):min(len(content), idx+100)])
idx = content.find('tenant_id')
if idx != -1: print('tenant_id around:', content[max(0, idx-100):min(len(content), idx+100)])
