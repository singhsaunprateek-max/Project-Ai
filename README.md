# GraphMind Ultimate — Domain Knowledge Graph Builder & Semantic Reasoning Explorer

## Open in VS Code
1. Download and extract this ZIP.
2. Open the extracted `domain-knowledge-graph-builder-ultimate` folder in VS Code.
3. Open `index.html`.
4. Right-click and choose **Open with Live Server** (recommended), or open the HTML file in a modern browser.

No npm install, build process, API key, or backend is required.

## Pages and features
- Dashboard with live graph statistics and quick-start questions.
- Domain AI Assistant with a broad curated Q&A pack about knowledge graphs, semantic networks, ontologies, taxonomies, graph relations, inference, default reasoning, RDF, RDFS, OWL, SPARQL, Neo4j, Cypher, graph algorithms, graph embeddings, RAG, applications, project architecture, viva preparation, and more.
- Interactive graph explorer with selectable nodes and relationship inspector.
- Knowledge builder to add and remove entities and semantic edges.
- Inference engine for is-a transitivity, inherited properties, and part-of chains.
- Ontology Studio explaining semantic vocabulary and reasoning assumptions.
- Searchable knowledge library.
- MCQ quiz with answer feedback and score.
- JSON export and localStorage persistence.

## Important capability note
The assistant is an offline, rule-based and curated knowledge-base assistant. It answers questions covered by its bundled knowledge pack and current graph, and it explains when it cannot find enough evidence. It is not an unrestricted LLM and cannot guarantee an answer to every possible question. To add open-ended AI coverage, connect a language model API through a secure backend and use graph retrieval (RAG) to ground the generated answer in your knowledge base.

## Semantic model
- `is-a`: class membership / subclassing.
- `part-of`: component-to-whole.
- `has-property`: attribute relation.
- Additional association predicates can be added through the builder.
- Inference includes transitive is-a, property inheritance, and part-of closure.
- The reasoner page demonstrates defeasible defaults and exceptions.

## Files
```text
domain-knowledge-graph-builder-ultimate/
├── index.html
├── styles.css
├── app.js
└── README.md
```
