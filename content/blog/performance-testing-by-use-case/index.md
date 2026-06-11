+++
title = "Reading Performance Testing by Use Case"
date = 2026-06-11
toc = true

description = "Most performance-testing programmes have a load generator. Few have a representative dataset. Almost none can inject failures while measuring user-perceived latency. The reasons are multi-causal — a culture that treats performance as a release-time formality, plans that under-budget the supporting work, applications whose testability was never designed in, and a tool catalogue organised by category rather than by intent. This article reframes performance testing around seven use cases — API load testing in CI/CD, full-stack validation, microservice resilience, database benchmarking, frontend optimisation, capacity planning, and pre-production data realism — and uses them as the spine of a practical campaign-setup guide: what each test is trying to prove, what testability hooks it requires, what it realistically costs, what cultural pre-requisites it has, and which combination of tools assembles it."

[taxonomies]
tags = ["performance engineering", "performance testing", "load testing", "chaos engineering", "k6"]

[extra]
giscus = true
copy_button = true
footnote_backlinks = true
+++

> *Most performance-testing programmes have a load generator. Most do not have a representative dataset. Most do not have a way to inject failures while measuring user-perceived latency. The asymmetry is consistent across organisations and consistent across years — and the reasons are consistent too: a culture in which performance is treated as a release-time formality, plans that under-budget the supporting work, applications whose testability was never designed in, and a tool catalogue organised by category rather than by intent. A green pre-release benchmark followed by a 14:30 production page-out is the routine cost of all four together.*

Of those four causes, the fourth — *framing* — is upstream of the other three. A team that cannot articulate what its test is trying to prove cannot budget for it, cannot ask for the testability hooks it needs, and cannot grow a culture around it. This article focuses on framing first: seven use cases that name what performance tests actually try to prove, each accompanied by the testability hooks the test requires, the realistic costs and timelines, the cultural pre-requisites, and the tool combinations that assemble it.

## Why the tool question comes last

Open any list of performance-testing tools and the structure repeats: *load testing. HTTP benchmarking. Browser performance. Chaos engineering. Service virtualisation. Data generation.* Sometimes profiling. Sometimes results analysis. The categories are real — they correspond to genuine sub-disciplines, each with its own literature, conferences, and product market.

The categories are also, by themselves, almost useless to a practitioner deciding what to do next.

Performance testing is hardly ever a single-category activity. *API load testing in CI/CD* is load testing plus pipeline integration plus result-comparison tooling. *Full-stack validation* is load testing plus browser perf plus observability correlation. *Microservice resilience testing* is chaos engineering plus service virtualisation plus user-latency measurement. The tools that win in one category and the tools that win in another can be combined into a stack that does what a single-category tool could not do alone — or, just as easily, into a stack that wastes everyone's time because the combinations were chosen by category rather than by use case.

A team that opens its annual planning conversation with *"what perf-testing tool should we adopt?"* has already framed itself out of the actually useful questions. The tool decision comes last. The questions that come first are four, in this order:

1. **What is this test trying to prove?** (the use case, the hypothesis)
2. **What does the application need to expose for the test to be possible?** (testability)
3. **What does the campaign realistically cost — set up, run, analyse?** (calibrage)
4. **What does the team need to accept for the result to drive a decision?** (culture)

(The French *calibrage* is kept untranslated throughout: it covers in one word the sizing of setup effort, run cost, and analysis time against the decision the test serves — "costing" captures only part of it.)

The seven use cases below are the entry point. Each one names a hypothesis, then walks through what that hypothesis requires of the application, of the project plan, of the team, and finally of the tool combination. The order matters — the tool is the last decision, not the first.

## Seven use cases that cover most testing work

