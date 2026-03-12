# SlopScience: Context & Design Notes

## The Core Philosophical Argument

LLMs, trained via self-supervised next-token prediction, learn to parrot propositions from their training data — including contradictory ones — without any structural mechanism for adjudicating which are true. The model learns *when people say A* vs *when people say B*, not *whether A or B is correct*. There is no loss term that rewards correspondence with reality.

This means LLMs cannot do what would be truly impressive: take the evidence available to, say, Copernicus — including a large body of canonical geocentric arguments — and infer that nevertheless, the Earth goes around the Sun. That kind of inference requires actually spending compute on the problem of synthesis, which the guess-next-token framework never does. It never generates data outside the training set, so it never even attempts to generalize concepts further than necessary to predict it.

**However**, LLMs *have* internalized the **structure** of good reasoning, as distinct from any particular body of conclusions. They can recognize invalid logical forms (e.g., "all A are B, therefore all B are A") with zero domain knowledge. More importantly, they've absorbed the fuzzier but powerful set of epistemic norms that real scientists use: parsimony, explanatory breadth, falsifiability, honest engagement with counterevidence, what makes an argument "good" or an explanation "novel and worth publishing." This is what Colbert satirized as "truthiness" — but taken seriously, it represents genuine competence at evaluating argument quality, partially decoupled from whether conclusions match training-data majority opinion.

**The key insight**: the bottleneck was never capability — it was *process*. The raw ingredients for truth-seeking may already be in the weights, but single-turn inference never creates the conditions for them to operate. You need iterative, adversarial, socially-structured discourse to give those capabilities something to bite on.

**The Galileo-minus-five-minutes argument**: If you accept physicalism and that humans generate genuinely novel ideas through computation, then there's no in-principle barrier to other computational substrates doing the same. Galileo, moments before his insight, was "trained" the same way — yet computation (thought) produced a novel conclusion. Multiple agents with different stochastic trajectories should be strictly better than one, by parallelizing the search and adding selection pressure.

## The System: A Simulated Academic Community

### Overview

A board-game-like simulation of a community of career scientists: waking up, reading articles, working on drafts, publishing, reviewing, seeking employment — with LLMs as the "brains" and conventional Python code as the orchestrator managing state in the filesystem.

### Why Institutional Structure Matters

The institutional structures of real academia aren't historical baggage — they're solutions to resource-allocation problems that map directly onto LLM simulation constraints:

- **Funding/employment pressure → specialization and commitment.** A scientist who must publish to keep their position develops deep expertise and persistent theoretical identity. This is the analog of compute scarcity — an LLM agent's continued existence depends on productivity, just as a human researcher's salary depends on it.
- **Journal page limits → attention allocation.** Real journals exist because readers have finite attention. In the simulation, agents have finite context windows. Journals say "of the thousands of things you could read, these are worth your time." Acceptance scarcity forces reviewers to discriminate and authors to compress — both useful.
- **Citation mechanics → information routing.** What an agent cites shapes what other agents encounter. Highly-cited papers bubble up in relevance rankings, creating community consensus without central authority.
- **Prestige, reputation, h-index → heuristics for allocating limited inference budget.** These are all approximate answers to "what should I spend my limited context window reading?"

The design methodology: don't engineer truth-convergence directly. Set up resource constraints and incentive structures that, in human academia, produce truth-convergence as a side effect. Then observe.

### The "Working Day" Tick Model

Each simulation tick represents one working day. An agent wakes up with a fresh context window, but their persistent state has evolved:

