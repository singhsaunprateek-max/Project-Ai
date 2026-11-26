import json
import os
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

DB_FILE = "graph_data.json"

# ==========================================
# 1. DEFAULT ENTITIES, RELATIONS & Q&A PACK
# ==========================================

RAW_ENTITIES = [
    ("knowledge-graph", "Knowledge Graph", "Concept", "A structured network of entities connected by typed, meaningful relationships.", ["nodes: entities", "edges: relationships", "supports: graph traversal"]),
    ("entity", "Entity", "Concept", "A uniquely identifiable object, person, place, event, concept, or abstract item represented as a node.", ["identity: unique identifier"]),
    ("node", "Node", "Concept", "The graph representation of an entity or resource.", ["role: vertex"]),
    ("edge", "Edge", "Concept", "A connection between two nodes. A semantic edge has a named predicate that explains the relationship.", ["role: relationship"]),
    ("triple", "RDF Triple", "Concept", "A subject-predicate-object statement. Example: (Alice, studies, Computer Science).", ["structure: subject-predicate-object"]),
    ("semantic-network", "Semantic Network", "Concept", "A graph-like representation of knowledge where nodes represent concepts and links represent semantic relationships.", ["representation: network"]),
    ("ontology", "Ontology", "Concept", "A formal, explicit specification of concepts in a domain, their properties, relationships, and constraints.", ["contains: classes", "contains: properties", "contains: axioms"]),
    ("taxonomy", "Taxonomy", "Concept", "A classification hierarchy that organises concepts into broader and narrower categories.", ["relation: hierarchical classification"]),
    ("class", "Class", "Concept", "A category or type whose members share characteristics, such as Student or Course.", ["role: type"]),
    ("instance", "Instance", "Concept", "A particular member of a class, such as a named student belonging to the Student class.", ["role: individual"]),
    ("property", "Property", "Concept", "A characteristic or attribute associated with an entity, class, or relationship.", ["examples: name, credits, date"]),
    ("is-a", "is-a Relationship", "Relation", "A taxonomic relationship expressing subclassing or class membership. It supports inheritance when modelled accordingly.", ["kind: taxonomic", "supports: inheritance"]),
    ("part-of", "part-of Relationship", "Relation", "A meronymic relationship expressing that one component belongs to a larger whole.", ["kind: meronymic", "direction: component to whole"]),
    ("has-property", "has-property Relationship", "Relation", "A relation attaching an attribute or value to an entity.", ["kind: attribute"]),
    ("inheritance", "Inheritance", "Reasoning", "The mechanism by which a specific class or instance receives applicable properties from a more general class.", ["depends_on: is-a hierarchy"]),
    ("property-propagation", "Property Propagation", "Reasoning", "The process of passing applicable properties through defined graph paths, such as from parent class to subclass.", ["requires: propagation rules"]),
    ("transitivity", "Transitivity", "Reasoning", "A relation is transitive if A related to B and B related to C allows inference that A is related to C.", ["example: is-a subclass chain"]),
    ("inference", "Inference", "Reasoning", "Deriving a new conclusion from existing facts, rules, and relationships.", ["input: facts and rules", "output: derived facts"]),
    ("semantic-reasoning", "Semantic Reasoning", "Reasoning", "Reasoning that uses the meaning and structure of concepts and relations to derive conclusions.", ["uses: ontology", "uses: inference"]),
    ("default-reasoning", "Default Reasoning", "Logic", "Drawing a typical conclusion when no contrary evidence is known; the conclusion can be withdrawn if an exception is discovered.", ["logic: defeasible"]),
    ("exception", "Exception", "Logic", "A more specific fact that blocks or overrides a general default assumption.", ["priority: specific evidence"]),
    ("non-monotonic-logic", "Non-monotonic Reasoning", "Logic", "A reasoning system in which adding new information can invalidate a previous conclusion.", ["supports: retraction"]),
    ("monotonic-logic", "Monotonic Reasoning", "Logic", "A reasoning system in which adding premises does not invalidate conclusions already entailed.", ["property: monotonicity"]),
    ("open-world", "Open World Assumption", "Logic", "The absence of a fact does not imply that the fact is false; it may simply be unknown.", ["assumption: unknown is not false"]),
    ("closed-world", "Closed World Assumption", "Logic", "Within a defined database scope, facts not recorded may be treated as false.", ["assumption: missing means false"]),
    ("RDF", "RDF", "Standard", "Resource Description Framework, a W3C data model for representing information as subject-predicate-object triples.", ["model: triples", "serializations: Turtle, RDF/XML, JSON-LD"]),
    ("RDFS", "RDF Schema", "Standard", "A vocabulary extending RDF with constructs such as classes, subclasses, domains, ranges, and subproperties.", ["supports: rdfs:subClassOf"]),
    ("OWL", "Web Ontology Language", "Standard", "A family of ontology languages used to express rich class descriptions, properties, individuals, and logical axioms.", ["based_on: description logic"]),
    ("SPARQL", "SPARQL", "Query Language", "A query language for retrieving and manipulating RDF graph data.", ["purpose: query RDF"]),
    ("Neo4j", "Neo4j", "Technology", "A native graph database that stores nodes, relationships, and properties and commonly uses the Cypher query language.", ["model: property graph", "query: Cypher"]),
    ("Cypher", "Cypher", "Query Language", "A declarative graph query language used with Neo4j to match and manipulate graph patterns.", ["used_with: Neo4j"]),
    ("property-graph", "Property Graph", "Model", "A graph model where nodes and relationships can both carry labels and key-value properties.", ["elements: nodes, relationships, properties"]),
    ("triple-store", "RDF Triple Store", "Technology", "A database designed to store RDF triples and support graph queries, often using SPARQL.", ["stores: RDF triples"]),
    ("graph-traversal", "Graph Traversal", "Algorithm", "Systematically visiting nodes or edges in a graph, commonly with breadth-first search or depth-first search.", ["algorithms: BFS, DFS"]),
    ("BFS", "Breadth-First Search", "Algorithm", "A graph traversal that explores neighbours level by level, typically using a queue.", ["data_structure: queue"]),
    ("DFS", "Depth-First Search", "Algorithm", "A graph traversal that explores a path deeply before backtracking, typically using recursion or a stack.", ["data_structure: stack"]),
    ("knowledge-base", "Knowledge Base", "Concept", "A structured collection of facts, rules, entities, and relationships used by a reasoning system.", ["contains: facts and rules"]),
    ("query-engine", "Query Engine", "Component", "The component that interprets a user query and retrieves or derives relevant information from a knowledge base.", ["input: query", "output: answer"]),
    ("rule-engine", "Rule Engine", "Component", "A component that applies logical or production rules to facts to derive conclusions.", ["input: facts and rules"]),
    ("explainability", "Explainability", "Quality", "The ability to show why a system returned a particular answer, including supporting facts and inference steps.", ["output: evidence trace"]),
    ("graph-embedding", "Graph Embedding", "Technique", "A technique that maps graph entities or structures into vector representations for machine learning tasks.", ["representation: vectors"]),
    ("knowledge-graph-completion", "Knowledge Graph Completion", "Task", "Predicting missing entities or relationships in a knowledge graph using structural or learned patterns.", ["methods: embedding, rules"]),
    ("entity-resolution", "Entity Resolution", "Task", "Identifying records that refer to the same real-world entity and linking or merging them appropriately.", ["goal: identity matching"]),
    ("data-integration", "Data Integration", "Task", "Combining data from different sources into a coherent representation, often requiring schema and entity alignment.", ["challenge: heterogeneity"]),
    ("semantic-search", "Semantic Search", "Application", "Retrieving information based on meaning and relationships rather than exact keyword matching alone.", ["uses: semantics"]),
    ("RAG", "Retrieval-Augmented Generation", "Technique", "A pattern where relevant external or local knowledge is retrieved and supplied as context to a language model before it generates an answer.", ["stages: retrieve, augment, generate"]),
    ("university-domain", "University Curriculum Domain", "Domain", "A sample domain containing students, faculty, courses, programmes, departments, and academic resources.", ["example_entities: Student, Course, Professor"]),
    ("student", "Student", "Domain Entity", "A person enrolled in an educational programme.", ["can_access_library: true", "has_student_id: true"]),
    ("CS Student", "CS Student", "Domain Entity", "A student specialising in Computer Science and Engineering.", ["department: CSE", "uses_computing_lab: true"]),
    ("professor", "Professor", "Domain Entity", "An academic faculty member who may teach, research, and supervise students.", ["has_office: true", "academic_role: faculty"]),
    ("visiting-professor", "Visiting Professor", "Domain Entity", "A professor temporarily associated with an institution; may have exceptions to regular duties.", ["appointment: temporary", "teaching_exempt: possible"]),
    ("course", "Course", "Domain Entity", "A structured unit of study with a syllabus, credits, learning outcomes, and assessments.", ["has_credits: true"]),
    ("curriculum", "Curriculum", "Domain Entity", "A planned set of courses and learning outcomes for an academic programme.", ["contains_courses: true"]),
    ("machine-learning", "Machine Learning", "Domain Entity", "A field of AI in which algorithms learn patterns from data to make predictions or decisions.", ["field: AI", "credits: 4"]),
    ("database-systems", "Database Systems", "Domain Entity", "A subject covering data modelling, database design, SQL, transactions, and data management.", ["field: Computer Science"]),
    ("default-example", "Bird Default Example", "Logic Example", "A classic defeasible rule: birds normally fly, but penguins are birds that are typically unable to fly.", ["default: birds fly", "exception: penguins"]),
    ("university-graph-example", "University Graph Example", "Example", "CS Student is-a Student; Student is-a Person. The graph can infer CS Student is-a Person and propagate parent properties.", ["relation: is-a"]),
    ("person", "Person", "Domain Entity", "A human being; the general parent class for students and faculty.", ["has_identity: true"]),
    ("btech-cse", "BTech CSE", "Domain Entity", "An undergraduate Computer Science and Engineering degree programme.", ["duration: 4 years"]),
    ("university-library", "University Library", "Domain Entity", "A university learning facility with physical and digital resources.", ["open_to_students: true"]),
]

