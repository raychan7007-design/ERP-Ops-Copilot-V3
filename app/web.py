from __future__ import annotations
import html
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from .db import rebuild_demo_db
from .copilot import ask
from .config import APP_HOST,APP_PORT,APP_VERSION,MAX_QUERY_LENGTH

PAGE = '''<!doctype html><meta charset="utf-8"><title>ERP Ops Copilot</title>
<style>
body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:980px;margin:36px auto;padding:0 20px;line-height:1.6;background:#f6f8fa;color:#1f2328}
h1{margin-bottom:4px}.card{background:white;border:1px solid #d0d7de;border-radius:12px;padding:18px;margin:16px 0;box-shadow:0 1px 2px rgba(0,0,0,.03)}
textarea{width:100%;height:86px;font-size:16px;padding:10px;box-sizing:border-box;border:1px solid #afb8c1;border-radius:8px}button{padding:9px 16px;font-size:14px;border:0;border-radius:8px;background:#1f6feb;color:white;cursor:pointer}.muted{color:#656d76}.badge{display:inline-block;padding:2px 8px;border-radius:999px;background:#ddf4ff;color:#0969da;font-size:12px;margin-right:6px}.answer{font-size:17px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.mini{background:#f6f8fa;border-radius:8px;padding:10px}table{border-collapse:collapse;width:100%}th,td{border-bottom:1px solid #d8dee4;padding:7px;text-align:left;font-size:13px}pre{white-space:pre-wrap;background:#0d1117;color:#e6edf3;padding:14px;border-radius:8px;overflow:auto}details{margin-top:10px}.quick form{display:inline-block;margin:4px}.quick button{background:#fff;color:#0969da;border:1px solid #8c959f}
@media(max-width:700px){.grid{grid-template-columns:1fr}}
</style>
<h1>ERP Ops Copilot</h1><div class="muted">RAG知识检索 · SQL业务查询 · ERP异常诊断 · UAT辅助 · 可解释Trace</div>
<div class="card"><form method="post" action="/"><textarea name="q" placeholder="示例：PO100为什么还是部分验收？">{query}</textarea><br><button>提交</button></form>
<div class="quick"><span class="muted">快速演示：</span>{quick}</div></div>{result}'''

QUICK=['PO100为什么还是部分验收？','SO100为什么不能出库？','SKU002库存多少？','库存台账为什么要保留？','分批验收怎么做UAT？']

def esc(x): return html.escape(str(x))

def render_result(data):
    route=esc(data.get('route',''))
    answer=esc(data.get('answer') or data.get('reason') or '')
    parts=[f'<div class="card"><div><span class="badge">{route}</span></div><div class="answer"><b>回答：</b>{answer}</div>']
    if data.get('reason') and data.get('answer')!=data.get('reason'):
        parts.append(f'<p><b>诊断原因：</b>{esc(data["reason"])}</p>')
    if data.get('action'):
        parts.append(f'<p><b>建议动作：</b>{esc(data["action"])}</p>')
    if data.get('confidence'):
        parts.append(f'<p class="muted">知识检索置信度：{esc(data["confidence"])}</p>')
    checks=data.get('checks') or []
    if checks:
        rows=''.join(f"<tr><td>{esc(c['check'])}</td><td>{esc(c['actual'])}</td><td>{esc(c['expected'])}</td><td>{'PASS' if c['pass'] else 'FAIL'}</td></tr>" for c in checks)
        parts.append('<h3>诊断检查链</h3><table><tr><th>检查</th><th>实际</th><th>期望</th><th>结果</th></tr>'+rows+'</table>')
    uat=(data.get('uat') or {}).get('cases') or []
    if uat:
        rows=''.join(f"<tr><td>{esc(c['id'])}</td><td>{esc(c['kind'])}</td><td>{esc(c['scenario'])}</td><td>{esc(c['expected'])}</td></tr>" for c in uat)
        parts.append('<h3>UAT 场景</h3><table><tr><th>ID</th><th>类型</th><th>场景</th><th>预期</th></tr>'+rows+'</table>')
    evidence=data.get('evidence')
    if isinstance(evidence,list) and evidence:
        cards=''.join(f"<div class='mini'><b>{esc(e.get('title',''))}</b><br><span class='muted'>{esc(e.get('source',''))} · score={esc(e.get('score',''))}</span><br>{esc(e.get('excerpt',''))}</div>" for e in evidence)
        parts.append('<h3>知识依据</h3><div class="grid">'+cards+'</div>')
    tools=data.get('tool_trace') or []
    if tools:
        cards=''.join(f"<div class='mini'><b>{esc(t.get('tool',''))}</b><br>{esc(t.get('purpose',''))}<br><span class='muted'>{esc(t.get('tables',''))} {esc(t.get('join',''))}</span></div>" for t in tools)
        parts.append('<h3>Tool Trace</h3><div class="grid">'+cards+'</div>')
    route_trace=data.get('route_trace') or {}
    parts.append(f"<details><summary>查看路由与完整JSON</summary><p class='muted'>{esc(route_trace.get('reason',''))}</p><pre>{esc(json.dumps(data,ensure_ascii=False,indent=2))}</pre></details></div>")
    return ''.join(parts)

class Handler(BaseHTTPRequestHandler):
    def _send(self, status, content, ctype='application/json; charset=utf-8'):
        payload = content.encode('utf-8') if isinstance(content, str) else json.dumps(content, ensure_ascii=False, indent=2).encode('utf-8')
        self.send_response(status); self.send_header('Content-Type', ctype); self.send_header('Content-Length', str(len(payload))); self.end_headers(); self.wfile.write(payload)
    def _render(self, result='',query=''):
        quick=''.join(f'<form method="post" action="/"><input type="hidden" name="q" value="{esc(q)}"><button>{esc(q)}</button></form>' for q in QUICK)
        self._send(200, PAGE.format(result=result,query=esc(query),quick=quick), 'text/html; charset=utf-8')
    def do_GET(self):
        if urlparse(self.path).path == '/api/health':
            self._send(200, {'status': 'ok', 'service': 'erp-ops-copilot','version':APP_VERSION}); return
        self._render()
    def do_POST(self):
        path = urlparse(self.path).path; n = int(self.headers.get('Content-Length', '0')); raw = self.rfile.read(n)
        if path == '/api/query':
            try:
                body = json.loads(raw.decode('utf-8'))
                query = body.get('query', '')
                if not isinstance(query, str) or not query.strip(): raise ValueError('query must be a non-empty string')
                if len(query) > MAX_QUERY_LENGTH: raise ValueError(f'query exceeds max length {MAX_QUERY_LENGTH}')
                data = ask(query); self._send(200, data)
            except Exception as e: self._send(400, {'error': str(e)})
            return
        q = parse_qs(raw.decode('utf-8')).get('q', [''])[0]
        try: result=render_result(ask(q))
        except Exception as e: result='<div class="card"><b>错误：</b>'+esc(e)+'</div>'
        self._render(result,q)
    def log_message(self, *args): pass

def main():
    rebuild_demo_db(); print(f'ERP Ops Copilot {APP_VERSION}: http://{APP_HOST}:{APP_PORT}'); HTTPServer((APP_HOST, APP_PORT), Handler).serve_forever()
if __name__ == '__main__': main()
