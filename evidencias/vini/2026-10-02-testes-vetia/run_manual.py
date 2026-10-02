"""Real API reproduction of synthetic manual scenarios; no model substitution."""
import json
from pathlib import Path
import time
from uuid import uuid4
import httpx

DIRECTORY = Path(__file__).resolve().parent

def main():
    manifest = json.loads((DIRECTORY / 'manual-cases.json').read_text())
    output = DIRECTORY / 'manual-raw.jsonl'
    if output.exists():
        raise SystemExit('Refusing to overwrite prior manual observations')
    with httpx.Client(base_url='http://localhost:8000',timeout=30,follow_redirects=True) as client:
        login = client.post('/auth/demo',json={'account':'tutor-a'})
        login.raise_for_status()
        client.headers['Authorization'] = 'Bearer ' + login.json()['access_token']
        try:
            for repetition in range(manifest['repetitions']):
                for case in manifest['cases']:
                    response = client.post('/workspace/conversations',json={})
                    response.raise_for_status()
                    cid = response.json()['id']
                    for index, content in enumerate(case['turns']):
                        start = time.monotonic()
                        response=client.post(f'/workspace/conversations/{cid}/messages',json={
                            'request_id':str(uuid4()),'content':content,'attendant_provider':'gemini'})
                        response.raise_for_status()
                        while True:
                            response=client.get(f'/workspace/conversations/{cid}')
                            response.raise_for_status()
                            doc=response.json()
                            if doc['status']!='processing' or time.monotonic()-start>=600:
                                break
                            time.sleep(.5)
                        # Do not capture auth headers, account data or hidden model reasoning.
                        for message in doc['messages']:
                            if message.get('triage'):
                                message['triage'].pop('raciocinio',None)
                        row={'case_id':case['id'],'repetition':repetition,'turn':index+1,
                             'input':content,'wall_s_including_polling':time.monotonic()-start,
                             'status':doc['status'],'conversation_id':cid,
                             'messages':doc['messages'],'followup':doc.get('followup'),'error':doc.get('error')}
                        with output.open('a') as stream:
                            stream.write(json.dumps(row,ensure_ascii=False)+'\n')
                        last=next((m for m in reversed(doc['messages']) if m['role']=='assistant'),{})
                        print(case['id'],repetition,index+1,doc['status'],last.get('triage',{}).get('classificacao'),flush=True)
                        if doc['status']!='idle':
                            break
        finally:
            client.post('/auth/logout')

if __name__=='__main__':
    main()