DEFAULT_ENTITIES = [
    {"id": eid, "name": name, "category": cat, "description": desc, "properties": props}
    for eid, name, cat, desc, props in RAW_ENTITIES
]

RELATIONS_RAW = [
    ("CS Student", "is-a", "Student"), ("Student", "is-a", "Person"), ("Professor", "is-a", "Person"),
    ("Visiting Professor", "is-a", "Professor"), ("Machine Learning", "is-a", "Course"),
    ("Database Systems", "is-a", "Course"), ("Machine Learning", "part-of", "Curriculum"),
    ("Database Systems", "part-of", "Curriculum"), ("Curriculum", "part-of", "BTech CSE"),
    ("Student", "has-property", "University Library"), ("Professor", "teaches", "Machine Learning"),
    ("CS Student", "enrolled-in", "BTech CSE"), ("RDFS", "extends", "RDF"), ("OWL", "builds-on", "RDF"),
    ("SPARQL", "queries", "RDF"), ("Cypher", "queries", "Neo4j"), ("RAG", "uses", "Knowledge Base"),
    ("Rule Engine", "supports", "Inference"), ("Graph Traversal", "supports", "Inference")
]

NAME_TO_ID = {e["name"]: e["id"] for e in DEFAULT_ENTITIES}
DEFAULT_RELATIONS = [
    [NAME_TO_ID.get(s, s), r, NAME_TO_ID.get(t, t)] for s, r, t in RELATIONS_RAW
]

