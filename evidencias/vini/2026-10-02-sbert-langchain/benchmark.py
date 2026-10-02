"""Run inside isolated backend venv; input bundle and output directory arguments."""
import os
os.environ.update(LANGSMITH_TRACING='false', LANGCHAIN_TRACING_V2='false', ANONYMIZED_TELEMETRY='false', TOKENIZERS_PARALLELISM='false')
import sys, json, time, hashlib, resource, platform, importlib.metadata
from pathlib import Path
import torch
torch.set_num_threads(4)
torch.set_num_interop_threads(1)
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from langchain_core.embeddings import Embeddings as LCEmbeddings
from langchain_core.runnables import RunnableLambda
from langchain_chroma import Chroma
from app.clients.retrieval_client import RetrievalClient, logger
from app.models.retrieved_document import RetrievedDocument
from app.core.config import settings
from app.pipeline.config_resolver import resolve
from app.prompts.triage import build_triage_messages
logger.disabled = True

bundle, model_key, destination = sys.argv[1:]
data=json.loads(Path(bundle).read_text())
output=Path(destination); output.mkdir(parents=True,exist_ok=True)
model_name, revision = data['models'][model_key]
start=time.perf_counter()
model=SentenceTransformer(model_name, revision=revision, device='cpu', local_files_only=True)
load_seconds=time.perf_counter()-start

class Embed(EmbeddingFunction[Documents]):
    def __call__(self, input: Documents) -> Embeddings:
        return model.encode(input, batch_size=8, show_progress_bar=False).tolist()
    def name(self): return 'isolated-sentence-transformer'
    def get_config(self): return {}

class LCEmbed(LCEmbeddings):
    def embed_documents(self, texts): return Embed()(texts)
    def embed_query(self, text): return Embed()([text])[0]

client=chromadb.PersistentClient(path=str(output/'chroma'),settings=ChromaSettings(anonymized_telemetry=False))
collection=client.create_collection('comparison',embedding_function=Embed(),configuration={'hnsw':{'space':'cosine'}})
cards=data['cards']
metas=[dict(title=c['reading_title'],body=c['reading_text'],topic=c['topic'],species=c['species'],display_title=c['display_title'],source='Ficha de triagem do time (mapa de assuntos)',references=json.dumps(c['references'],ensure_ascii=False)) for c in cards]
start=time.perf_counter()
collection.add(ids=['ficha__'+c['topic'] for c in cards],documents=[c['search_text'] for c in cards],metadatas=metas)
index_seconds=time.perf_counter()-start
store=Chroma(client=client,collection_name='comparison',embedding_function=LCEmbed(),create_collection_if_not_exists=False)
cfg=resolve(settings)

def native(query): return RetrievalClient.retrieve([query],collection=collection)
def wrapped(query):
    rows=store.similarity_search_with_score(query,k=min(max(settings.TOP_K*10,settings.TOP_K),len(cards)))
    docs=[]
    for doc,distance in rows:
        m=doc.metadata
        docs.append(RetrievedDocument(id=doc.id,chunk_id=doc.id,title=m['title'],content=m['body'],source=m['source'],score=1-float(distance),topic=m['topic'],species=m['species'],display_title=m['display_title'],references=tuple(json.loads(m['references']))))
    return sorted(docs,key=lambda d:d.score,reverse=True)
def finish(query,docs):
    prompt=build_triage_messages(query,docs[:3],cfg)
    return docs,hashlib.sha256(json.dumps(prompt,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
chain=RunnableLambda(lambda query: (query,wrapped(query))) | RunnableLambda(lambda pair: finish(*pair))
arms={'native':lambda q:finish(q,native(q)), 'langchain':chain.invoke}
for fn in arms.values(): fn(data['cases'][0]['text'])
with (output/'queries.jsonl').open('w') as handle:
    for repeat in range(3):
        for i,case in enumerate(data['cases']):
            order=list(arms) if (i+repeat)%2==0 else list(reversed(arms))
            for arm in order:
                start=time.perf_counter(); docs,prompt_hash=arms[arm](case['text']); elapsed=time.perf_counter()-start
                row=dict(model=model_key,arm=arm,repeat=repeat,id=case['id'],dataset=case['dataset'],expected=case['expected'],seconds=elapsed,topics=[d.topic for d in docs],scores=[d.score for d in docs],ids=[d.id for d in docs],prompt_sha256=prompt_hash)
                handle.write(json.dumps(row,ensure_ascii=False)+'\n'); handle.flush()
        print(model_key,'repeat',repeat+1,'complete',flush=True)
lengths=[len(model.tokenizer.encode(c['search_text'],truncation=False)) for c in cards]
metadata=dict(model=model_name,revision=revision,load_seconds=load_seconds,index_seconds=index_seconds,dimensions=model.get_sentence_embedding_dimension(),max_seq_length=model.max_seq_length,card_token_lengths=lengths,cards_truncated=sum(n>model.max_seq_length for n in lengths),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,platform=platform.platform(),torch_threads=torch.get_num_threads(),config=cfg.model_dump(),versions={p:importlib.metadata.version(p) for p in ['sentence-transformers','torch','chromadb','langchain-core','langchain-chroma','transformers']},vector_bytes=len(cards)*model.get_sentence_embedding_dimension()*4)
(output/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
print(json.dumps(metadata,ensure_ascii=False),flush=True)
