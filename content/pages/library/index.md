+++
path = "library"
title = "A Performance Engineer's Library"
description = "An annotated bibliography of books, talks, blogs, podcasts, and academic resources for the practising performance engineer — covering systems performance, observability, capacity planning, and software performance engineering. The textual companion to the Awesome Performance Engineering tool list."

date = 2026-05-01

template = "info-page.html"
insert_anchor_links = "left"

[taxonomies]
tags = ["performance engineering", "observability", "performance testing", "bibliography", "books"]

[extra]
show_reading_time = false
copy_button = true
footnote_backlinks = true
+++

Performance engineering draws from several intellectual traditions that have, until recently, evolved largely in parallel: queueing theory and operations research; systems-level performance analysis rooted in operating-systems internals; site reliability engineering from the post-Borg era; and the observability literature that emerged with cloud-native architectures. The corpus is therefore both broader and more fragmented than newcomers typically expect.

This page collects the works that, in the curator's judgement, form a coherent foundation for the discipline — and the resources practitioners reach for when that foundation has to be applied in production. It is intended as a permanent reference, revised periodically rather than chronologically, and is the textual companion to [**Awesome Performance Engineering**](/awesome-performance-engineering/), which catalogues *tools* rather than *ideas*.

## Selection criteria

Each entry has been retained on at least two of the following grounds:

- **Conceptual durability.** The work introduces or formalises a concept — Universal Scalability Law, the USE method, observability as a property of systems — whose value is independent of any particular tool generation.
- **Methodological clarity.** The work presents a measurement or analysis technique that practitioners can apply directly, such as flame graphs, coordinated-omission-aware load testing, or change-point detection for performance regressions.
- **Empirical grounding.** The work draws on production-scale operation rather than abstract or purely academic argument.

Resources are grouped by *domain* rather than by *medium*, because in practice a practitioner's question tends to be domain-shaped ("how do I plan capacity?") rather than format-shaped ("what should I read?"). Where a single work spans multiple domains, it is placed where its primary contribution lies.

Bibliographic entries follow APA-style conventions and are rendered with hanging indents; an annotation follows the citation, separated by an em dash.

## Foundations

### Measurement, methodology, and statistical reasoning

{% references() %}

Jain, R. (1991). *The Art of Computer Systems Performance Analysis.* Wiley. — The foundational textbook on measurement, experimental design, simulation, and queueing models. Predates most of the modern toolchain, but its treatment of confidence intervals, factorial experimental design, and workload characterisation remains directly applicable.

Sites, R. L. (2021). *Understanding Software Dynamics.* Addison-Wesley. — A modern complement to Jain, focused on the gap between aggregate metrics and individual-event behaviour. Introduces KUtrace and argues, persuasively, that timeline-oriented profiling exposes phenomena that statistical summaries hide.

Wescott, B. *Every Computer Performance Book.* — Practical, vendor-neutral methodology with a bias toward simple models and parsimonious measurement.

{% end %}

### Systems performance

{% references() %}

Gregg, B. (2020). *Systems Performance* (2nd ed.). Addison-Wesley. — The single most comprehensive reference on Linux performance methodology. Establishes the USE method (utilisation, saturation, errors) as a discipline for resource analysis.

Gregg, B. (2019). *BPF Performance Tools.* Addison-Wesley. — The definitive reference on eBPF-based observability and dynamic tracing for production systems.

{% end %}

### Capacity planning and scalability theory

{% references() %}

Gunther, N. J. (2007). *Guerrilla Capacity Planning.* Springer. — Introduces the Universal Scalability Law (USL), which subsumes Amdahl's Law by adding a coherency-overhead term. The USL is the most useful single equation a performance engineer can keep in mind, and Gunther's treatment is its canonical exposition.

Kejariwal, A., & Allspaw, J. (2017). *The Art of Capacity Planning* (2nd ed.). O'Reilly. — Pragmatic capacity planning grounded in operational practice at Etsy, Flickr, and others.

{% end %}

### Software performance engineering

{% references() %}

Smith, C. U., & Williams, L. G. (2001). *Performance Solutions.* Addison-Wesley. — The methodological foundation of Software Performance Engineering (SPE): model performance characteristics before building, validate against measurements after building.

Molyneaux, I. (2014). *The Art of Application Performance Testing* (2nd ed.). O'Reilly. — The most complete treatment of the performance-testing lifecycle, from strategy through execution to post-mortem analysis.

{% end %}

### Distributed systems and architecture

{% references() %}

Kleppmann, M. (2017). *Designing Data-Intensive Applications.* O'Reilly. — The standard architectural reference for distributed systems and data pipelines. Indispensable for reasoning about latency, consistency, and throughput trade-offs in modern stacks.

Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (Eds.). (2016). *Site Reliability Engineering.* O'Reilly. [Free online](https://sre.google/sre-book/table-of-contents/). — The book that established SRE as a discipline. Essential for the language of SLOs, error budgets, and operational engineering.

Campbell, L., & Majors, C. (2017). *Database Reliability Engineering.* O'Reilly. — SRE principles applied to database operations and performance.