QA_PACK = [
    {
        "keys": ["knowledge graph", "what is a kg", "define kg"],
        "title": "What is a knowledge graph?",
        "body": "A knowledge graph is a structured representation of information in which entities are represented as nodes and relationships are represented as edges. Relationships have meaning, so systems can traverse the graph and infer connections instead of relying only on isolated stored facts.",
        "points": [
            "Nodes represent entities or concepts.",
            "Edges represent typed relationships such as is-a, part-of, authored-by, or located-in.",
            "Properties describe characteristics of nodes or relationships.",
            "Inference rules can derive additional facts from graph structure."
        ],
        "trace": "Identify entities → connect them with typed predicates → apply graph traversal and inference."
    },
    {
        "keys": ["semantic network", "semantic net"],
        "title": "What is a semantic network?",
        "body": "A semantic network is a graph-based knowledge representation in which concepts are nodes and semantic relations are links. It is a foundational idea behind many knowledge representation and knowledge graph systems.",
        "points": [
            "Represents concepts and their relations visually.",
            "Can express classification, part-whole, and association links.",
            "Supports associative retrieval and inheritance when rules are defined."
        ],
        "trace": "Concept nodes + meaningful links form a semantic network."
    },
    {
        "keys": ["ontology", "what is an ontology"],
        "title": "What is an ontology?",
        "body": "An ontology is a formal, explicit specification of the concepts in a domain and the relationships, properties, constraints, and axioms that apply to them. It defines the vocabulary and meaning used by a knowledge graph.",
        "points": [
            "Classes define categories, such as Student and Course.",
            "Individuals are specific members of classes.",
            "Properties describe attributes and relations.",
            "Axioms define constraints and logical statements."
        ],
        "trace": "Define domain vocabulary → define classes and properties → add axioms and individuals."
    },
    {
        "keys": ["taxonomy", "ontology vs taxonomy", "difference between ontology and taxonomy"],
        "title": "Ontology vs taxonomy",
        "body": "A taxonomy is primarily a classification hierarchy, often a tree of broader and narrower categories. An ontology is richer: it can include classes, individuals, attributes, many relation types, constraints, and logical axioms.",
        "points": [
            "Taxonomy: focuses on hierarchical categorisation.",
            "Ontology: models richer semantics and constraints.",
            "Example taxonomy: Animal → Mammal → Cat.",
            "Example ontology: Cat is-a Mammal; Cat has-property numberOfLegs=4."
        ],
        "trace": "Compare scope: classification hierarchy versus a richer formal domain model."
    },
    {
        "keys": ["is-a", "isa relation", "is a relationship"],
        "title": "What does is-a mean?",
        "body": "The is-a relation represents class membership or subclassing. For example, CS Student is-a Student and Student is-a Person. In a class hierarchy, this allows transitive classification and property inheritance.",
        "points": [
            "It is taxonomic / hierarchical.",
            "It supports inheritance of applicable parent properties.",
            "If A is-a B and B is-a C, infer A is-a C when the relation is modelled transitively."
        ],
        "trace": "A → is-a → B → is-a → C; derive A → is-a → C."
    },
    {
        "keys": ["part-of", "part of relationship", "meronym"],
        "title": "What does part-of mean?",
        "body": "Part-of is a meronymic relation: it connects a component to the larger whole that contains or includes it. For example, a course can be part of a curriculum.",
        "points": [
            "is-a expresses category membership or subclassing.",
            "part-of expresses component-to-whole structure.",
            "Transitivity is a modelling choice and should be validated for the domain."
        ],
        "trace": "Course → part-of → Curriculum; Curriculum → part-of → Programme."
    },
    {
        "keys": ["inheritance", "property inheritance"],
        "title": "How does inheritance work in a knowledge graph?",
        "body": "Inheritance allows a specific class to receive applicable properties from a more general parent class. If CS Student is-a Student and Student is-a Person, then CS Student may inherit Student properties and Person properties.",
        "points": [
            "Direct properties belong to the entity itself.",
            "Inherited properties originate from ancestors.",
            "More specific values may override general defaults."
        ],
        "trace": "CS Student → Student → Person; collect properties at each ancestor."
    },
    {
        "keys": ["default reasoning", "defeasible reasoning"],
        "title": "What is default reasoning?",
        "body": "Default reasoning draws a typical conclusion when there is no known contrary evidence. It is defeasible: the conclusion can be withdrawn when a more specific exception is discovered.",
        "points": [
            "A default is a typical rule, not an absolute truth.",
            "An exception provides more specific evidence.",
            "The exception blocks or overrides the default conclusion."
        ],
        "trace": "General default → check specific exceptions → accept or defeat conclusion."
    },
    {
        "keys": ["rdf", "resource description framework"],
        "title": "What is RDF?",
        "body": "RDF (Resource Description Framework) is a W3C standard data model for describing resources using subject-predicate-object triples.",
        "points": [
            "Subject: the resource being described.",
            "Predicate: the named property or relation.",
            "Object: a resource or literal value.",
            "RDF graphs are sets of triples and can be queried with SPARQL."
        ],
        "trace": "Example: (Alice, studies, ComputerScience)."
    },
    {
        "keys": ["owl", "web ontology language"],
        "title": "What is OWL?",
        "body": "OWL (Web Ontology Language) is a W3C family of ontology languages for expressing rich knowledge about classes, properties, individuals, and logical constraints.",
        "points": [
            "Can define equivalent and disjoint classes.",
            "Can express property characteristics and restrictions.",
            "Supports formal ontology reasoning."
        ],
        "trace": "Ontology axioms are processed by an OWL reasoner to derive logical entailments."
    },
    {
        "keys": ["sparql"],
        "title": "What is SPARQL?",
        "body": "SPARQL is the standard query language for RDF data. It allows users to match graph patterns, retrieve bindings, and perform updates.",
        "points": [
            "SELECT retrieves variable bindings.",
            "ASK checks whether a pattern exists.",
            "CONSTRUCT builds an RDF graph from matches."
        ],
        "trace": "Write a graph pattern → match triples → return variable bindings or a constructed graph."
    },
    {
        "keys": ["neo4j"],
        "title": "What is Neo4j?",
        "body": "Neo4j is a graph database using a property graph model. It stores nodes, relationships, labels, and key-value properties.",
        "points": [
            "Nodes represent entities.",
            "Relationships are directed and typed.",
            "Cypher is used to query and update the graph."
        ],
        "trace": "Model nodes and edges → persist in Neo4j → query patterns with Cypher."
    },
    {
        "keys": ["rag", "retrieval augmented"],
        "title": "What is Retrieval-Augmented Generation (RAG)?",
        "body": "RAG is a pattern in which a system retrieves relevant information from a knowledge source and supplies it to a language model as context before generating an answer.",
        "points": [
            "Retrieve relevant passages or graph neighbourhoods.",
            "Augment the model prompt with evidence.",
            "Generate an answer grounded in retrieved context."
        ],
        "trace": "Question → retrieve graph context → augment prompt → generate grounded response."
    },
    {
        "keys": ["architecture", "system architecture"],
        "title": "Project system architecture",
        "body": "The project is organised into a frontend UI, Python Flask REST API, JSON graph store, semantic inference engine, and explainable query responder.",
        "points": [
            "Frontend UI: interactive graph explorer, builder, and chat.",
            "Flask Backend: REST endpoints for entities, relations, reasoning, and Q&A.",
            "Graph Store: persistent JSON storage for nodes and edges.",
            "Reasoner: computes transitivity, property inheritance, and part-of closure."
        ],
        "trace": "User query → Flask API → graph lookup & inference → explainable JSON response."
    },
    {
        "keys": ["viva", "interview questions", "oral exam"],
        "title": "Viva preparation: key questions",
        "body": "Important viva areas include graph structure, ontology versus taxonomy, is-a versus part-of, inheritance, property propagation, transitivity, default reasoning, exceptions, RDF triples, OWL, and SPARQL.",
        "points": [
            "Why use a knowledge graph instead of a relational table?",
            "How is is-a different from part-of?",
            "What is property propagation?",
            "Why is default reasoning non-monotonic?",
            "How does the query engine explain its answers?"
        ],
        "trace": "Prepare definitions → give examples → explain implementation → discuss limitations."
    }
]