| Use case | Tool categories involved | Representative tools |
|----------|--------------------------|----------------------|
| **1. API load testing in CI/CD** | Load testing, CI/CD integration, regression detection | k6, Gatling, Artillery |
| **2. Full-stack performance validation** | Load testing, browser perf, observability correlation | k6, Lighthouse, Grafana, OpenTelemetry |
| **3. Microservice resilience testing** | Chaos engineering, service virtualisation, latency measurement | Litmus, Chaos Mesh, Gremlin, WireMock |
| **4. Database performance benchmarking** | Benchmarking, data generation, replay | HammerDB, sysbench, pgbench, Faker |
| **5. Frontend experience optimisation** | Browser performance, RUM, synthetic monitoring | Lighthouse, WebPageTest, Playwright, web-vitals |
| **6. Capacity planning & saturation testing** | Load testing (open-loop), HTTP benchmarking | Gatling open injection, wrk2, Vegeta, Hyperfoil |
| **7. Pre-production data realism** | Data generation, service virtualisation, anonymisation | Faker, DataFaker, WireMock, Mockaroo |

The seven use cases do not partition the space — most non-trivial testing programmes touch several of them simultaneously. The point of the table is not exhaustiveness but *entry*: what use case maps to the question you are actually trying to answer.

## Use case 1 — API load testing in CI/CD

**The use case** — *every change to this API should be measured against a known load profile, and a regression should fail the pipeline before merge.*

**Points of attention**

- *Testability*: the service must expose a load profile that maps to production traffic shape. If only `/health` is hit, the test is exercising the wrong thing. The test target must also be deployable on each PR — usually as a containerised replica spun up by the pipeline.
- *Calibrage*: the test must be light enough to run on every change — typically under 10 minutes including warmup. A 60-minute test will not survive the first month. Cloud-load costs scale with frequency × duration; budget for it before agreeing the cadence.
- *Culture*: the team must accept that performance is a *merge gate*, not a release-time check. Without that contract, the gate gets disabled on the first false positive that delays an unrelated feature.

**The right tool combination** is a load generator with a CLI and a machine-readable result format (k6, Gatling, Artillery), a pipeline integration that runs it against the representative target, and a regression detector that compares the result to a historical baseline. The detector is the under-loved piece. Shared CI runners are noisy neighbours — percentiles drift run-to-run for reasons unrelated to the code — and that noise is what kills fixed-threshold gates: they either fire constantly or never. Change-point detection on percentile time series (the *Hunter* paper from DataStax is a useful reference) is the honest alternative; a dedicated, consistent runner for the performance job is its complementary testability requirement.

**Workflow at maturity**: PR opens → pipeline runs the load test against the candidate → result is compared to the rolling baseline of the main branch → a statistically significant regression fails the merge → the developer either explains the regression or fixes it.

**Anti-pattern to avoid**: *load tests that pass once and never run again*. A pre-release load test that took two weeks to author, ran once, and then sat in a wiki page is not a regression detector — it is a souvenir.

**A second anti-pattern**: gating on average latency. A regression confined to the tail barely moves the mean — it gets diluted away by the fast majority. Configure the gate on p95 or p99, not on the mean.

## Use case 2 — Full-stack performance validation

**The use case** — *the next release combines a backend change, a frontend change, and an infrastructure change. Did the user-perceived latency improve, regress, or stay flat?*

**Points of attention**

- *Testability*: the full user journey must be reachable from a single test driver. Hidden auth flows, multi-domain redirects, or handshake protocols that only the frontend knows break the test before it starts. End-to-end trace propagation (OpenTelemetry trace IDs flowing from browser to backend) is a prerequisite, not a nice-to-have.
- *Calibrage*: full-stack tests take 10×–100× longer to set up than single-layer tests because they require coordination across teams (backend, frontend, platform). Budget weeks, not days, for the first iteration; budget recurring time for maintenance after each architecture change.
- *Culture*: requires accepting that the test result is *one number for the user journey*, not three numbers (one per team). Teams that compete on layer-specific KPIs resist this framing — the political work happens before the technical work.

