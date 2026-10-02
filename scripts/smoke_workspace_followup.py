"""Opt-in real API smoke test. Creates synthetic cases in the academic tutor account.
Never substitutes model responses. Output contains synthetic reports, not credentials.
"""
import argparse
import json
import time
from pathlib import Path
from uuid import uuid4
import httpx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--provider", choices=["gemini", "ollama"], default="gemini")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = []
    with httpx.Client(base_url=args.base_url, timeout=30, follow_redirects=True) as client:
        response = client.post("/auth/demo", json={"account": "tutor-a"})
        response.raise_for_status()
        client.headers["Authorization"] = "Bearer " + response.json()["access_token"]
        try:
            def submit(cid, content, metadata=None):
                response = client.post(f"/workspace/conversations/{cid}/messages", json={
                    "request_id": str(uuid4()), "content": content, "attendant_provider": args.provider,
                    **(metadata or {})})
                response.raise_for_status()
                deadline = time.monotonic() + 600
                while time.monotonic() < deadline:
                    response = client.get(f"/workspace/conversations/{cid}")
                    response.raise_for_status()
                    doc = response.json()
                    if doc["status"] != "processing":
                        return doc
                    time.sleep(2)
                raise TimeoutError("Analysis did not finish within 600 seconds")

            for name, report in [
                ("immediate", "Meu gato está respirando com a boca aberta e faz muita força para respirar mesmo parado."),
                ("resolved", "Meu gato está estranho, entra na caixa de areia muitas vezes. Não vi o que acontece lá."),
                ("form", "Meu gato está diferente hoje. Não consigo explicar o que mudou."),
                ("form_severe", "Meu gato está diferente quando vai à caixa de areia. Não consegui ver o que aconteceu.")]:
                response = client.post("/workspace/conversations", json={})
                response.raise_for_status()
                cid = response.json()["id"]
                doc = submit(cid, report)
                if name == "resolved" and doc.get("followup", {}).get("state") == "asking":
                    doc = submit(cid, "Ele tenta fazer xixi várias vezes e não sai nenhuma gota de urina.")
                if name in {"form", "form_severe"}:
                    for _ in range(5):
                        state = doc.get("followup", {})
                        if doc["status"] == "failed" or state.get("state") not in {"asking", "form"}:
                            break
                        if state["state"] == "form":
                            answer = "Não sai nenhum xixi" if name == "form_severe" else "Não observei"
                            if answer not in state["options"]:
                                raise AssertionError("Required truthful option absent from actual form")
                            doc = submit(cid, answer, {"origin": "form", "question_id": state["question_id"], "selected_option": answer})
                            break
                        doc = submit(cid, "Não sei dizer")
                results.append({"scenario": name, "provider_requested": args.provider,
                    "conversation_id": cid, "status": doc["status"], "error": doc.get("error"),
                    "followup": doc.get("followup"), "messages": doc["messages"]})
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
                print(name, doc["status"], doc.get("followup", {}).get("state"), flush=True)
        finally:
            client.post("/auth/logout")


if __name__ == "__main__":
    main()
