import tempfile,unittest
from pathlib import Path
from app.db import rebuild_demo_db
from app.router import route,extract_entities,route_with_reason
from app.sql_tools import get_stock,get_purchase_order,get_sales_order,recent_movements,explain_tool
from app.diagnostics import diagnose_purchase,diagnose_sales
from app.uat import generate_uat
from app.rag import Retriever
from app.copilot import ask

class TestCopilot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(); cls.db=Path(cls.tmp.name)/'erp.db'; rebuild_demo_db(cls.db)
    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()
    def test_entities(self): self.assertEqual(extract_entities('po100 和 sku2')['po_id'],'PO100'); self.assertEqual(extract_entities('po100 和 sku2')['sku'],'SKU002')
    def test_route_po(self): self.assertEqual(route('PO100为什么还是部分验收？')[0],'purchase_diagnosis')
    def test_route_so(self): self.assertEqual(route('SO100为什么不能出库？')[0],'sales_diagnosis')
    def test_route_uat(self): self.assertEqual(route('这个需求怎么做UAT？')[0],'uat')
    def test_stock(self): self.assertEqual(get_stock('SKU001',self.db)['stock_qty'],3)
    def test_po(self): self.assertEqual(get_purchase_order('PO100',self.db)['remaining_qty'],2)
    def test_so(self): self.assertEqual(get_sales_order('SO100',self.db)['qty'],5)
    def test_movement(self): self.assertEqual(recent_movements('SKU002',5,self.db)[0]['source_id'],'SO101')
    def test_po_diag(self): self.assertIn('剩余2件',diagnose_purchase('PO100',self.db)['reason'])
    def test_so_diag(self): self.assertIn('当前可用库存3件',diagnose_sales('SO100',self.db)['reason'])
    def test_uat_partial_receipt(self): self.assertEqual(len(generate_uat('新增分批验收功能')['cases']),6)
    def test_uat_over_receive(self): self.assertTrue(any('拒绝' in c['expected'] for c in generate_uat('新增分批验收功能')['cases']))
    def test_rag_inventory(self):
        hits=Retriever().search('为什么库存余额还需要库存流水？',3)
        self.assertTrue(hits); self.assertIn('库存',hits[0]['text'])
    def test_end_to_end_po(self): self.assertEqual(ask('PO100为什么还是部分验收？',self.db)['route'],'purchase_diagnosis')
    def test_end_to_end_so(self): self.assertIn('库存不足',ask('SO100为什么不能出库？',self.db)['reason'])
    def test_end_to_end_sku(self): self.assertEqual(ask('SKU002库存多少？',self.db)['record']['stock_qty'],16)
    def test_end_to_end_knowledge(self): self.assertTrue(ask('为什么库存余额还需要库存流水？',self.db)['evidence'])
    def test_end_to_end_uat(self): self.assertEqual(ask('分批验收怎么做UAT？',self.db)['type'],'uat')

    def test_route_trace(self):
        kind,ent,trace=route_with_reason('SO100为什么不能出库？')
        self.assertEqual(kind,'sales_diagnosis'); self.assertEqual(trace['matched_rule'],'sales_order_diagnosis')
    def test_route_entity_fallback(self): self.assertEqual(route('PO100')[0],'purchase_diagnosis')
    def test_sql_explainability(self):
        x=explain_tool('get_purchase_order',{'po_id':'PO100'}); self.assertIn('purchase_orders',x['tables']); self.assertTrue(x['join'])
    def test_diag_checks(self): self.assertTrue(all(c['pass'] for c in diagnose_purchase('PO100',self.db)['checks']))
    def test_sales_decision(self): self.assertEqual(diagnose_sales('SO100',self.db)['decision']['result'],'BLOCK')
    def test_uat_has_idempotency(self): self.assertTrue(any(c['kind']=='idempotency' for c in generate_uat('新增分批验收功能')['cases']))
    def test_rag_trace(self):
        r=ask('库存台账为什么要保留？',self.db); self.assertEqual(r['route'],'knowledge'); self.assertIn('retrieval_trace',r); self.assertTrue(r['evidence'])
    def test_tool_trace_sku(self): self.assertTrue(ask('SKU002库存多少？',self.db)['tool_trace'])
    def test_uat_generic_no_crash(self):
        r=generate_uat('新增一个必填字段')
        self.assertEqual(r['requirement_type'],'generic')
        self.assertEqual(len(r['cases']),5)
        self.assertTrue(any(c['kind']=='invalid' for c in r['cases']))

if __name__=='__main__': unittest.main()
