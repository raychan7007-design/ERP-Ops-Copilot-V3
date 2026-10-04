from __future__ import annotations
import argparse,json
from app.db import rebuild_demo_db
from app.copilot import ask

def main():
    parser=argparse.ArgumentParser(description='ERP Ops Copilot')
    parser.add_argument('question',nargs='?',help='Question to ask')
    parser.add_argument('--init-db',action='store_true',help='Rebuild demo database')
    args=parser.parse_args()
    if args.init_db: rebuild_demo_db()
    q=args.question or 'PO100为什么还是部分验收？'
    print(json.dumps(ask(q),ensure_ascii=False,indent=2))
if __name__=='__main__': main()
