1. RAG over public SEC filings where every claim is checked against its cited passage; unsupported claims get flagged.

2. Result:
   Questions evaluated: 50  
   Citation support before filter: 0.5  
   Seeded unsupported claims caught: 25  

   Measured with `make bench`: [raw results](evidence/bench.json), [command output](evidence/checks.log), [environment](evidence/environment.json).

3. Architecture:
```mermaid
flowchart LR
    PublicSECXBRLFacts --> SparseEmbeddings --> Retrieval --> ExtractiveAnswer --> CitationChecker
```

4. Run it:
```sh
make setup
make lint test bench
make demo
```

5. Decisions and limits: Public SEC financial facts, not personal financial records; source URL, retrieval hash and accession numbers are in data/. The SEC HTML endpoint returned 403; the documented data.sec.gov API succeeded. This is extractive RAG with character-ngram TF-IDF embeddings, not a neural financial analyst or generative LLM evaluation. Fifty template questions use distinct reported concepts; unsupported values are deliberately injected into half the answers to test checking. The checker validates concept, context, value, unit and scale against the cited structured fact; it cannot establish broader semantic claims. Retrieval accuracy and retained support are reported separately in bench.json. Examples are evidence/caught-claims.json. No investment advice or company affiliation.

6. Next: Add human-authored questions over narrative filing passages and a separately evaluated semantic entailment checker.
