+++
title = "Reading Observability by Intent"
date = 2026-05-05
updated = "2026-06-11"
toc = true

description = "Tool taxonomies organise observability by metrics, traces, logs, and profiles. Practitioners organise it by intent: what am I trying to understand, debug, or prove? This article reframes the observability stack around six common intents — Golden Signals, latency propagation, high-cardinality debugging, low-overhead profiling, black-box, and cost-efficient at scale — with the workflows, the right tool combinations, the anti-patterns to avoid, and a dedicated treatment of how unified APM platforms (Datadog, New Relic, Dynatrace) fit in the intent-routing framing."

[taxonomies]
tags = ["observability", "performance engineering", "OpenTelemetry", "APM", "distributed tracing"]

[extra]
giscus = true
copy_button = true
footnote_backlinks = true
+++

> *Checkout p99 doubled at 12:14. The metrics dashboard says so. The trace explorer can show you any single request, but the slow ones are interleaved with the fast across thirty services. The log search returns a million lines. Forty minutes in, the on-call team — whether three engineers across three tools or one engineer across the six widgets of a unified platform — still cannot say what changed. The instrumentation works correctly. The way it was reached for does not.*

This article is the first half of a diptych. It reframes the observability stack around six intents that map to most production debugging work. A companion piece — [*Reading Performance Testing by Use Case*](/blog/performance-testing-by-use-case/) — applies the same exercise to the testing side. The two are intended to be read together; this side stands on its own in the meantime.

## The taxonomy problem

Open any observability vendor's marketing site and the structure is immediately recognisable: *Metrics. Traces. Logs. Profiling.* Sometimes events. Sometimes RUM. The structure is convenient — it maps to internal product teams, to billing pages, to integration tabs. It is the structure of what is *being sold*, not of what is *being done*.

Practitioners do not arrive at observability with a request to "buy metrics." They arrive with a question: *why did the p99 of the cart service triple at 14:30 yesterday?*, *why does this batch take twelve hours when last week it took six?*, *why is the new microservice slower than the monolith it replaced?* These questions are intent-shaped. None of them maps to a single building block. Most of them require a *combination* of building blocks, used in a specific order, with specific failure modes when the combination is wrong.

Reading observability by intent flips the entry point back to the practitioner's question. The operational consequence, observed across incidents like the one above, is that the time-to-first-useful-signal collapses from tens of minutes to a few — not because anyone bought a faster tool, but because the on-call reaches for the right tool first. The savings live entirely in the routing decision.

## Six intents that cover most observability work

| Intent | Building blocks | Representative tools |
|--------|-----------------|----------------------|
| **1. Golden Signals / RED / USE** | Metrics, dashboards, alerting | Prometheus, Grafana, VictoriaMetrics, Alertmanager |
| **2. Latency propagation & dependency analysis** | Distributed tracing | OpenTelemetry, Jaeger, Tempo, Zipkin |
| **3. High-cardinality debugging & unknown-unknowns** | Event-based observability, rich-context logging | OpenTelemetry, Honeycomb, structured logging stacks |
| **4. Low-overhead production profiling** | Continuous profiling, eBPF | Parca, Pyroscope, async-profiler, bpftrace |
| **5. Black-box & legacy systems** | Metrics scraping, log-based analysis | StatsD, Graphite, Zabbix, Checkmk |
| **6. Cost-efficient observability at scale** | Telemetry pipelines, sampling | OpenTelemetry Collector, Vector, Fluent Bit |

The six intents do not partition the space — most real production work touches several of them on the way to the answer. The point of the table is not exhaustiveness but *entry*: what intent maps to the question on your screen.

## Intent 1 — Golden Signals / RED / USE

The intent here is the simplest and the most universal: *is this service healthy, and if not, where in its operating envelope is it failing?*

The workflow is by now classical. Pick the level of analysis: per-service (the Four Golden Signals — latency, traffic, errors, saturation — or their RED restatement: Rate, Errors, Duration) or per-resource (USE — Utilisation, Saturation, Errors). Instrument the relevant counters and gauges. Attach an alerting rule to the threshold that matters. Watch a dashboard for context.

The right tool combination is what most cloud-native shops already have on the wall: a metrics back-end (Prometheus, VictoriaMetrics, Mimir for scale), a visualisation layer (Grafana, Perses), and an alert manager. The OpenTelemetry metrics SDK is the converging instrumentation surface; the back-end becomes a question of scale, retention, and cost.