# ==========================================
# 2. DATABASE PERSISTENCE HELPERS
# ==========================================

def load_db():
    if not os.path.exists(DB_FILE):
        data = {"entities": DEFAULT_ENTITIES, "relations": DEFAULT_RELATIONS}
        save_db(data)
        return data
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_entity(db, eid):
    return next((e for e in db["entities"] if e["id"] == eid), None)


# ==========================================
# 3. SEMANTIC INFERENCE ENGINE
# ==========================================

def get_ancestors(db, eid, seen=None):
    if seen is None:
        seen = set()
    ancestors = []
    for s, r, t in db["relations"]:
        if s == eid and r == "is-a" and t not in seen:
            seen.add(t)
            ancestors.append(t)
            ancestors.extend(get_ancestors(db, t, seen))
    return ancestors


def derive_facts(db):
    derived = []
    for entity in db["entities"]:
        ancestors = get_ancestors(db, entity["id"])

        # Rule 1: Transitive is-a
        for anc_id in ancestors:
            anc = get_entity(db, anc_id)
            if anc:
                chain = " → ".join([entity["name"]] + [get_entity(db, a)["name"] for a in ancestors if get_entity(db, a)])
                derived.append({
                    "text": f"{entity['name']} is-a {anc['name']}",
                    "why": f"Transitive is-a path: {chain}",
                    "rule": "TRANSITIVITY"
                })

        # Rule 2: Property Inheritance
        inherited_props = {}
        for anc_id in ancestors:
            anc = get_entity(db, anc_id)
            if anc:
                for prop in anc.get("properties", []):
                    inherited_props[prop] = anc["name"]

        for prop, source_name in inherited_props.items():
            derived.append({
                "text": f"{entity['name']} inherits {prop}",
                "why": f"Property propagated from {source_name}.",
                "rule": "INHERITANCE"
            })

    # Rule 3: Transitive part-of
    for s, r, t in db["relations"]:
        if r == "part-of":
            for s2, r2, t2 in db["relations"]:
                if s2 == t and r2 == "part-of":
                    s_ent = get_entity(db, s)
                    t_ent = get_entity(db, t)
                    t2_ent = get_entity(db, t2)
                    if s_ent and t_ent and t2_ent:
                        derived.append({
                            "text": f"{s_ent['name']} is part of {t2_ent['name']}",
                            "why": f"Part-of chain: {s_ent['name']} → {t_ent['name']} → {t2_ent['name']}",
                            "rule": "PART-OF"
                        })
    return derived


