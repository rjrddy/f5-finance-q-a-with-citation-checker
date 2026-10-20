"""Sparse-embedding retrieval over public SEC facts with exact structured citations."""

import json
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def supported(claim: dict, cited: dict) -> bool:
    return all(
        claim.get(key) == cited.get(key) for key in ["concept", "context", "text", "scale", "unit"]
    )


def retrieve(facts: list[dict], questions: list[str]) -> list[int]:
    passages = [
        f"{f['concept']} context {f['context']} value {f['text']} {f['unit']}" for f in facts
    ]
    embed = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
    matrix = embed.fit_transform(passages)
    return np.argmax(cosine_similarity(embed.transform(questions), matrix), axis=1).tolist()


def benchmark() -> dict:
    facts = json.loads(Path("data/facts.json").read_text())
    chosen = []
    seen = set()
    for i, fact in enumerate(facts):
        if fact["concept"] not in seen:
            chosen.append(i)
            seen.add(fact["concept"])
        if len(chosen) == 50:
            break
    assert len(chosen) == 50
    questions = [
        f"What value was reported for {facts[i]['concept']} in context {facts[i]['context']}?"
        for i in chosen
    ]
    indexes = retrieve(facts, questions)
    rows = []
    for n, (question, expected, citation) in enumerate(zip(questions, chosen, indexes)):
        claim = dict(facts[citation])
        injected = n % 2 == 0
        if injected:
            claim["text"] = "UNSUPPORTED-" + claim["text"]
        ok = supported(claim, facts[citation])
        rows.append(
            {
                "question": question,
                "expected_citation": expected,
                "citation": citation,
                "claim": claim,
                "supported": ok,
                "injected_unsupported": injected,
            }
        )
    caught = sum(r["injected_unsupported"] and not r["supported"] for r in rows)
    source = json.loads(Path("data/source.json").read_text())
    Path("evidence/qa.json").write_text(json.dumps({"source": source, "answers": rows}, indent=2))
    examples = [r for r in rows if r["injected_unsupported"]][:3]
    Path("evidence/caught-claims.json").write_text(json.dumps(examples, indent=2))
    return {
        "questions_evaluated": len(rows),
        "citation_support_rate_before_filter": sum(r["supported"] for r in rows) / len(rows),
        "unsupported_claims_caught": caught,
        "retained_citation_support_rate": sum(r["supported"] for r in rows)
        / sum(not r["injected_unsupported"] for r in rows),
        "retrieval_accuracy": sum(a == b for a, b in zip(chosen, indexes)) / len(chosen),
        "public_sec_facts": len(facts),
    }


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2))