**The right tool combination** joins the layers explicitly. A browser-driving load tool (Playwright, k6 with the browser module, Cypress in performance mode) issues realistic user journeys; an observability layer (OpenTelemetry instrumentation in the application, Grafana for the metrics) captures the backend trace; the result is a test that says *"the checkout journey on this build takes X ms end-to-end, of which Y ms is server time and Z ms is browser rendering."*

**Workflow at maturity**: deploy the release candidate to a full-stack staging environment → run the browser-driven journey under a modest concurrent load → decompose the end-to-end number via the trace into server, network, and rendering time → compare the decomposition, layer by layer, against the previous release's.

**Anti-pattern to avoid**: *testing layers in isolation and assuming the sum is the truth*. Backend p95 and frontend Largest Contentful Paint do not add — they overlap, they interact, and one can mask the other when measured separately. The only number that predicts the user-observable outcome is the one measured end-to-end on the actual journey, not the arithmetic of two layer-local p95s.

**A second anti-pattern, more subtle**: validating against synthetic backend mocks. The mock replies in 1 ms; the real service replies in 80 ms. The frontend test shows a fast Time to Interactive that production will never reproduce.

## Use case 3 — Microservice resilience testing

**The use case** — *do the user-observable signals — latency, error rate, completion of the user journey — degrade gracefully when an upstream dependency fails, slows down, or returns garbage?*

**Points of attention**

- *Testability*: the fault injector needs a hook into the right layer (Kubernetes for pod-level, a service mesh for HTTP-level, network for latency injection). Systems without those layers exposed for testing make resilience testing effectively impossible without re-architecting first. This is the use case most often blocked by upstream testability decisions.
- *Calibrage*: chaos experiments take hours to set up (hypothesis, injection, measurement, rollback) and minutes to run. They cannot be parallelised easily — each experiment needs the system in a known state. Plan one experiment per week per service, not per day.
- *Culture*: the highest cultural barrier of the seven use cases. The team must accept that *inducing failure* in non-prod is normal engineering work, not a stunt. Without that acceptance, chaos experiments degrade to quarterly game days, then to annual ones, then to absence — and the discipline dies quietly.

**The right tool combination** is a chaos-engineering platform that can inject controlled failures at the right layer (Litmus or Chaos Mesh in Kubernetes; Gremlin as a managed service; toxiproxy at the network edge for finer control), a service-virtualisation tool for upstream dependency misbehaviour (WireMock is the workhorse), and — critically — a measurement layer that captures *user-observable* metrics during the chaos run. Observation is what makes resilience testing different from breaking-things-for-fun.

**Workflow**: steady-state hypothesis → fault injection → measurement → comparison. The hypothesis is *"if dependency X returns 500 ms latency for 30 seconds, the user-facing p99 should stay below 1 s."* The injection runs the fault for the agreed duration. The measurement layer records the actual user-facing p99. Hypothesis violated → system more fragile than the team thought; validated → next dependency.

**Anti-pattern to avoid**: *resilience testing that does not measure user-observable latency*. Killing a pod and watching the pod re-spawn is not a resilience test; it is a reconciliation test. The question is not "does Kubernetes do its job?" — the question is "does the user notice?". Without an observation layer wired to the chaos run, the test produces no evidence of either side.

**A second anti-pattern**: validating only the dependency-failure case. Most production incidents do not involve dependencies *failing*; they involve dependencies *getting slow*. Latency injection is harder to set up and far more revealing than failure injection.

## Use case 4 — Database performance benchmarking

**The use case** — *will this database (engine, version, schema, hardware tier) sustain the workload we are about to put on it?*

**Points of attention**

