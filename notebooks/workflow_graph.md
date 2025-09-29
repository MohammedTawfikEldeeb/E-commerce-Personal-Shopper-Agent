```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	orchestrator(orchestrator)
	search(search)
	recommender(recommender)
	evaluator(evaluator)
	generator(generator)
	faq(faq)
	__end__([<p>__end__</p>]):::last
	__start__ --> orchestrator;
	evaluator -. &nbsp;generate&nbsp; .-> generator;
	evaluator -.-> search;
	orchestrator -.-> __end__;
	orchestrator -.-> faq;
	orchestrator -.-> recommender;
	orchestrator -.-> search;
	search --> evaluator;
	faq --> __end__;
	generator --> __end__;
	recommender --> __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc

```