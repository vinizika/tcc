"""Rebuild summary from the two immutable JSONL result files."""
import json, statistics, math
from pathlib import Path
root=Path(__file__).resolve().parent
def percentile(values,p):
    values=sorted(values); pos=(len(values)-1)*p; low=int(pos); high=math.ceil(pos)
    return values[low]+(values[high]-values[low])*(pos-low)
def rank(row):
    return next((i+1 for i,t in enumerate(row['topics']) if t in row['expected']),None)
summary={}
for model in ['bge','minilm']:
    rows=[json.loads(line) for line in (root/model/'queries.jsonl').read_text().splitlines()]
    assert len(rows)==1506, (model,len(rows))
    summary[model]={'metadata':json.loads((root/model/'metadata.json').read_text()),'groups':{},'equivalence':{}}
    pairs={(r['dataset'],r['id'],r['repeat'],r['arm']):r for r in rows}
    assert len(pairs)==len(rows)
    compared=[(r,pairs[(r['dataset'],r['id'],r['repeat'],'langchain')]) for r in rows if r['arm']=='native']
    assert all(r['topics']==pairs[(r['dataset'],r['id'],0,r['arm'])]['topics'] for r in rows), 'Unstable ranks across repeats'
    summary[model]['equivalence']={'pairs':len(compared),'same_topics':sum(a['topics']==b['topics'] for a,b in compared),'same_ids':sum(a['ids']==b['ids'] for a,b in compared),'same_prompt':sum(a['prompt_sha256']==b['prompt_sha256'] for a,b in compared),'max_score_difference':max(abs(x-y) for a,b in compared for x,y in zip(a['scores'],b['scores'])),'median_paired_overhead_ms':statistics.median((b['seconds']-a['seconds'])*1000 for a,b in compared)}
    for dataset in ['regua','dev','calibracao','independentes','all']:
        for arm in ['native','langchain']:
            group=[r for r in rows if (dataset=='all' or r['dataset']==dataset) and r['arm']==arm]
            unique=[r for r in group if r['repeat']==0]; ranks=[rank(r) for r in unique]
            timings=[r['seconds']*1000 for r in group]
            summary[model]['groups'][dataset+'/'+arm]={'n_cases':len(unique),'n_calls':len(group),**{f'hit{k}':sum(v is not None and v<=k for v in ranks) for k in [1,3,5]},'mrr50':sum(1/v if v else 0 for v in ranks)/len(ranks),'median_ms':statistics.median(timings),'p95_ms':percentile(timings,.95),'min_ms':min(timings),'max_ms':max(timings)}
            summary[model]['groups'][dataset+'/'+arm]['by_repeat']={str(repeat):{'median_ms':statistics.median(r['seconds']*1000 for r in group if r['repeat']==repeat),'p95_ms':percentile([r['seconds']*1000 for r in group if r['repeat']==repeat],.95)} for repeat in range(3)}
(root/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
baseline={(r['dataset'],r['id']):r for r in map(json.loads,(root/'bge/queries.jsonl').read_text().splitlines()) if r['arm']=='native' and r['repeat']==0}
candidate={(r['dataset'],r['id']):r for r in map(json.loads,(root/'minilm/queries.jsonl').read_text().splitlines()) if r['arm']=='native' and r['repeat']==0}
changes=[]
for key,a in baseline.items():
    b=candidate[key]; ra,rb=rank(a),rank(b)
    changes.append({'dataset':key[0],'id':key[1],'expected':a['expected'],'bge_rank':ra,'minilm_rank':rb,'bge_top3':a['topics'][:3],'minilm_top3':b['topics'][:3]})
(root/'case-comparison.json').write_text(json.dumps(changes,indent=2,ensure_ascii=False))
paired={}
for dataset in ['regua','dev','calibracao','independentes','all']:
    group=[c for c in changes if dataset=='all' or c['dataset']==dataset]
    def hit(row,key): return row[key] is not None and row[key]<=3
    paired[dataset]={'n':len(group),'minilm_gains':sum(hit(c,'minilm_rank') and not hit(c,'bge_rank') for c in group),'minilm_losses':sum(hit(c,'bge_rank') and not hit(c,'minilm_rank') for c in group),'hit3_delta_percentage_points':100*sum(int(hit(c,'minilm_rank'))-int(hit(c,'bge_rank')) for c in group)/len(group)}
(root/'paired-quality.json').write_text(json.dumps(paired,indent=2))
print(json.dumps({k:{'groups':v['groups'],'equivalence':v['equivalence']} for k,v in summary.items()},indent=2))