- *Testability*: the test database must match the production hardware tier, OS, kernel, filesystem, and storage layer. A benchmark on a different storage system is fiction. The instrumentation also matters: the database's internal counters (buffer-pool hit rate, lock waits, checkpoint behaviour) must be queryable during the run, not just the client-side latency.
- *Calibrage*: building a representative dataset is often 80% of the work and 5% of the planning. Block weeks upfront. The benchmark itself must run long enough to cross the relevant cache layers (buffer pool warmup, OS page cache, disk caches) — plan hours per run, not minutes.
- *Culture*: database benchmarks need a DBA in the room to interpret the internal counters. Without that expertise, the numbers are reported but not understood — and the test produces no actionable result. A perf engineer working alone on a database benchmark is producing material for a DBA's later interpretation, not a finished result.

**The right tool combination** is a benchmark running a representative workload (HammerDB for OLTP, sysbench for synthetic primitives, pgbench for PostgreSQL specifically), a data generator producing a representative dataset (Faker or DataFaker for shape, restored production snapshots when permissible for cardinality), and a measurement harness capturing the database's own internal counters alongside the client-side latency.

**Workflow at maturity**: define the target workload mix → generate or restore a dataset of representative cardinality → run the benchmark long enough to cross the cache layers → record latencies, throughput, and database internal metrics → compare against the engineering target.

**Anti-pattern to avoid**: *benchmarking against a tiny dataset and concluding that the database is fast*. A 100 MB dataset that fits in the buffer pool says nothing about a 200 GB working set on a server with 32 GB of RAM. The *cardinality of distinct values per indexed column* is the parameter that moves the answer most.

**A second anti-pattern**: benchmarking single primitives in isolation (pure-INSERT, pure-SELECT) and reporting the numbers as though they characterised the production workload. Real workloads are mixes; the contention behaviour of a 70/30 read/write workload is not predicted by the throughput of either side run alone.

## Use case 5 — Frontend experience optimisation

**The use case** — *the browser experience is slow. Where is the time going, and what change to the build, the assets, or the rendering path moves the needle?*

**Points of attention**

- *Testability*: synthetic measurements require a representative test page (not just the marketing home page) and a stable test environment that does not change between runs. RUM measurements require user consent, a beacon endpoint, and a back-end pipeline to receive and aggregate the data — non-trivial in jurisdictions with strict privacy law (GDPR opt-in flow needs to be designed before the data flows).
- *Calibrage*: synthetic measurement is cheap (seconds per run, free tooling). RUM is operationally non-trivial — sampling design, beacon endpoint engineering, analysis pipeline. Budget the RUM pipeline as engineering work, not as a tool purchase. The Lighthouse-CI part is cheap; the RUM-correlation part is not.
- *Culture*: requires accepting that Core Web Vitals are a *product metric*, not a developer-only concern. Teams whose product organisation does not own performance numbers struggle to act on them — the data exists, but no decision follows.

**The right tool combination** divides between *synthetic* (lab-controlled, repeatable) and *real-user* measurement. Synthetic tools (Lighthouse, WebPageTest, Playwright with metrics, the underlying `web-vitals` library) produce controlled measurements of Core Web Vitals and waterfall traces. RUM tools (commercial APM-RUM products, or DIY with `web-vitals` plus a back-end) produce the actual distribution as users see it.

Both are necessary. Synthetic measurement gives signal-to-noise that real-user cannot match — the same test on the same build produces nearly identical results, which is what makes regression detection feasible. RUM gives the truth about what users actually experience — including network heterogeneity, device heterogeneity, and the long tail that synthetic measurement never sees.

**Workflow at maturity**: synthetic measurement gates the pipeline; RUM measurement validates that the lab improvements translated to real users; the two diverge in interesting cases — a test that improves Lighthouse but not RUM is usually optimising a metric the lab measures and users do not notice.

**Anti-pattern to avoid**: *running Lighthouse once on a marketing page and declaring the site fast*. Web performance is workload-dependent: the first page paint is one workload, the long-tail interaction-heavy session is another. Both deserve measurement; neither characterises the other.