The anti-pattern to avoid is reaching for *logs* to compute service-level signals. Aggregating five minutes of access logs to compute a request rate or a 99th-percentile latency works once, breaks at scale, becomes expensive at large scale, and silently deceives at very large scale (sampled logs lose the tail, and the tail is what you wanted to see). Metrics are the right substrate for this intent. Logs serve a different intent — see Intent 3.

A second anti-pattern: alerting on causes instead of symptoms. A rule per metric — CPU above 80 %, queue depth above N, disk at 90 % — pages on conditions users may never notice, and trains the on-call to ignore the pager. Alert on the symptoms (the golden signals at the service boundary); keep the causes for the dashboard the alert links to.

## Intent 2 — Latency propagation & dependency analysis

The intent: *user request X took 2.3 s; which service in the call graph is responsible, and why?*

The workflow is "start at the slow user span and walk upstream." A trace is a tree of spans; the leaf or sub-tree where the bulk of the duration lives is the suspect. Critically, this is **not** an aggregate question — it is asked of an individual request, and answered by examining that request's trace.

The right tool combination is OpenTelemetry SDKs at the application layer, an OTel Collector for transport and sampling, and a tracing back-end (Jaeger, Grafana Tempo, Zipkin, or a commercial APM that consumes OTLP). The choice of back-end is dominated by storage cost and query ergonomics; the instrumentation layer should remain OTel for portability.

The anti-pattern to avoid is *trying to do this with metrics*. Per-service p99 dashboards do not tell you which downstream call is responsible for a *particular* slow request — they aggregate across all requests, and the aggregate hides the causal chain. Service maps generated from metrics show topology, not propagation. Tracing exists because metrics are the wrong shape for this question.

A second anti-pattern: heavy sampling at the wrong layer. Sampling 1 % of traces uniformly will lose almost all instances of the rare slow paths. Tail-based sampling at the OTel Collector — keep traces with errors, keep traces above a latency threshold — is structurally honest and cost-efficient.

## Intent 3 — High-cardinality debugging & unknown-unknowns

The intent: *something is wrong, but I do not know yet which dimension matters — is it a specific user agent, a specific tenant, a specific feature flag, a specific deployment region? I need to slice and re-slice until the suspect dimension reveals itself.*

This is the case the **event-based observability** school (Charity Majors, Honeycomb, the *Observability Engineering* book) was built for. Each request emits a single rich event tagged with every dimension that might matter — user ID, tenant, region, feature flags active, build hash, browser, latency. Querying then becomes "group by *anything* and look for outliers."

The right tool combination is an event ingestion path that does not pre-aggregate (Honeycomb is the canonical example; OpenTelemetry tracing back-ends increasingly serve this role; mature structured-logging stacks with index-on-read approach the same point from a different angle). The key property is **high cardinality and high dimensionality** — many distinct values per dimension, many dimensions per event.

The anti-pattern to avoid is *pre-aggregating before knowing the question*. Classical metrics pipelines compress events into time-bucketed counters, which is what makes them cheap — but it also commits you to a fixed cardinality. The dimension you want to slice by tomorrow has been thrown away yesterday. The discipline of high-cardinality observability is to keep the events whole until query time.

A second anti-pattern: assuming structured logs alone are sufficient. They are *closer* to the right shape than unstructured logs, but log pipelines that index on a fixed schema lose the property that matters here — that any field can become a query dimension at debug time, including fields nobody knew to declare in advance.

## Intent 4 — Low-overhead production profiling

The intent: *the metrics tell me a service is slow, the trace tells me which service is slow, but neither tells me which lines of code are slow inside that service.*