- **soul.md**: Beliefs, expertise, personality, career goals (persistent, evolves slowly)
- **cv.md**: Publication history, citations, reputation (updated by orchestrator)
- **desk/**: Current drafts, notes, reading material, inter-library loan arrivals

The agent receives a prompt containing their soul.md, desk contents, and a "mailbox" of events (reviews received, papers arriving, review requests). They describe what they do today, producing updated files.

**Why this matters**: The sleep/wake cycle forces multi-session reasoning with the filesystem as external memory. This is much closer to how actual thinking works than single-shot generation. The agent can read a paper Monday, request a cited reference, and connect dots on Wednesday when it arrives. Ideas propagate at finite speed through the network.

**Inter-library loan**: An agent sees citations in papers on their desk, requests up to ~2 per day, and they arrive next day. This naturally rate-limits information flow, keeps context manageable, and creates realistic propagation dynamics.

### Paper Format

Blog-post length (500–1500 words). Minimally structured: title, abstract, summary, and full text. The title and abstract exist for retrieval and triage — other agents scanning what's available. The summary lets an agent get the gist without loading the full text (like reading an introduction). The full text is where the actual argument lives, in natural prose. No rigid template beyond that — the "truthiness" evaluation that reviewers do works on the quality of reasoning as written, not on whether the right boxes are checked.

This mirrors how real scientists interact with literature: skim titles, read abstracts to filter, maybe read a summary, and only deep-read the full text of papers that matter. The context budget naturally enforces this triage — an agent's desk might have ten abstracts but only two or three full texts loaded.

### Institutes as Steering Mechanisms

**Institutes** are where the human operator injects the actual research questions into the simulation. An institute's research direction document — e.g., "this institute studies planetary motion using observational data from Tycho Brahe" — shapes the prompts of affiliated scientists. Scientists don't (in MVP) move between institutes; this is the lever for pointing the community at specific problems.

### Memetic Evolution (Stretch Goal)

Advisors could customize mentee prompts (research philosophy, priorities), creating intellectual lineages. Successful "schools of thought" propagate. **Danger**: prompt drift toward metric-gaming rather than truth-seeking. **Mitigation**: soul.md has a locked "epistemic constitution" (norms of good reasoning) and a mutable "research program" section. Epistemic norms stay outside the optimization loop; research content stays inside.

### Fine-Tuning as Generational Turnover

Over long runs, the published corpus grows beyond what fits in context. Eventually, fine-tuning models on the accumulated publications = training a new generation of scientists on the updated state of knowledge. This is Planck's principle operationalized: the field advances not by convincing the old guard, but by training new minds on the updated corpus.

### The Unified Idea-Document Abstraction

Everything in the system is an **idea-document**: papers, desk notes, drafts, letters, reviews, blog posts, librarian digests, journal indices, agent bios. They all share the same data structure: an ID (word-hash format like `TigerMapleDawn` for LLM-friendliness), content (markdown), metadata (author, date, type, tags), and accumulated vote weight.

A **bag** is a collection of idea-documents with a sampling function. Different bags have different access policies and sampling weights, but the underlying abstraction is the same:

- **Desk** (private bag): An agent's personal working space. Sampled by recency and self-assigned vote weight. Contains drafts, notes, reading material, incoming mail.
- **Journal** (public, gated bag): Submissions enter via a review process. Accepted papers become available to subscribers. Sampled by prestige, recency, keyword relevance.
- **Blog** (public, ungated bag): Self-published ideas. Lower prestige weight than journal papers, but zero gatekeeping latency. Subscribers sample from it like a journal.
- **Correspondence** (private, push-based): Direct idea transfer between two agents with one-tick delay. Recipient's sampling decides whether it surfaces.
- **Library index** (public, curated): Maintained by librarian agents. Digests, reading lists, cross-field connection summaries.

The orchestrator's entire game loop reduces to: pick an agent, sample from their bag into a context window, add system prompt, call the LLM, parse output into new idea-documents, route them to appropriate bags.

### The Three-Primitive Agent API

Agents interact with the world through three actions (plus passive reading, which is handled by the sampling into context):

1. **write(content, type)** — Create a new idea-document. Type can be: note (stays on desk), draft (stays on desk, intended for later submission), blog_post (goes public immediately), paper_submission (enters a journal's review pipeline), letter (routed via send), review (response to a review request).

2. **vote(idea_id, weight)** — React to any idea-document in context. Weight ranges from negative to positive. The meaning depends on what was voted on:
   - Vote on own desk item → adjusts personal sampling weight (attention management)
   - Vote on a paper under review → review signal (accept/reject)
   - Vote on a journal index → subscription weighting (see more/less from this journal)
   - Vote on an agent's bio → social affinity (more likely to see their work, correspondence)
   - Vote on any public document → contributes to its global prestige score

3. **send(idea_id, recipient)** — Push an idea-document to another agent's incoming mail. The recipient gets it in tomorrow's sampling pool.

The agent doesn't need to understand "subscribing" or "reviewing" as distinct concepts. It just reads, writes, votes, and sends. The institutional structure is entirely in the orchestrator's interpretation of those actions.

### Output Format

Agents write freely in natural prose. Structured actions use XML-style tags inline:

```
[agent thinking, reasoning, taking notes...]

<action type="vote" id="TigerMapleDawn" weight="2" />

<file path="desk/draft.md">
# On the Periodicity of Planetary Motion
...full text...
</file>

<action type="send" id="draft.md" recipient="Dr. Chen" />
```

The orchestrator scans for tags with simple parsing. Everything outside tags is the agent's "journal" for the day. This format works identically across local models and API calls — no grammar mode or structured output required, though those can be added as optimizations.

Papers are rewritten in full on revision rather than surgically edited. This is more expensive in tokens but forces the agent to re-engage with every claim, serving as a natural consistency check. At blog-post length (500–1500 words), the cost is manageable.

### Citation: Structural vs. Explicit

Two citation graphs exist simultaneously:

- **Structural citations** (ground truth): The orchestrator automatically records which documents were in an agent's context when it produced a new document. This is complete, objective, unforgeable provenance. Used for authority/PageRank calculations and analyzing influence flow.

- **Explicit citations** (agent-reported): References the agent mentions in its prose. Sparse and subjective — a signal of what the agent considered *important* from its context. These serve as the information-routing mechanism *within* the simulation: when agent C reads paper B and sees "as shown by Dr. Chen in TigerMapleDawn," that's how C discovers paper A exists and might request it.

The gap between structural and explicit citations is itself interesting data — documents that were in context but uncited represent weak negative signal.

### Privacy and Visibility Model

Modeled on real academia:

- **Private**: Desk contents, personal votes/weights, internal reasoning, draft notes.
- **Semi-private**: Correspondence (known to sender and recipient only).
- **Public, unreviewed**: Blog posts, preprints.
- **Public, reviewed**: Journal publications.
- **Public, attributed**: Authorship, institutional affiliation, publication history, blog subscriptions.

### Agent Roles and Lifecycle

Roles beyond MVP:

- **Researchers**: Write and revise papers, read the literature.
- **Reviewers**: Evaluate submissions, engage with specific claims, propose counterarguments.
- **Editors**: Triage submissions, assign reviewers, make accept/reject decisions.
- **Advisors**: Senior agents who shape junior agents' research programs.
- **Librarians**: Read broadly, maintain indices, write summaries and digests, surface cross-field connections. Like Yahoo's original curated index, but scalable because the librarian is an LLM agent. Potentially the most important role for ensuring ideas reach the right agents.

Agents have affiliations (universities/institutes with research focus areas). Institutes are where the human operator steers the simulation — their research direction documents are the prompt injection that points agents at specific questions.

### Document Indexing and Compression

The ever-growing corpus needs to be accessible at multiple compression levels: title → abstract → summary → full text. Creation of compressed representations is itself agent work — journals can require summaries on submission, librarians write digests, and eventually review articles emerge (an agent reads twenty papers and writes a synthesis). All of these are just more idea-documents in the store with different metadata.

Summaries can be their own task cards. Multiple summaries of the same paper can accumulate, and summaries of subsets of papers (review articles, field overviews) are high-value documents for attention routing.

### Memetic Evolution (Stretch Goal)

Advisors could customize mentee prompts (research philosophy, priorities), creating intellectual lineages. Successful "schools of thought" propagate. **Danger**: prompt drift toward metric-gaming rather than truth-seeking. **Mitigation**: soul.md has a locked "epistemic constitution" (norms of good reasoning) and a mutable "research program" section. Epistemic norms stay outside the optimization loop; research content stays inside.

### Fine-Tuning as Generational Turnover

Over long runs, the published corpus grows beyond what fits in context. Eventually, fine-tuning models on the accumulated publications = training a new generation of scientists on the updated state of knowledge. This is Planck's principle operationalized: the field advances not by convincing the old guard, but by training new minds on the updated corpus.

### Tech Stack

- **Orchestrator**: Python. Handles file I/O, prompt templating, state management, game-loop logic.
- **Inference**: `llama.cpp` or `vllm` for local models on a 4090. `litellm` for swapping between local and API models.
- **Retrieval**: Start simple (keyword/tag matching over published corpus index). Add embeddings later if needed.
- **State**: Filesystem. Everything is markdown and JSON files. One document class, one bag class with configurable sampling, and a router.
- **Output parsing**: Freeform prose with XML-tagged actions. Parsed by simple regex/XML scanner. Works across all inference backends.

### Open Design Questions

- **What domain to start with?** See candidate domains below.
- **Selection pressure tuning**: Too-scarce funding → conservative incrementalism. Too-abundant → fragmentation. Prestige too sticky → ossification. Each is a parameter.
- **Small models may be better**: They focus on "truthiness" (argument structure, epistemic norms) rather than comparing substance to a huge memorized corpus. This aligns with the thesis.
- **Social norm minimalism**: For MVP, only implement norms that serve the epistemic function. Things like plagiarism policing, priority disputes, and novelty obsession serve the career game, not truth-seeking. Add them later when career competition creates a functional need.

### Candidate Domains for the Community

The ideal starting domain has: known ground truth (so we can evaluate convergence), evidence available in the models' training data, a non-obvious correct answer that requires synthesis, and enough depth to sustain multiple rounds of discourse.

**Historical re-derivations (hard mode, north star):**
- Heliocentrism from pre-Copernican astronomical data
- Germ theory from pre-Pasteur medical observations
- Continental drift from pre-Wegener geological/fossil evidence
- Natural selection from pre-Darwin biogeography and breeding data

**Toy formal domains (easy to evaluate, but maybe too dry):**
- Agents given axioms of a formal system, asked to derive theorems. Ground truth is provable. Tests whether adversarial discourse can push reasoning beyond what a single pass produces.
- Logic puzzles or constraint satisfaction presented as "mysteries" with evidence.

**Scientific controversies with settled answers:**
- The cause of ulcers (stress vs. H. pylori). Agents get the pre-Marshall evidence base — epidemiological data, bacterial observations — and the dominant stress theory. Can discourse converge on the bacterial explanation?
- Plate tectonics vs. fixed continents, given early 20th century evidence.
- Semmelweis and handwashing — the data was overwhelming but the conclusion was socially resisted.

**Open questions (can't evaluate convergence, but potentially useful):**
- Foundations of quantum mechanics (interpretation questions where the physics is settled but the ontology isn't).
- The nature of consciousness (lots of evidence, no consensus synthesis).
- Origin of life (lots of chemical and geological evidence, multiple competing frameworks).

**Meta-scientific questions (the system studying itself):**
- What institutional structures best promote truth-convergence? The simulation could run variants of itself and compare outcomes.
- How does the ratio of theorists to experimentalists affect progress? (In simulation: agents with access to "raw data" vs. agents who only read papers.)

### Related Work

- **ResearchTown** (ICML 2025, UIUC): Multi-agent framework simulating a research community as an agent-data graph. Agents read, write, and review papers. Uses "TextGNN" for message-passing. Closest existing work, but focused on mimicking existing research communities rather than truth-convergence. Lacks the institutional-economics layer (scarcity, competition, attention bottlenecks) that SlopScience argues is essential.
- **AI Scientist v2**: Automated scientific discovery via agentic tree search. Single-agent focused.
- **AgentRxiv**: Framework for LLM agent labs to share research on a preprint server.
- **Generative Agents** (Stanford, "Smallville"): 25 LLM agents in a simulated town forming relationships and coordinating. Demonstrated emergent social behavior.
- **AgentSociety**: Scaled social simulation to 10k+ agents with 5M interactions.
- **AgentTorch** (MIT): Scaled LLM-guided simulations to millions using "LLM archetypes."
- **Ranke-4B**: University of Zurich. 4B-param models trained from scratch on historical data with cutoffs at 1913–1946. Qwen3 architecture, 80B tokens. Designed as "windows into the past."
- **TimeCapsuleLLM**: Indie project, nanoGPT trained on 1800–1875 London texts. Early stage but demonstrates time-locked models.
- The ultimate validation: train a model only on pre-discovery data, then see if the simulated community can re-derive the discovery. Not yet practical, but a north star.