**A second anti-pattern**: optimising for synthetic scores at the expense of real-user impact. A Lighthouse improvement that does not move the RUM distribution is, by construction, optimising a benchmark behaviour and not a user-perceptible one — most often by tuning a build-time choice (asset preloading, image format, render-blocking-script reordering) that the synthetic harness rewards but the typical user's network or device never benefits from.

## Use case 6 — Capacity planning & saturation testing

**The use case** — *what is the maximum sustainable rate this system can serve, and what does it do as it approaches the wall?*

**Points of attention**

- *Testability*: capacity tests need an environment *sized to production*. A test against a 1/10th-scale staging environment is a 1/10th-truth answer. The load target also needs to be reachable at the target rate without rate-limiting the test infrastructure itself — a frequent footgun when the test rig sits behind the same WAF as production.
- *Calibrage*: open-loop generation needs headroom in the test rig itself — in tools whose arrival-rate executors draw on a VU pool (k6, Gatling), the pool must be large enough to absorb the queueing peak under stress (the k6 `dropped_iterations` footgun, treated at length in [*Coordinated Omission*](/blog/coordinated-omission/)). Plan capacity for the *test infrastructure*, not just the target. Cloud-load injection at 1 000+ rps for an hour can cost thousands of dollars per run — discover that before agreeing the cadence with the architecture team.
- *Culture*: capacity tests produce numbers that drive infrastructure decisions (*"we need 30 % more headroom"*). The team must accept that those decisions follow the test, not the test budget. Otherwise the test gets tuned to produce the affordable answer, and the exercise loses its informational value.

**The right tool combination** is an *open-loop* load generator (Gatling with open injection profiles, wrk2, Vegeta, Hyperfoil), a load profile that ramps the target rate through the suspected breaking point, and a measurement layer capturing both server-side metrics (utilisation, saturation, errors — the USE method) and client-side latency including queueing delay.

**The crucial constraint** is the workload model. A closed-loop tool (default `wrk`, `ab`, `hey`, k6 in `constant-vus` mode) cannot honestly answer this question — when the system slows down, the tool slows with it, and the saturation behaviour is hidden by *coordinated omission*. Capacity planning *requires* an open-loop tool. Without it, the capacity number you produce is fiction.

**Workflow**: ramp the target rate through the suspected wall → capture latency and throughput at each rate → identify the inflection point at which latency starts to grow super-linearly with rate → compare against the engineering target.

**Anti-pattern to avoid**: *measuring throughput without measuring tail latency*. A system that sustains 10 000 rps with p99 of 50 ms is in a different operating regime from a system that sustains 10 000 rps with p99 of 8 s. Both report the same throughput. The second one will fail in production at any rate above the latency contract.

**A second anti-pattern**: averaging across the ramp. A latency distribution aggregated over the whole climb mixes the healthy regime with the saturated one and reports a number that describes neither. Hold each rate as a steady-state plateau, report per-plateau distributions, and let the inflection point show itself.

## Use case 7 — Pre-production data realism

**The use case** — *the test environment has 1 000 records. Production has 200 million. Every test result is a fiction until the cardinality matches.*

**Points of attention**

- *Testability*: characterising the production data shape (volume per table, cardinality per indexed column, value distribution) is the first task. Teams without DBA-side visibility on the production database cannot even start — characterisation itself becomes a pre-requisite project.
- *Calibrage*: building a realistic dataset is engineering work — typically weeks for the first iteration, ongoing maintenance after every schema change. Plan it as a sub-project with its own owner, not as a side-task of the test scenario. Anonymisation pipelines (for environments where production data exists but cannot be copied) double the effort.
- *Culture*: requires accepting that *data engineers, DBAs, and security people* will be in the planning meetings, not just the performance engineer. The cross-team coordination cost is where the realism budget actually lives, and the most under-invested use case is under-invested for that reason — no single team owns the work.