# ==========================================
# 4. DOMAIN AI QUERY ENGINE
# ==========================================

def score_qa(query):
    words = [w for w in re.sub(r"[^a-z0-9\s-]", " ", query.lower()).split() if len(w) > 2]
    best_item = None
    best_score = 0
    q_lower = query.lower()

    for item in QA_PACK:
        score = 0
        for k in item["keys"]:
            kl = k.lower()
            if kl in q_lower:
                score = max(score, len(kl.split()) * 3 + len(kl) / 20)
        for w in item["title"].lower().split():
            if w in words:
                score += 1
        if score > best_score:
            best_score = score
            best_item = item

    return best_item if best_score >= 2 else None


def answer_question(db, q):
    l = q.lower().strip()
    derived = derive_facts(db)
    best = score_qa(q)
    exact = next((e for e in db["entities"] if e["name"].lower() in l), None)

    if re.match(r"^(hi|hello|hey)\b", l):
        return {
            "title": "Hello!",
            "body": "I'm GraphMind (Python Backend). Ask me about knowledge graphs, ontologies, inference, RDF/OWL, SPARQL, or your graph entities.",
            "points": [],
            "trace": "Greeting recognised; no graph inference needed."
        }

    if re.search(r"how many|count|number of", l) and re.search(r"entity|entities|node|nodes|relation|edge", l):
        return {
            "title": "Current graph statistics",
            "body": f"The backend graph currently contains {len(db['entities'])} entities and {len(db['relations'])} explicit relationships, with {len(derived)} derived conclusions.",
            "points": [
                f"Entities: {len(db['entities'])}",
                f"Relationships: {len(db['relations'])}",
                f"Derived conclusions: {len(derived)}"
            ],
            "trace": "Counted current backend JSON graph records."
        }

    if re.search(r"list.*(entity|entities|concept|node)|show.*(entity|entities|concept|node)", l):
        return {
            "title": "Entities in the current graph",
            "body": "Here are the concepts currently loaded in the Python knowledge base.",
            "points": [f"{e['name']} — {e['category']}" for e in db["entities"][:80]],
            "trace": "Enumerated the graph entity registry."
        }

    if exact and re.search(r"inherit|propert|attribute", l):
        anc_ids = get_ancestors(db, exact["id"])
        inherited_points = []
        for aid in anc_ids:
            anc = get_entity(db, aid)
            if anc:
                for p in anc["properties"]:
                    inherited_points.append(f"Inherited from {anc['name']}: {p}")
        chain = " → ".join([exact["name"]] + [get_entity(db, a)["name"] for a in anc_ids if get_entity(db, a)])
        return {
            "title": f"Properties of {exact['name']}",
            "body": f"{exact['name']} has {len(exact['properties'])} direct properties and inherits {len(inherited_points)} properties through its is-a ancestors.",
            "points": [f"Direct: {p}" for p in exact["properties"]] + inherited_points,
            "trace": f"{chain}; collect ancestor properties."
        }

    if exact and re.search(r"what is|who is|define|describe|explain", l):
        anc_ids = get_ancestors(db, exact["id"])
        points = [f"Category: {exact['category']}"] + exact["properties"]
        for aid in anc_ids:
            anc = get_entity(db, aid)
            if anc:
                points.append(f"is-a {anc['name']}")
        chain = " → ".join([exact["name"]] + [get_entity(db, a)["name"] for a in anc_ids if get_entity(db, a)])
        return {
            "title": f"About {exact['name']}",
            "body": exact["description"],
            "points": points,
            "trace": chain if anc_ids else "Retrieved the entity description and properties."
        }

    if re.search(r"which.*(part|course)|part of|part-of", l):
        pts = [
            f"{get_entity(db, s)['name']} part-of {get_entity(db, t)['name']}"
            for s, r, t in db["relations"]
            if r == "part-of" and get_entity(db, s) and get_entity(db, t)
        ]
        return {
            "title": "Part-of relationships",
            "body": "These are the component-to-whole relations currently represented in the graph.",
            "points": pts,
            "trace": "Traversed explicit part-of edges."
        }

    if best:
        return {
            "title": best["title"],
            "body": best["body"],
            "points": best.get("points", []),
            "trace": best.get("trace", "Matched a curated domain knowledge entry.")
        }

    if exact:
        return {
            "title": f"Knowledge about {exact['name']}",
            "body": exact["description"],
            "points": exact["properties"],
            "trace": "Matched an entity in the knowledge graph."
        }

    return {
        "title": "I couldn't find a reliable answer in this knowledge pack",
        "body": "This Python backend uses a curated domain knowledge pack plus your editable graph. Try rephrasing with key terms such as ontology, inheritance, RDF, OWL, SPARQL, Neo4j, or default reasoning.",
        "points": [
            "Try: Explain ontology vs taxonomy.",
            "Try: How does is-a inheritance work?",
            "Try: What are RDF triples?"
        ],
        "trace": "No sufficiently relevant knowledge entry or graph entity was matched."
    }


