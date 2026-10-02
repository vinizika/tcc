"""Token-length diagnostics only; no model forward pass or external inference."""
import json,sys
from pathlib import Path
from transformers import AutoTokenizer
data=json.loads(Path(sys.argv[1]).read_text())
result={}
for key,(name,revision) in data['models'].items():
    tokenizer=AutoTokenizer.from_pretrained(name,revision=revision,local_files_only=True)
    limit=128 if key=='minilm' else 8192
    cases=[{'dataset':c['dataset'],'id':c['id'],'tokens':len(tokenizer.encode(c['text'],truncation=False))} for c in data['cases']]
    result[key]={'max_seq_length':limit,'queries_truncated':sum(c['tokens']>limit for c in cases),'cases':cases}
Path(sys.argv[2]).write_text(json.dumps(result,indent=2))