**The right tool combination** depends on the constraint. For greenfield testing, data generators (Faker, DataFaker, Mockaroo) populate datasets with controlled cardinality, distribution, and referential integrity. For schemas where production data exists but cannot be copied (PII, regulatory constraints), anonymisation pipelines (built on the same generators, plus deterministic hashing for keys) produce realistic-shape datasets. For dependency replacement, service virtualisation (WireMock for HTTP, mock-aware frameworks per protocol) substitutes upstream services with controllable behaviour.

**Workflow at maturity**: characterise the production data shape → generate or anonymise a dataset that matches the shape within the constraints → automate the regeneration so the dataset stays in sync with schema migrations.

**Anti-pattern to avoid**: *uniform-distribution synthetic data*. Real production data is rarely uniformly distributed. A user table with `Faker.name()` produces uniform-cardinality names; a real user table has heavy-tailed distributions (the 100 most common names cover 30 % of users; the long tail covers the rest). Index selectivity, cache hit rates, and query plans all depend on this shape — uniform synthetic data systematically under-represents the worst case.

## Where unified testing platforms fit — and what they leave untouched

Unified testing platforms — **BlazeMeter** (Perforce), **Tricentis NeoLoad**, **Grafana k6 Cloud**, **LoadRunner Enterprise** (OpenText), **Octoperf**, and others — are one of the most consequential adoption decisions a perf-testing programme will make. They consolidate what is well-defined and well-marketed: load generation, test scripting, distributed execution, cloud-based VU injection, results storage, comparison views, CI/CD hooks. The packaging is good, the engineering is real, the operational value at low maturity is genuine.

The question this article frames is: *for which use cases does the platform fit, and for which does it constrain?*

### Coverage

The same seven use cases, scored against what a unified platform actually delivers:

| Use case | What the platforms cover | What they leave open |
|----------|--------------------------|----------------------|
| 1. API load testing in CI/CD | ✅ Home territory. Scripting, distribution, CI hooks, baseline comparison — all integrated. | Regression detection is usually fixed-threshold, not change-point. |
| 2. Full-stack validation | 🟡 Some platforms (k6 Cloud) ship browser modules. Most do not. | The wire to a backend-observability layer (OTel traces, Grafana) stays a manual integration. |
| 3. Microservice resilience | ❌ Chaos engineering is not a platform feature. | Litmus, Chaos Mesh, Gremlin remain separate. The integration between chaos injection and user-observable latency stays custom. |
| 4. Database benchmarking | ❌ Outside scope: the platforms target application traffic, not database-internal benchmarks. | HammerDB / sysbench / pgbench remain separate tools with separate teams. |
| 5. Frontend optimisation | ❌ Lighthouse / WebPageTest / RUM are different products with different audiences. | The entire frontend stack remains untouched. |
| 6. Capacity planning | 🟡 Open-loop generation is supported (constant-arrival-rate or equivalent). | Per-VU pricing turns sustained ramps into budget conversations (the year-2 vignette below). |
| 7. Data realism | ❌ Generators are bundled at best, anonymisation pipelines never. | Characterising production shape and refreshing on schema migrations stays manual in every shop. |

The platforms solve use case 1 cleanly, partially solve 2 and 6, and leave 3, 4, 5, 7 untouched. A platform is therefore a real accelerator on a narrow front, and a no-op on a wide one.

### The recognisable trajectory

A composite — no single team said exactly this — but the pattern in the field is recognisable:

> **Year 1** — *"We adopted BlazeMeter for the load tests. The team can author scenarios in a day, the CI hooks work out of the box, reporting is clean. The previous home-grown k6-on-EC2 rig is decommissioned. This is transformative."*
>
> **Year 2** — *"The capacity test against the e-commerce backend costs $4 200 in cloud VU-hours per run. The performance lead has to file a budget exception for each one. The cadence drops from weekly to quarterly."*
>
> **Year 3** — *"We re-introduce k6-on-EKS for the high-frequency tests and keep BlazeMeter for executive demos. The data-realism pipeline still does not exist. Resilience testing is done by hand twice a year during the dependency upgrade window. The team feels behind."*

