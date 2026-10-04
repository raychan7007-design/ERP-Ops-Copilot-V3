from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path
from .config import KNOWLEDGE_DIR

@dataclass
class Chunk:
    chunk_id: str
    source: str
    title: str
    text: str

def load_chunks(root: Path = KNOWLEDGE_DIR):
    chunks=[]
    for path in sorted(root.glob('*.md')):
        content=path.read_text(encoding='utf-8')
        sections=re.split(r'(?m)^##\s+', content)
        intro=sections[0].strip()
        if intro:
            chunks.append(Chunk(f'{path.stem}:intro',path.name,path.stem,intro))
        for idx,sec in enumerate(sections[1:],1):
            lines=sec.strip().splitlines()
            if not lines: continue
            title=lines[0].strip()
            body='\n'.join(lines[1:]).strip()
            chunks.append(Chunk(f'{path.stem}:{idx}',path.name,title,body))
    return chunks