# ==========================================
# 5. FLASK REST API ENDPOINTS
# ==========================================

@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/graph", methods=["GET"])
def get_graph():
    db = load_db()
    derived = derive_facts(db)
    return jsonify({
        "entities": db["entities"],
        "relations": db["relations"],
        "derivedFacts": derived,
        "qaCount": len(QA_PACK)
    })


@app.route("/api/entities", methods=["POST"])
def add_entity():
    payload = request.json or {}
    name = payload.get("name", "").strip()
    if not name:
        return jsonify({"error": "Entity name is required."}), 400

    db = load_db()
    if any(e["name"].lower() == name.lower() for e in db["entities"]):
        return jsonify({"error": "Entity already exists."}), 409

    eid = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    new_entity = {
        "id": eid,
        "name": name,
        "category": payload.get("category", "Class"),
        "description": payload.get("description") or "User-created concept.",
        "properties": [p.strip() for p in payload.get("properties", []) if p.strip()]
    }
    db["entities"].append(new_entity)
    save_db(db)
    return jsonify({"message": "Entity created.", "entity": new_entity}), 201


@app.route("/api/entities/<eid>", methods=["DELETE"])
def delete_entity(eid):
    db = load_db()
    db["entities"] = [e for e in db["entities"] if e["id"] != eid]
    db["relations"] = [r for r in db["relations"] if r[0] != eid and r[2] != eid]
    save_db(db)
    return jsonify({"message": "Entity and connected edges removed."})


@app.route("/api/relations", methods=["POST"])
def add_relation():
    payload = request.json or {}
    s = payload.get("source")
    r = payload.get("predicate")
    t = payload.get("target")

    if not s or not t or s == t:
        return jsonify({"error": "Choose two different entities."}), 400

    db = load_db()
    if any(rel[0] == s and rel[1] == r and rel[2] == t for rel in db["relations"]):
        return jsonify({"error": "Relationship already exists."}), 409

    db["relations"].append([s, r, t])
    save_db(db)
    return jsonify({"message": "Semantic relation added.", "relation": [s, r, t]}), 201


@app.route("/api/ask", methods=["POST"])
def ask_endpoint():
    payload = request.json or {}
    question = payload.get("question", "").strip()
    if not question:
        return jsonify({"error": "Question cannot be empty."}), 400

    db = load_db()
    response = answer_question(db, question)
    return jsonify(response)


@app.route("/api/reset", methods=["POST"])
def reset_graph():
    data = {"entities": DEFAULT_ENTITIES, "relations": DEFAULT_RELATIONS}
    save_db(data)
    return jsonify({"message": "Graph reset to default dataset."})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