What this trajectory illustrates is not a flaw in the platforms — they do exactly what they are sold to do. It illustrates the *limit of what a tool decision can solve*. The platform answers parts of *calibrage* and *combination* — fine for use case 1, partial for 2 and 6. It answers neither *testability* nor *culture*, and it does not address the use cases (3, 4, 5, 7) where those two dimensions dominate. A team that adopts a platform and skips the four-question setup will, predictably, be in the year-3 situation within 18–24 months — not because the platform failed, but because the work the platform does not do was never started in parallel.

### What this means for the platform decision

A unified platform is the right adoption for use case 1 (CI/CD load) and a defensible accelerator for use cases 2 and 6 — *provided the platform's pricing model is compatible with the test cadence the team actually needs*.

The platform is not a substitute for the work each use case requires on testability, calibrage, and culture. Buying the platform without the surrounding work produces the year-3 trajectory; buying it *after* the surrounding work is in motion turns it into a force multiplier. The order matters more than the choice.

## A maturity ladder

Where a testing programme actually sits along these use cases is usually a more useful diagnostic than which tools it has bought. A simple three-rung ladder per use case:

| Use case | Getting started | Mature | World-class |
|----------|-----------------|--------|-------------|
| 1. CI/CD load | Manual run before release | Automated, fixed-threshold gate | Automated, change-point regression detection |
| 2. Full-stack | Backend tested in isolation | Backend + frontend tested separately | Single test exercises the journey end-to-end with observability correlation |
| 3. Resilience | Manual chaos game days | Automated chaos in non-prod | Continuous chaos in prod, with automatic rollback on observed user-impact |
| 4. Database | Synthetic primitives (sysbench defaults) | Representative workload mix | Production workload replay |
| 5. Frontend | Lighthouse on the home page | Synthetic + RUM on key journeys | RUM SLO on Core Web Vitals, regression-gated by synthetic |
| 6. Capacity | Closed-loop tool against staging | Open-loop tool, methodical ramp | Open-loop tool, queueing-theory-grounded interpretation, USL fit |
| 7. Data realism | Faker defaults | Production-shape synthetic | Anonymised replay with cardinality preserved |

The pattern across rungs is consistent: each step trades convenience for honesty. *Getting started* is what is cheap to set up; *mature* is what is correct on average; *world-class* is what survives an honest interrogation of how production actually behaves. The blocker to move from one rung to the next is almost never the choice of tool — it is testability, calibrage, or culture for the use case in question.

## How to set up a campaign that actually works

A working performance-testing campaign comes from answering four questions, in this order:

1. **What is the test trying to prove?** Pick the use case from the seven above. State the hypothesis as a sentence — *"if the checkout API is called at 1 000 rps with a 70/30 read/write mix against a 200M-record dataset, p99 latency stays below 80 ms."* If the hypothesis cannot be stated in a sentence, the campaign is not ready; iterate on the hypothesis before going further.

2. **What does the application need to expose for this test to be possible?** Run the testability checklist for the chosen use case (the *Points of attention* above). If the hooks do not exist — no measurement points, no realistic dataset, no dependency-isolation mechanism — the first deliverable of the campaign is the engineering work to add them, not a load test. Most under-prepared programmes skip this step and produce numbers that mean nothing.

3. **What does the campaign realistically cost — set up, run, analyse?** Calibrate the test scope against the budget, not the other way around. A 6-week setup for a one-time stress test that nobody will rerun is a souvenir. A 2-day setup for a regression check that runs on every merge is an asset. The asset compounds; the souvenir decays. Forecast both the setup cost and the steady-state run cost; teams routinely under-estimate the second.