{% end %}

### Observability

{% references() %}

Majors, C., Fong-Jones, L., & Miranda, G. (2022). *Observability Engineering.* O'Reilly. — The contemporary canonical text on observability as a *property of systems* rather than a category of tools. Argues for high-cardinality, high-dimensionality event data over aggregated metrics.

Sridharan, C. (2018). *Distributed Systems Observability.* O'Reilly. [Free online](https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/). — The earlier and shorter introduction; valuable for its treatment of the three telemetry pillars and their failure modes.

Boten, A. (2022). *Cloud Native Observability with OpenTelemetry.* Packt. — The most current introduction to OpenTelemetry as the converging instrumentation standard.

Julian, M. (2017). *Practical Monitoring.* O'Reilly. — Vendor-neutral monitoring principles, anti-patterns, and on-call design.

{% end %}

### Domain-specific performance

#### JVM and Java

{% references() %}

Oaks, S. (2020). *Java Performance* (2nd ed.). O'Reilly. — Comprehensive JVM tuning reference.

Evans, B. J., Gough, J., & Newland, C. (2018). *Optimizing Java.* O'Reilly. — JIT, bytecode, threading, and cloud performance.

Beckwith, M. (2024). *JVM Performance Engineering.* Addison-Wesley. — HotSpot internals, GraalVM, ahead-of-time compilation.

{% end %}

#### Web and frontend

{% references() %}

Grigorik, I. *High Performance Browser Networking.* O'Reilly. [Free online](https://hpbn.co/). — Essential for the network and protocol layer.

Souders, S. (2007). *High Performance Web Sites.* O'Reilly. — Historically important: the rules that defined modern web performance optimisation.

Wagner, J. L. (2017). *Web Performance in Action.* Manning. — HTTP/2, rendering optimisation, and modern build pipelines.

{% end %}

#### Database performance

{% references() %}

