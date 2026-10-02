"""Archive browser captures and verify snapshots without touching prior evidence."""
import hashlib
import json
from pathlib import Path
import re
import shutil
from datetime import datetime, timezone

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    snapshots=OUT/'screenshots'
    snapshots.mkdir(exist_ok=True)
    tests=ROOT/'frontend-react/test-results'
    for name in ('entry.png','chat.png','clinic.png','mobile-chat.png','mobile-map.png'):
        shutil.copyfile(tests/name,snapshots/name)
    for p in tests.glob('triage-guidance-*/guidance-mobile.png'):
        shutil.copyfile(p,snapshots/(p.parent.name+'.png'))
    history={}
    for directory in ('2026-10-02-correcao-conversacional-v2','2026-09-28-avaliacao-conversacional'):
        folder=OUT.parent/directory
        manifest=json.loads((folder/'final-integrity.json').read_text())
        history[directory]=all(digest(folder/name)==sha for name,sha in manifest['artifacts_sha256'].items())
    matches=[]
    pattern=re.compile(r'AIza[0-9A-Za-z_-]{30,}|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    for p in OUT.rglob('*'):
        if p.is_file() and p.suffix!='.png' and pattern.search(p.read_text(errors='replace')):
            matches.append(str(p.relative_to(OUT)))
    comparison=json.loads((OUT/'comparison.json').read_text())
    result={'utc':datetime.now(timezone.utc).isoformat(),'historical_artifacts_intact':history,
        'source_changes_during_run':comparison['source_changes_during_run'],
        'backend_changed_since_v2':comparison['backend_changed_since_v2'],
        'secret_pattern_matches':matches,
        'artifacts_sha256':{str(p.relative_to(OUT)):digest(p) for p in OUT.rglob('*') if p.is_file() and p.name!='integrity.json'}}
    (OUT/'integrity.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    assert all(history.values()) and not matches and not result['source_changes_during_run'],result
    print('Integrity verified; historical data preserved.')

if __name__=='__main__':
    main()
