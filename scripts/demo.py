from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.db import rebuild_demo_db
from app.copilot import ask

rebuild_demo_db()
questions=[
    'PO100为什么还是部分验收？',
    'SO100为什么不能出库？',
    'SKU002现在库存多少，最近发生了什么？',
    '为什么库存余额还需要库存流水？',
    '新增分批验收功能，允许多次到货但累计不得超过采购数量，怎么做UAT？'
]
for q in questions:
    print('\n###',q)
    print(json.dumps(ask(q),ensure_ascii=False,indent=2))
