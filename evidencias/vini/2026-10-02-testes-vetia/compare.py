"""Offline comparison of frozen historical and current observations."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from report_conversation_eval import summarize, paired, distribution

def read_turns(directory):
    return [json.loads(line) for line in (directory/'raw.jsonl').read_text().splitlines()]

def main():
    current = read_turns(OUT)
    summary = summarize(current)
    result = {'current':summary,'historical':{},'comparisons':{},
              'scope':'72 paired calibration decisions; four API scenarios; separate manual exploration; no human usability study'}
    def after(records):
        return [r for r in records if r['kind']=='turn' and r['phase']=='baseline' and r['arm']=='after']
    for key,folder in [('original_pr16','2026-09-28-avaliacao-conversacional'),
                       ('corrected_v2','2026-10-02-correcao-conversacional-v2')]:
        records=read_turns(OUT.parent/folder)
        result['historical'][key]=summarize(records)['calibration']
        result['comparisons'][key+'_to_current']=paired(after(records),after(current))
        if key=='corrected_v2':
            old={(r['case_id'],r['repetition']):r for r in after(records)}
            def prompt_hash(row):
                return [c.get('input_sha256') for c in row['calls'] if c['stage']=='classification']
            result['identical_classification_inputs_to_v2']=[{
                'case_id':r['case_id'],'repetition':r['repetition'],
                'identical':prompt_hash(r)==prompt_hash(old[(r['case_id'],r['repetition'])])}
                for r in after(current)]
    manual=[json.loads(line) for line in (OUT/'manual-raw.jsonl').read_text().splitlines()]
    result['manual_exploration']={}
    for case_id in sorted({r['case_id'] for r in manual}):
        for turn in sorted({r['turn'] for r in manual if r['case_id']==case_id}):
            rows=[r for r in manual if r['case_id']==case_id and r['turn']==turn]
            findings=[]
            for r in rows:
                last=next((m for m in reversed(r['messages']) if m['role']=='assistant'),{})
                findings.append({'repetition':r['repetition'],'status':r['status'],
                    'classification':last.get('triage',{}).get('classificacao') if r['status']=='idle' else None,
                    'sources':[s['title'] for s in last.get('sources',[])],
                    'model':(last.get('provenance') or {}).get('attendant'),
                    'timings':last.get('timings')})
            result['manual_exploration'][f'{case_id}_turn_{turn}']={
                'classifications':dict(Counter(r['classification'] for r in findings)),
                'wall_including_polling_s':distribution([r['wall_s_including_polling'] for r in rows]),
                'observations':findings}
    def api_results(directory):
        data=json.loads((directory/'api-smoke.json').read_text())
        return [{ 'scenario':r['scenario'],'status':r['status'],
            'classification':next((m['triage']['classificacao'] for m in reversed(r['messages']) if m.get('triage')),None),
            'state':(r.get('followup') or {}).get('state'),
            'turns':sum(m['role']=='tutor' for m in r['messages'])} for r in data]
    result['api_current']=api_results(OUT)
    result['api_previous']=api_results(OUT.parent/'2026-10-02-validacao-final')
    assertions=json.loads((OUT/'api-assertions.json').read_text())
    result['api_failures']=[r['scenario'] for r in assertions if r['status']!='idle' or r['classification']!=r['expected']
        or (r['scenario']=='form' and r['state']!='insufficient')
        or (r['scenario']!='form' and r['state']!='completed')
        or (r['scenario']=='form_severe' and (r['last_tutor_origin']!='form' or r['last_tutor_content']!='Não sai nenhum xixi'))]
    result['browser_current']=json.loads((OUT/'browser-tests.json').read_text())['stats']
    result['browser_previous']=json.loads((OUT.parent/'2026-10-02-validacao-final/browser-tests.json').read_text())['stats']
    snap=json.loads((OUT/'snapshot.json').read_text())
    result['source_changes_during_run']=[p for p,sha in snap['files'].items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=sha]
    prev=json.loads((OUT.parent/'2026-10-02-correcao-conversacional-v2/code-and-data-fingerprint.json').read_text())
    result['backend_changed_since_v2']=[p for p,sha in prev['files'].items() if p.startswith('backend/app/') and hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=sha]
    (OUT/'comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('current','historical','manual_exploration','identical_classification_inputs_to_v2')},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