Winand, M. *SQL Performance Explained.* [Free online](https://use-the-index-luke.com/). — Vendor-agnostic indexing fundamentals (Oracle, MySQL, PostgreSQL, SQL Server).

Botros, S., & Tinley, J. (2021). *High Performance MySQL* (4th ed.). O'Reilly. — MySQL optimisation at scale.

{% end %}

### Systems thinking

{% references() %}

Meadows, D. H. (2008). *Thinking in Systems: A Primer.* Chelsea Green. — Stocks, flows, feedback loops, and leverage points — the conceptual scaffolding for capacity reasoning at any scale.

Serazzi, G. (2023). *Performance Engineering.* Springer. [Open Access](https://link.springer.com/book/10.1007/978-3-031-36763-2). — Performance evaluation through case studies using Java Modelling Tools (JMT).

{% end %}

## Landmark talks

Conference presentations frequently introduce concepts well before they reach books. The following are referenced repeatedly across the field.

{% references() %}

Tene, G. *How NOT to Measure Latency* [Conference talk]. [YouTube](https://www.youtube.com/watch?v=lJ8ydIuPFeU). — The definitive treatment of coordinated omission and tail-latency measurement. Required viewing for anyone writing or interpreting load tests.

Gregg, B. (2013). *Blazing Performance with Flame Graphs* [Conference talk]. USENIX LISA. [Slides and video](https://www.brendangregg.com/). — The original presentation of flame graphs as a visualisation primitive for stack-sampling profilers.

Gregg, B. (2016). *Give Me 15 Minutes and I'll Change Your View of Linux Tracing* [Conference talk]. USENIX LISA. [Slides and video](https://www.brendangregg.com/). — A concise primer on the modern Linux tracing ecosystem.

Cantrill, B. (2018). *The Hurricane's Butterfly* [Conference talk]. Jane Street. [YouTube](https://www.youtube.com/watch?v=7AO4wz6gI3Q). — Debugging pathologically performing systems — a study in disciplined investigation.

Berger, E. (2019). *Performance Matters* [Conference talk]. Strange Loop. [YouTube](https://www.youtube.com/watch?v=r-TLSBdHe1A). — Causal profiling and the Coz profiler; an unusually rigorous treatment of why traditional profilers can mislead optimisation decisions.

Thompson, M. *Mechanical Sympathy* [Conference talk]. [InfoQ](https://www.infoq.com/presentations/mechanical-sympathy/). — The case for understanding hardware in order to write effective high-performance software.

{% end %}

## Standards and methodologies

- [**USE method**](https://www.brendangregg.com/usemethod.html) — utilisation, saturation, errors. A systematic procedure for resource-level performance analysis.
- [**RED method**](https://grafana.com/blog/the-red-method-how-to-instrument-your-services/) — rate, errors, duration. The service-level counterpart to USE.
- [**Universal Scalability Law**](https://arxiv.org/abs/0808.1431). Gunther's two-parameter scalability model that subsumes Amdahl's Law by accounting for coherency cost.
- [**Google SRE — Testing for Reliability**](https://sre.google/sre-book/testing-reliability/). The SRE chapter on testing practices, foundational for modern reliability engineering.
- [**Performance Testing Guidance for Web Applications**](https://learn.microsoft.com/en-us/previous-versions/msp-n-p/bb924375(v=pandp.10)) (Microsoft patterns & practices). Older but methodologically sound.
- [**W3C Web Performance APIs**](https://www.w3.org/webperf/). Navigation Timing, Resource Timing, Long Tasks, and the rest of the standardised browser-side instrumentation surface.

## Benchmark suites and reference workloads

- [**TPC Benchmarks**](https://www.tpc.org/). TPC-C (OLTP), TPC-H and TPC-DS (decision support), TPCx-IoT, and others — the industry-standard family for transactional and analytical database benchmarking.
- [**SPEC Benchmarks**](https://www.spec.org/). SPECjbb (Java application server), SPECweb, SPECpower, and the broader SPEC family.
- [**YCSB — Yahoo! Cloud Serving Benchmark**](https://github.com/brianfrankcooper/YCSB). The most cited benchmark in the NoSQL and cloud-database literature; over 3,500 academic citations.

## Online resources and blogs

### Documentation and learning material

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/) — primary reference for the converging instrumentation standard.
- [k6 Documentation](https://grafana.com/docs/k6/latest/) — particularly clear treatment of load-test design, thresholds, and result interpretation.
- [Gatling Academy](https://academy.gatling.io/) — free training material.
- [Web.dev — Learn Performance](https://web.dev/learn/performance/) — Google's comprehensive course on Core Web Vitals and rendering.

### Practitioner blogs

- [**Brendan Gregg's blog**](https://www.brendangregg.com/) — the central reference for Linux performance, eBPF, and flame graph methodology.
- [**Mechanical Sympathy** (Martin Thompson)](http://mechanical-sympathy.blogspot.com) — low-latency, lock-free systems, and the LMAX Disruptor.
- [**The Observation Deck** (Bryan Cantrill)](https://bcantrill.dtrace.org/) — DTrace, observability, and the cultural history of system debugging.
- [**Honeycomb blog**](https://www.honeycomb.io/blog) — observability engineering, frequently with empirical depth.
- [**Grafana blog**](https://grafana.com/blog/) — technical content on the Grafana observability stack.
- [**Netflix Tech Blog**](https://netflixtechblog.com/) — chaos engineering, adaptive streaming, and large-scale reliability.
- [**High Scalability**](https://highscalability.com/) — long-running compendium of architecture case studies.

### Newsletters, calendars, and aggregators

- [**SRE Weekly**](https://sreweekly.com/) — weekly digest on reliability and observability.
- [**PerfPlanet — Web Performance Calendar**](https://calendar.perfplanet.com/) — twenty-four invited articles every December since 2009; one of the most consistently substantive sources in web performance.
- [**CNCF TAG Observability**](https://github.com/cncf/tag-observability) — community standards and whitepapers.
- [**CNCF TAG App Delivery**](https://github.com/cncf/tag-app-delivery) — cloud-native delivery practices, including performance.

## Podcasts

- [**TestGuild Performance**](https://testguild.com/performance-testing/) — a weekly podcast on performance testing and SRE, running since 2014. Notable for breadth of practitioner interviews.
- [**PerfBytes**](https://www.perfbytes.com/) — performance engineering topics and conference coverage.

## Research and academic venues

The academic performance-engineering literature is concentrated in two communities:

- [**ICPE — International Conference on Performance Engineering**](https://icpe.spec.org/). The annual ACM/SPEC conference deliberately bridges research and industry practice.
- [**ACM SIGMETRICS**](https://www.sigmetrics.org/). The premier academic venue for performance-evaluation research.

A small selection of papers that practitioners frequently cite:

{% references() %}

Smith, C. U., & Williams, L. G. (2000). Software performance antipatterns. *Proceedings of the 2nd International Workshop on Software and Performance (WOSP).* — The foundational catalogue of recurring performance problems and their remedies.

Jiang, Z. M., & Hassan, A. E. (2015). A survey on load testing of large-scale software systems. *IEEE Transactions on Software Engineering, 41*(11), 1091–1118. — Comprehensive survey covering load design, execution, and analysis methodology.

Fleming, M., et al. (2023). Hunter: Using change point detection to hunt for performance regressions. *Proceedings of the International Conference on Performance Engineering (ICPE).* — Automated regression detection in continuous integration; representative of the recent literature on quantitative quality gates.

{% end %}

## Companion: tools

This page is the textual companion to [**Awesome Performance Engineering**](/awesome-performance-engineering/), which catalogues the open-source and commercial tools that operationalise the ideas above. The two are intended to be consulted together: the books and talks here explain *why* a method works; the tools listed there are *how* it gets applied to a running system.

## Selection notes

Inclusion is editorial rather than exhaustive. Resources are added when they introduce or substantially clarify a concept, and removed when they are superseded or no longer accessible. Suggestions and corrections are welcome via the [site repository](https://github.com/be-next/idle-ti.me).
