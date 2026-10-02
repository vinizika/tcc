"""Reproducible local validation orchestration, preserving earlier packages."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path('/Users/vinicius/Documents/tcc')
OUT = ROOT / 'evidencias/vini/2026-10-02-testes-vetia'
PREV = ROOT / 'evidencias/vini/2026-10-02-correcao-conversacional-v2'
PY = str(ROOT / '.venv/bin/python')
NODE = '/Users/vinicius/.npm/_npx/52027bd8fc0022aa/node_modules/node/bin/node'

def dump(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def run(name, command, cwd=ROOT, extra=None):
    start = time.monotonic()
    with (OUT / (name + '.log')).open('w') as log:
        result = subprocess.run(command, cwd=cwd, env=dict(os.environ, DEBUG='true', **(extra or {})), stdout=log, stderr=subprocess.STDOUT)
    row = dict(name=name, command=command, cwd=str(cwd), exit_code=result.returncode, wall_s=time.monotonic()-start)
    with (OUT / 'commands.jsonl').open('a') as output:
        output.write(json.dumps(row) + '\n')
    print(name, result.returncode, round(row['wall_s'], 2), flush=True)
    return result.returncode

def setup():
    if (OUT / 'snapshot.json').exists():
        raise SystemExit('Snapshot already exists; refusing to overwrite')
    for name in ('cases.json', 'baseline_workspace.py', 'freeze.json'):
        shutil.copyfile(PREV / name, OUT / name)
    paths = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines()
    paths += ['frontend-react/src/components/TriageGuidance.tsx', 'frontend-react/tests/triage-guidance.spec.ts']
    selected = [p for p in paths if p.startswith(('backend/app/', 'backend/data/', 'frontend-react/src/', 'frontend-react/tests/', 'scripts/')) or p in ('frontend-react/index.html', 'frontend-react/package-lock.json', 'backend/chroma_db/active_collection.json')]
    dump('snapshot.json', {'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'files':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in selected if (ROOT/p).is_file()},
        'diff': subprocess.check_output(['git','diff','--','backend/app','frontend-react','frontend'],cwd=ROOT,text=True)})
    run('freeze-audit', [PY,'scripts/audit_conversation_eval.py',str(OUT),'--previous',str(PREV),'--freeze'])

def checks():
    commands = [(name,[PY,'-m','pytest','-q',path],ROOT) for name,path in [('backend','backend/tests'),('scripts','scripts/tests'),('mock','mock/tests')]]
    commands += [('typescript',[NODE,'node_modules/typescript/bin/tsc','-b'],ROOT/'frontend-react'),
                 ('vite',[NODE,'node_modules/vite/bin/vite.js','build'],ROOT/'frontend-react'),
                 ('fichas',[PY,'scripts/sync_fichas.py','--check'],ROOT),
                 ('vocabulario',[PY,'scripts/sync_retrieval_terms.py','--check'],ROOT)]
    failures = [name for name,cmd,cwd in commands if run(name,cmd,cwd)]
    dump('check-failures.json', failures)

def clinical():
    code = run('calibration', [PY,'scripts/run_conversation_eval.py','--phase','baseline','--output-dir',str(OUT),'--mongo-database','tcc_eval_vetia_20261002'])
    if code:
        raise SystemExit(code)
    code = run('api-smoke',[PY,'scripts/smoke_workspace_followup.py','--provider','gemini','--output',str(OUT/'api-smoke.json')])
    if code:
        raise SystemExit(code)
    cases = json.loads((OUT/'api-smoke.json').read_text())
    expected = {'immediate':'EMERGENCIA','resolved':'EMERGENCIA','form':'INCERTO','form_severe':'EMERGENCIA'}
    rows = []
    for case in cases:
        last = next((m for m in reversed(case['messages']) if m['role']=='assistant'), {})
        tutor = next(m for m in reversed(case['messages']) if m['role']=='tutor')
        rows.append(dict(scenario=case['scenario'], expected=expected[case['scenario']], status=case['status'],
            classification=last.get('triage',{}).get('classificacao'),state=(case.get('followup') or {}).get('state'),
            last_tutor_origin=tutor.get('origin'),last_tutor_content=tutor['content']))
    dump('api-assertions.json',rows)

def browser():
    source=OUT/'api-smoke.json'
    if not source.exists():
        source=ROOT/'evidencias/vini/2026-10-02-validacao-final/api-smoke.json'
    cases=json.loads(source.read_text())
    dump('browser-live-input.json',{'source':str(source),'conversation_id':cases[0]['conversation_id'],
                                  'note':'Existing real API conversation; no clinical HTTP fixtures in workspace tests'})
    raise SystemExit(run('browser',[NODE,'node_modules/@playwright/test/cli.js','test','--reporter=list,json'],ROOT/'frontend-react',
        {'APP_URL':'http://localhost:3000','LIVE_RAG_CONVERSATION_ID':cases[0]['conversation_id'],
         'PLAYWRIGHT_JSON_OUTPUT_NAME':str(OUT/'browser-tests.json')}))

def manual():
    raise SystemExit(run('manual',[PY,str(OUT/'run_manual.py')]))

if __name__ == '__main__':
    {'setup':setup,'checks':checks,'clinical':clinical,'browser':browser,'manual':manual}[sys.argv[1]]()
