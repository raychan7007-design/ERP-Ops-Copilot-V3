from __future__ import annotations
import math,re
from collections import Counter,defaultdict
from .knowledge import load_chunks
from .config import DEFAULT_TOP_K

TOKEN_RE=re.compile(r'[A-Za-z0-9_\-]+|[\u4e00-\u9fff]')
STOP=set('的了是在和与及或把被一个一种进行通过如果那么可以需要当前系统业务用户'.strip())

# Domain query expansion is deliberately small and inspectable. It improves
# retrieval on common ERP paraphrases without pretending to be semantic embedding.
DOMAIN_EXPANSIONS={
    '收货':['验收','到货','入库'],
    '到货':['验收','收货','入库'],
    '入库':['验收','库存'],
    '库存台账':['库存流水','追溯'],
    '库存变化':['库存流水','追溯'],
    '库存为什么':['库存流水','追溯'],
    '超卖':['库存不足','销售出库'],
    '缺货':['库存不足','安全库存'],
    '补货':['安全库存','低库存'],
    '角色':['权限','越权'],
    '验收测试':['UAT','测试场景'],
    '用户验收':['UAT','测试场景'],
    'fitgap':['Fit-Gap','AS-IS','TO-BE'],
    'fit-gap':['AS-IS','TO-BE','差异'],
    '差异分析':['Fit-Gap','AS-IS','TO-BE'],
    '先收':['分批验收','部分验收','累计验收'],
    '分两次':['分批验收','部分验收','累计验收'],
    '挂在采购单':['采购订单','验收关联'],
}

def expand_query(text:str):
    lower=text.lower().replace(' ','')
    additions=[]
    for phrase,terms in DOMAIN_EXPANSIONS.items():
        if phrase.lower().replace(' ','') in lower:
            additions.extend(terms)
    return text+' '+' '.join(dict.fromkeys(additions)) if additions else text

def tokenize(text:str):
    raw=[t.lower() for t in TOKEN_RE.findall(text)]
    cn=[t for t in raw if len(t)==1 and '\u4e00'<=t<='\u9fff']
    other=[t for t in raw if not (len(t)==1 and '\u4e00'<=t<='\u9fff')]
    bigrams=[cn[i]+cn[i+1] for i in range(len(cn)-1)]
    return [t for t in other+cn+bigrams if t not in STOP and t.strip()]

class Retriever:
    def __init__(self,chunks=None):
        self.chunks=chunks or load_chunks()
        self.docs=[tokenize(c.title+' '+c.text) for c in self.chunks]
        n=max(1,len(self.docs)); df=defaultdict(int)
        for toks in self.docs:
            for t in set(toks): df[t]+=1
        self.idf={t:math.log((n+1)/(d+1))+1 for t,d in df.items()}
        self.vecs=[self._vec(toks) for toks in self.docs]
    def _vec(self,toks):
        c=Counter(toks); return {t:(1+math.log(v))*self.idf.get(t,1) for t,v in c.items()}
    @staticmethod
    def _cos(a,b):
        num=sum(v*b.get(k,0) for k,v in a.items())
        da=math.sqrt(sum(v*v for v in a.values())); db=math.sqrt(sum(v*v for v in b.values()))
        return num/(da*db) if da and db else 0.0
    def search(self,query,top_k=DEFAULT_TOP_K):
        expanded=expand_query(query)
        q_tokens=tokenize(expanded); q=self._vec(q_tokens); scored=[]
        q_lower=expanded.lower().replace(' ', '')
        noisy={'为什么','为什','什么','怎么','如何','需要','可以','不能','下面','一个'}
        query_terms={t for t in q_tokens if len(t)>1 and t not in noisy}
        for chunk,vec,doc_tokens in zip(self.chunks,self.vecs,self.docs):
            base=self._cos(q,vec); boost=0.0
            title=chunk.title.lower().replace(' ', '')
            hay=(chunk.title+' '+chunk.text).lower().replace(' ', '')
            matched=[]
            for token in query_terms:
                if token in hay:
                    boost += 0.12 if len(token)==2 else 0.22
                    if token in title:
                        boost += 0.10
                    matched.append(token)
            if 'fit-gap' in q_lower and 'fit-gap' in hay: boost += 0.6
            score=base+min(boost,0.9)
            if score>0:
                scored.append((score,base,boost,chunk,sorted(set(matched))))
        scored.sort(key=lambda x:x[0],reverse=True)
        out=[]
        for rank,(score,base,boost,c,matched) in enumerate(scored[:top_k],1):
            out.append(dict(rank=rank,score=round(score,4),base_score=round(base,4),keyword_boost=round(boost,4),
                            chunk_id=c.chunk_id,source=c.source,title=c.title,text=c.text,matched_terms=matched,
                            expanded_query=expanded))
        return out

def _confidence(top_score:float,second_score:float|None):
    if top_score < 0.18: return 'low'
    margin=top_score-(second_score or 0)
    if top_score >= 0.75 and margin>=0.08: return 'high'
    if top_score >= 0.35: return 'medium'
    return 'low'

def answer_from_knowledge(query,top_k=3):
    hits=Retriever().search(query,top_k)
    if not hits:
        return {"answer":"知识库中没有足够依据，建议补充具体业务对象或单据编号。","evidence":[],"confidence":"low","retrieval_trace":{"expanded_query":expand_query(query),"top_k":top_k}}
    confidence=_confidence(hits[0]['score'],hits[1]['score'] if len(hits)>1 else None)
    if hits[0]['score'] < 0.12:
        return {"answer":"知识库检索到的依据相关性过低，暂不直接给出业务结论。建议补充更具体的流程、规则或单据关键词。","evidence":[],"confidence":"low","retrieval_trace":{"expanded_query":hits[0]['expanded_query'],"top_hits":[{k:h[k] for k in ('rank','chunk_id','score','matched_terms')} for h in hits]}}
    evidence=[]; snippets=[]
    for h in hits:
        parts=[x.strip() for x in re.split(r'(?<=[。；;])\s*|\n+',h['text']) if x.strip()]
        excerpt=' '.join(parts[:2]) if parts else h['title']
        snippets.append(f"{h['title']}：{excerpt}")
        evidence.append({"source":h['source'],"title":h['title'],"chunk_id":h['chunk_id'],"rank":h['rank'],"score":h['score'],"matched_terms":h['matched_terms'],"excerpt":excerpt})
    return {"answer":"；".join(snippets[:3]),"evidence":evidence,"confidence":confidence,
            "retrieval_trace":{"expanded_query":hits[0]['expanded_query'],"top_k":top_k,"top_hits":[{k:h[k] for k in ('rank','chunk_id','score','base_score','keyword_boost','matched_terms')} for h in hits]}}