This is the home territory of the **continuous profiling** family. Sampling-based profilers (Parca, Pyroscope, async-profiler in low-frequency mode) attach to a running process, collect stack samples at a low rate, and produce flame graphs that show *where time is being spent in the code*. eBPF-based variants (the Parca agent, Pyroscope's eBPF mode, the OpenTelemetry eBPF profiler) extend the same approach to the kernel and to processes that cannot be modified.

The right entry point is "after the trace, before the local profiler." A trace identifies the service; a continuous profile identifies the code path *within* the service that is responsible for the cost. The two are complementary — neither replaces the other.

The anti-pattern to avoid is *running a high-frequency profiler in production*. async-profiler at its default rate is fine; pushed to a kHz sample rate it can become non-trivial overhead. The discipline is to sample at a low rate continuously, not to attach a high-rate profiler reactively when an incident is in progress (the act of attaching changes the system, and the incident is the worst time to confirm that).

A second anti-pattern: relying on profiles alone for causation. A flame graph shows *what is hot*, not *why it is hot*. The why usually requires combining the profile with traces, metrics, or domain knowledge.

## Intent 5 — Black-box & legacy systems

The intent: *I cannot instrument the system. It is a vendor appliance, a regulated environment that forbids agent installation, a 1996 mainframe that nobody is going to recompile, or a closed third-party SaaS.*

This is where the older observability lineage — StatsD, Graphite, Nagios, Zabbix, Checkmk — earns its place. These tools were built for a world without distributed tracing and largely without OpenTelemetry; their craft is in **what can be observed from outside the system**: SNMP polling, log scraping, network probes, synthetic checks, agent-based metrics collection from the OS layer.

The right tool combination depends on the constraints. For a regulated production environment where instrumentation is forbidden by audit, agent-based collectors (Telegraf, Netdata, Checkmk) feed a metrics back-end via standard interfaces. For a vendor SaaS, the API endpoint metrics, plus synthetic transactions, plus log ingestion, are usually the only signals available. For a legacy host, SNMP and log shipping remain serviceable.

The anti-pattern to avoid is *treating greenfield systems with black-box methods*. A Kubernetes microservice that you control should be instrumented at the application layer. Falling back to SNMP polling because that is the team's habit is a missed opportunity, and it produces lower-fidelity data than the system natively supports.

The reverse anti-pattern is also real: assuming OpenTelemetry can replace the black-box layer. Most heterogeneous environments will run both paths in parallel for years. The choice is not OTel-or-nothing; it is which subset of the system gets which level of fidelity, and what the explicit migration plan is for the rest. Without that plan, the black-box layer becomes permanent by default.

## Intent 6 — Cost-efficient observability at scale

The intent: *the bill arrived, the bill was eye-watering, and now I have to bring it down without losing the signal I depend on.*

This intent is increasingly load-bearing. Observability data volumes have outgrown the linear pricing models that supported the previous generation of stacks. The architectural answer is the **telemetry pipeline** layer — a buffer between the application and the back-end where data can be sampled, dropped, transformed, routed, and re-shaped.

The right tool combination centres on the OpenTelemetry Collector (the converging standard), Vector (Rust-based, high throughput, mature transformation language), and Fluent Bit (lightweight, embedded, log-focused). The pipeline executes the cost-control policy: tail-based trace sampling, attribute pruning to remove cardinality-bombing labels before they hit the back-end, log-level filtering, and dual-routing to send a high-fidelity stream to a cheap archive while sending a sampled stream to the queryable back-end.

The anti-pattern to avoid is *cardinality bombs*. A single misconfigured label — `user_id` on a high-traffic metric, an unbounded HTTP path, a request ID — can multiply metric series by orders of magnitude and dominate the cost. Catching cardinality bombs at the pipeline layer (before they hit the TSDB) is usually cheaper and faster than catching them at ingestion (where they can take down the back-end first).

A second anti-pattern: cost-cutting by aggregation that destroys the question one wanted to ask. Sampling 1 % uniformly is mathematically simple and operationally lossy — the rare events are exactly the events you keep observability for. Sampling configured with intent preserves the signal while reducing volume — tail-based for outcome-dependent rules (keep errors, keep p99 outliers, keep slow traces), head-based only for what is known upfront (per-route or per-tenant rates).

## Where unified APM platforms fit in this picture

The article so far has assumed a stack of specialised tools — Prometheus, Jaeger, Loki, Pyroscope, each chosen for one intent. That assumption fits cloud-native and OSS-oriented teams; it fits much less well the very large population of organisations whose observability is consolidated on a single commercial platform — **Datadog, New Relic, Dynatrace**, and increasingly Grafana Cloud. The intent framing must hold up here too, or it does not hold up at all.

### Coverage

| Intent | Datadog | New Relic | Dynatrace | Where specialists still pull ahead |
|--------|---------|-----------|-----------|-----------------------------------|
| 1. Golden Signals | ✅ native | ✅ native | ✅ native | Prometheus + Grafana at marginal zero cost when already deployed |
| 2. Latency propagation | ✅ mature APM | ✅ mature APM | ✅ **PurePath** — code-level, end-to-end transaction tracing; arguably the deepest available | Jaeger / Tempo for extreme-scale storage |
| 3. High-cardinality | 🟡 progressing | 🟡 NRDB closest of the three | 🟡 Grail/DQL queries raw data ad hoc; Davis correlates | **Honeycomb** — no other tool truly competes here |
| 4. Continuous profiling | ✅ wide-language profiler | 🟡 Pixie-derived, partial | ✅ code-level via PurePath | Pyroscope at much lower marginal cost |
| 5. Black-box / legacy | ✅ broad integration catalogue | ✅ idem | ✅ idem | No major specialist advantage |
| 6. Cost-efficient at scale | ❌ the platform *is* the cost problem | ❌ idem (per-user pricing slightly more predictable) | ❌ idem | OTel Collector + Vector + Fluent Bit exist *to manage* the platform bills |

The platforms genuinely cover most intents, often very well. They are not theatre.

### The decision moves; the platform forgives wrong moves

The temptation on reading the coverage table is to conclude that the unified platform supersedes the intent framing — *if all six intents live behind one URL, why decide?* That reading mistakes what consolidation actually changes.

The decision is still there. Inside the Datadog console, the on-call engineer at 12:14 still has to choose between *Service Map*, *Dashboard*, *Trace Explorer with latency filter*, *Logs Live Tail with custom facets*, *Continuous Profiler*, and *Watchdog*. These are the six intents of this article, renamed as widgets. The platform unifies the *substrate*; it does not absorb the *intent decision*.

What the platform *does* change — and this is the central operational value, frequently underplayed in vendor messaging — is the **cost of a wrong first move**. In a specialised-tool world, an incorrect first move is expensive: each pivot to a different tool requires re-establishing context (timestamps, trace IDs, service filters, time windows) by hand. In a unified platform, that context propagates automatically: an error in the log opens to its source trace; the trace opens to a continuous profile of the service at that exact instant; the profile opens to a metric timeseries aligned on the same window with deployment markers visible.

The on-call engineer can therefore follow a sub-optimal cognitive path — pursue an incorrect hypothesis for thirty seconds, see that it leads nowhere, and pivot — without paying minutes of re-contextualisation. The skill of intent-routing is not eliminated; it shifts from a *first-move skill* (expensive in a specialised world, because each tool start is costly) to a *dead-end-recognition skill* (cheap in a unified world, because pivoting is cheap). At 02:00, when the engineer is least able to choose optimally, this forgiveness of wrong moves is the single most operationally valuable property the platform provides.

That property has limits. Context propagation works inside the platform's data model; pivoting to anything outside (a partner-SaaS log, a PostgreSQL execution plan, a profiler not in catalogue) breaks the chain. The rebound also assumes the data exists — if the dimension you want to slice by was sampled away at ingest, the cognitive trail dead-ends against an invisible wall, which is worse than a visible one. And for very deep incidents — cross-team, multi-day, multi-hypothesis — the platform's pre-cabled paths become a constraint, not a feature.

### Where specialists still keep a structural edge

Two intents withstand the unified-platform argument. The first is **Intent 3 (high-cardinality)**, where Honeycomb's design — ingest rich events, never pre-aggregate — produces a substantively different debugging experience. The big platforms have progressed (New Relic's NRDB and Dynatrace's Grail are closest), but none of them can group-by-anything at scale-stable pricing the way an event store designed for it can.

The second is **Intent 6 (cost)**, and it deserves its own treatment.

### The Intent 6 paradox, in lived form

A composite — no single team said exactly this — but the trajectory of a Datadog (or New Relic, or Dynatrace) adoption is recognisable in the field:

> **Year 1** — *"We have everything in one platform. Time-to-resolution is down, on-call quality of life is up, this is transformative."*
>
> **Year 2** — *"The bill has tripled. We are now the largest line item in the SaaS budget."*
>
> **Year 3** — *"We deploy an OTel Collector in front of the platform to sample traces and prune labels before ingestion. We cap log retention at 7 days. We stand up an OpenSearch cluster alongside the platform to retain logs longer at a fraction of the cost."*

Three things break in year 3, all of them quiet:

- **Reducing log or trace retention to 7 days** fragilises post-mortems on slow-incubating incidents — the cloud-native ones that surface a week after deploy.
- **Aggressive sampling at ingest** silently disables the high-cardinality debugging the platform was supposed to enable; the dimension you want to slice by tomorrow is no longer in the data today.
- **Multiplying back-ends** (Datadog + OpenSearch for logs, often + a separate metrics store, sometimes + a separate profiler) re-introduces exactly the cross-tool context-loss the platform was originally bought to eliminate.

The cost discipline that makes year 3 sustainable structurally fights against the integration property that made year 1 valuable. There is no clean exit from this — it is the genuine paradox of the unified-platform model at scale.

### What this means for the article's thesis

The intent framing is not invalidated by the existence of unified platforms; it is sharpened. In a specialised-tool environment, intent-routing is a *first-move skill* — opening the wrong tool wastes minutes. In a unified-platform environment, intent-routing becomes a *dead-end-recognition skill* — staying in the wrong widget wastes seconds, but staying *unaware that the data has been sampled away* wastes the entire incident. In both worlds, the discipline is the same: name the intent before you reach.

## A decision tree

When the dashboard turns red and the page goes out, the question to ask first is not *which tool* but *which intent*. A simple heuristic:

```
Is the question "is the service healthy?"
  → Intent 1. Reach for metrics dashboards and the alert that fired.

Is the question "where in the call graph did the time go?"
  → Intent 2. Reach for the trace of the slow request.

Is the question "which dimension is the symptom correlated with?"
  → Intent 3. Reach for the event-based / high-cardinality store.

Is the question "where in the code is the time spent?"
  → Intent 4. Reach for the continuous profile (after Intent 2 has narrowed to a service).

Is the question "what can I see from outside?"
  → Intent 5. Reach for the black-box collector — but verify that
    no inside view was actually available first.

Is the question "why is this so expensive?"
  → Intent 6. Reach for the telemetry pipeline first, the back-end
    second, the application instrumentation third.
```

The tree is not the truth, but it is a structured first move when the alternative is opening every dashboard at once. Most real incidents touch two or three of the intents in succession; recognising which one applies *now* shortens the path.

## What this reframing changes

Three things, in increasing order of disruption:

1. **It exposes redundancy in the stack.** A team that has bought a metrics platform, a logs platform, an APM platform, and a profiling platform — but uses each one for the intent it was sold for — is paying for capabilities that overlap and missing intents that none of them address well.
2. **It exposes under-investment.** Most real observability gaps are not in the metrics/traces/logs trio. They are in Intent 6 (the pipeline layer is afterthought-quality) and in Intent 3 (high-cardinality is the slowest to mature). Reading by intent makes the asymmetry visible.
3. **It forces tool combinations rather than tool stacks.** Intents 2 and 4 reinforce each other when wired together: a trace narrows the suspect to a service, a continuous profile narrows it within the service, and the combined cost is one mid-sized profiler agent plus a tracing back-end — far less than two platforms bought separately. Intent 3 only matures when Intent 6's pipeline runs tail-based sampling that preserves the rare-but-interesting events; without that pairing, high-cardinality observability either bankrupts the budget or sheds the signal it was meant to keep. These are decisions about *how the existing tools talk to each other*, not about which platform to buy. The discipline is integration, not procurement.

If you take one thing from this reframing: when next paged, ask "what intent is this?" before opening any tool. Naming the intent is free; the cost of mis-routing — measured in minutes added to time-to-resolution — is the highest cost paid during the entire incident.

## Companion piece

A second article in this diptych — [*Reading Performance Testing by Use Case*](/blog/performance-testing-by-use-case/) — applies the same exercise to the testing side. Together, the two attempt to bridge a gap that most performance engineering practice still treats as separate: *observability* and *testing* are taught as different domains, owned by different teams, using different toolchains. They are, in fact, two views of the same problem — *understanding how a system behaves*. The first via the production system itself; the second via controlled probes against it.

The full curated catalogue of the tools cited above is on the [Awesome Performance Engineering](/awesome-performance-engineering/) page maintained alongside this blog.

## Further reading

The references below are also collected in this site's [library of foundational works](/library/), under *Observability*.

{% references() %}

Majors, C., Fong-Jones, L., & Miranda, G. (2022). *Observability Engineering.* O'Reilly. — The contemporary canonical text on observability as a property of systems. The argument for high-cardinality, high-dimensionality data is its central thread.

Sridharan, C. (2018). *Distributed Systems Observability.* O'Reilly. [Free online](https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/). — The earlier and shorter introduction, with a clear treatment of the three pillars and their failure modes.

Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (Eds.). (2016). *Site Reliability Engineering.* O'Reilly. [Free online](https://sre.google/sre-book/table-of-contents/). — The book that established the Four Golden Signals as a service-health methodology; RED (Tom Wilkie) and USE (Brendan Gregg) are its service-level and resource-level counterparts.

Gregg, B. *The USE Method.* [brendangregg.com/usemethod.html](https://www.brendangregg.com/usemethod.html). — The canonical exposition of the resource-analysis discipline, by its author.

OpenTelemetry. *OpenTelemetry Documentation.* [opentelemetry.io/docs/](https://opentelemetry.io/docs/). — The primary reference for the converging instrumentation standard.

CNCF Observability Technical Advisory Group. *TAG-Observability community resources.* [github.com/cncf/tag-observability](https://github.com/cncf/tag-observability). — Vendor-neutral community standards and whitepapers.

{% end %}