4. **What does the team need to accept for the result to drive a decision?** Identify the human in the room who will say *"we ship"* or *"we don't ship"* based on the test result. If that person does not exist or is not aligned, the test will produce a report and no decision. The cultural pre-requisite for each use case (above) names who that person typically is — and who has to be brought on board before the test is run, not after.

The tool decision — *which load generator, which chaos platform, which database benchmark, which unified platform* — comes after these four are answered. It is rarely the part of the campaign that determines success. The first four are.

## What to take away

If the seven use cases compress into a handful of sentences, they are these:

- **The tool decision comes last.** Hypothesis, testability, *calibrage*, culture — in that order. A team that opens with the tool question has framed itself out of the questions that determine whether the result will mean anything.
- **A campaign is ready when its hypothesis fits in one sentence.** *"At 1 000 rps with a 70/30 read/write mix against a 200M-record dataset, p99 stays below 80 ms."* No sentence, no campaign.
- **The first deliverable is often engineering, not a test.** Missing trace propagation, missing representative dataset, missing injection point — building the hooks is the campaign's first sprint, not a delay to it.
- **Every test is an asset or a souvenir.** The regression check that runs on every merge compounds; the six-week stress-test setup that ran once decays. The existing test portfolio can be audited with that single criterion.
- **There are three reliable ways to produce a green and false result**: gating on the mean (blind to tail regressions), capacity-testing with a closed-loop tool (coordinated omission hides the saturation), and benchmarking a dataset that fits in the buffer pool (the cache answers, not the database).
- **Test slowness, not just failure.** Most production incidents are dependencies getting slow, not dying — and a chaos run that does not measure user-observable latency proves nothing either way.
- **Unified platforms solve use case 1, partially solve 2 and 6, and leave the rest untouched.** Bought after the surrounding work is in motion, a platform is a force multiplier; bought instead of it, it is the year-3 trajectory on a schedule.
- **A test without a decider produces a report, not a decision.** The person who will say *"we ship"* or *"we don't ship"* on the strength of the result must exist — and their absence is detectable, and fixable, before the test runs.

The seven use cases and the tools cited above are catalogued in the [Awesome Performance Engineering](/awesome-performance-engineering/) list maintained alongside this blog. For the production-observation side of the same problem — *understanding how a system behaves* — see the companion piece [*Reading Observability by Intent*](/blog/observability-by-intent/).

## Further reading

The references below are also collected in this site's [library of foundational works](/library/).

{% references() %}

Molyneaux, I. (2014). *The Art of Application Performance Testing* (2nd ed.). O'Reilly. — The most complete treatment of the performance-testing lifecycle, from strategy through execution to post-mortem analysis.

Smith, C. U., & Williams, L. G. (2001). *Performance Solutions.* Addison-Wesley. — The methodological foundation of Software Performance Engineering: model performance characteristics before building, validate against measurements after building.

Jiang, Z. M., & Hassan, A. E. (2015). A survey on load testing of large-scale software systems. *IEEE Transactions on Software Engineering, 41*(11), 1091–1118. — Comprehensive survey covering load design, execution, and analysis methodology.

Fleming, M., et al. (2023). Hunter: Using change point detection to hunt for performance regressions. *Proceedings of the International Conference on Performance Engineering (ICPE).* — Automated regression detection in continuous integration, from DataStax; the reference for use case 1's mature rung.

Kejariwal, A., & Allspaw, J. (2017). *The Art of Capacity Planning* (2nd ed.). O'Reilly. — Pragmatic capacity planning grounded in operational practice. The reference for use case 6.

Tene, G. *How NOT to Measure Latency* [Conference talk]. [YouTube](https://www.youtube.com/watch?v=lJ8ydIuPFeU). — The definitive talk on coordinated omission and tail latency, foundational to use case 6.

Grafana k6 Documentation. *Open and closed models.* [grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/). — Practical reference for choosing an executor that matches the use case.

{% end %}
