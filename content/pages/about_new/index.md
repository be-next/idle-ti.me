+++
path = "about-new"
title = "About me (new draft)"
description = "Jérôme Ramette — performance engineer, generalist, and crisis-recovery practitioner. From the ZX81 to AI, a journey through 25+ years of critical information systems work — across 8 industries and 4 ministries, from junior developer to programme director."

date = 2026-05-02
draft = true

template = "info-page.html"
insert_anchor_links = "left"
toc = true

[extra]
show_reading_time = true
copy_button = false
footnote_backlinks = true
+++

Performance engineer, generalist, and crisis-recovery practitioner. For more than 25 years I have helped organisations rebuild trust in critical information systems — across eight industries and four ministries, in roles running from junior developer to programme director.

An AI thread runs through the whole arc: a DEA in artificial intelligence in 1997, neural networks built and trained when the field was at its least fashionable, one of the first French natural-language interfaces shipped to production in 2001, an introductory AI course taught at university — and, today, engagements where AI components sit inside the systems whose performance and reliability I am asked to secure.

<!-- toc -->

## Numbers that frame the work

A few figures help calibrate what follows. They are not the work itself — they only sketch its surface area.

{% number_grid() %}
{{ number_card(value="25+", label="years in IT", context="first commercial assignment in January 1998") }}
{{ number_card(value="50+", label="engagements", context="across both private and public sectors") }}
{{ number_card(value="8", label="industries", context="rail, defense, telecom, banking, assistance, energy, public sector, hospitality") }}
{{ number_card(value="4", label="French ministries", context="Defense, Education, Treasury / DGME, Ecology — plus DGI and HAS") }}
{{ number_card(value="3,000–13,000", label="users impacted", context="single-engagement scope on the larger crisis missions") }}
{{ number_card(value="7", label="missions in English", context="international teams across France, Italy, Russia, USA") }}
{{ number_card(value="500+", label="load-test campaigns / year", context="current scope at SNCF Voyageurs Transilien Information Voyageur") }}
{{ number_card(value="1997", label="DEA in AI · top of class", context="Université Paris VIII — published at Cellular Automata Workshop '97, Gargnano, Italy") }}
{% end %}

## A career in three movements

### Movement I — Making of a generalist (1998–2003)

The story begins in early 1998 with two short engagements that already announce the breadth: a chip-card secured-access interface in Visual C++ at **Cyberis**, and the requirements specification for the start-up control software of the Le Havre thermal power plant's first unit at **EDF**. By June 1998, two longer commitments open in parallel: at **AREVA / COGEMA**, designing and tuning the Oracle 7 information system that supports a nuclear-fuel reprocessing facility (project SYDDEX); and at **Dassault Aviation**, taking over the maintenance of CECILIA — a safety-of-function workshop developed in LeLisp, then ported to Java 1.2.

The dot-com era follows. In June 2000, I co-build **BizzGo** — joining the founding team as CTO to design and ship a mobile-services integration platform, recruiting and managing a small team of engineers, and deploying for the Manx Telecom 3G pilot and a Jersey Telecom service offer. In parallel, from late 2001, leading the project at **Dejima** that builds one of the first French natural-language SMS interfaces — querying CityVox, PagesJaunes and Orange's geolocation platform with sentences like *"find me a good Italian nearby"*. Behind that project sits the academic grounding: a **DEA in artificial intelligence** (Université Paris VIII, 1997, top of class), neural networks designed and trained by hand, and a publication at the Cellular Automata Workshop '97 in Gargnano. The second AI winter is at its quietest point; today's LLM landscape would have looked like science fiction.

This early period teaches two things that have stayed. First: the layers of the stack are not separable. A latency anomaly in 2024 has the same anatomy as an Oracle 7 join in 1999; the tools change, the physics does not. Second: building a system end-to-end — from chip driver to user interface, from database tuning to product positioning — leaves you with a default reflex of looking *across* boundaries rather than within them. Every later role has been a variation on that reflex.

### Movement II — Performance as a discipline (2003–2016)

The transition is abrupt: from start-up CTO to crisis-time consultant on telecom platforms at industrial scale. **SFR's S3P platform** first — three successive engagements between 2003 and 2007, including the *avalanche* operation that prevents the system from collapsing under Christmas-peak traffic — then **PRM 1.2**, with Accenture and AMDOCS as integrators. **France Telecom's Siegfried** order-management front office. Then a widening of scope through engagements led from **Cité Conseil** and, in parallel from 2009, from **Trexia Consulting**: the *Schéma Directeur Informatique 2010-2012* at **PagesJaunes** (presented to the COMEX), the multi-country deployment of **Europ Assistance's NSV2** contract platform piloted from Italy, and data-quality work for the **Alstom / General Electric** merger.

By 2011 the centre of gravity has shifted from technical performance to organisational transformation. At the **French Ministry of Ecology**, I manage a team of twenty consultants on the SI RH transformation toward the *Opérateur National de Paye* — eighty-three RH procedures reviewed, full convergence-and-validation cycle with the deputy HR director. At **Bouygues Telecom**, three engagements in succession: management and organisation rescue of a fifty-person technical service; the AMOA design of a virtual call-centre handling **3 million calls per month** across 2 000 internal staff and seven outsourcers; then the deployment of a Genesys-Salesforce CRM coupling on **12 sites and 4 000 positions in six months**.

This decade teaches the discipline that names this site: *performance engineering as a practice that combines technical, operational, and organisational change in step*. None of the three is sufficient on its own. A migration that holds load but breaks operations fails. A reorganisation that the technology cannot support fails. A product change that the team did not understand fails. The work is to make the three move together, even when the time pressure says otherwise.

### Movement III — Reliability as a craft (2016–today)

In 2016, I join **QOSGUARD** as a *Directeur de mission*. The work converges on a narrower object: the resilience and performance of critical information systems under operational pressure. The first crisis taskforce is at the **Ministry of Defense** — the GMOA system used by 3 000 users across 54 sites is failing under daily load — followed almost immediately by **SNCF Réseau's SPOT** / IBM Maximo system, the maintenance-management tool for 13 000 rail workers, in active rejection by its users. Both engagements require the same combination: hands-on technical instrumentation, a remediation plan that the existing teams can own, and re-anchoring of the operations and change-management processes around the system.

From 2017 onward, three streams continue in parallel. *Trajectory securing* for large public-sector transformations — the **Cyclades** exam-management programme at the **Ministry of Education**, the FD@Ligne to CHORUS DT migration at the **Armed Forces (SMODI)**. *Performance and resilience advisory* at the **SNCF group** — the *Plan Marshall de la performance* at SNCF Réseau, then the **PulsIV / First** passenger-information overhaul at SNCF Voyageurs (April 2017 – June 2019), then since June 2019 leading the performance-testing team for the **Transilien Information Voyageur** system: 50 applications, ~80 application versions per year, **500+ load-test campaigns annually**. Third stream: standalone advisory engagements that recur — **Sodexo Prestige Venues & Events** (IT rationalisation), **Fortuneo** (ITSM maturity for the Director of Processes and Costs), **SNCF Direction du Matériel** (Industry-4.0 troubleshooting on the Reflex logistics platform from Hardis).

The work I publish on idle-ti.me — the [tools list](/awesome-performance-engineering/) and the [library](/library/) — is the public form of this practice. From 2022 to 2024, I also taught at **CY Cergy Paris Université** — an introduction to artificial intelligence at bachelor level, plus blockchain and IT governance. The word *craft* in "reliability as a craft" is deliberate: at this stage of a career, technical depth is necessary but not sufficient — the difference is increasingly in the judgment.

## What I bring to the table

{% capability_grid() %}
{% capability_card(title="Performance & observability practice") %}
Hands-on with k6, JMeter, Gatling, Grafana, OpenTelemetry, and the wider observability stack. Load-test design grounded in production traffic patterns; workload modelling that survives contact with reality; continuous regression detection embedded in CI/CD pipelines rather than left as a release-time gate. The [tools list](/awesome-performance-engineering/) and [library](/library/) on this site are the public form of that practice.
{% end %}
{% capability_card(title="Crisis recovery on critical systems") %}
Diagnosing degraded systems with users in active rejection; standing up cross-functional crisis taskforces that the existing teams can own; designing remediation plans that align technical fixes with operations and change management. Public examples include SNCF Réseau's SPOT (13 000 users), the Ministry of Defense's GMOA (3 000 users / 54 sites), and the SNCF Voyageurs PulsIV / First passenger-information overhaul.
{% end %}
{% capability_card(title="Cross-functional IT leadership") %}
Twenty-five years of moving across the full stack of an IT organisation: development, database administration, architecture, urbanisation, MOE, MOA, AMOA, change management, programme governance, vendor management, and strategic IT planning. Comfortable on both sides of the table — the CIO's, and the team's. Equally comfortable in French and in English (seven engagements conducted entirely in English).
{% end %}
{% capability_card(title="AI — from the winter to the boom") %}
A DEA in artificial intelligence (Université Paris VIII, 1997, top of class), neural networks designed and trained during the second AI winter, and one of the first French natural-language interfaces shipped to production (Dejima, 2001 — in service at France Telecom for several years). More recently: an introductory AI course taught at bachelor level (CY Cergy Paris Université), and engagements where AI components sit inside the system under test. Performance engineering and AI now meet in the same place — making model-embedding systems observable, testable, and reliable.
{% end %}
{% end %}

## Sectors and craft

Nine emblematic milestones across the three movements — colour-coded by phase. The full chronology is much denser; what follows captures the turning points.

{% timeline() %}
{{ timeline_item(year="1998", phase="foundations", title="First missions", desc="Cyberis · EDF · AREVA · Dassault") }}
{{ timeline_item(year="2000", phase="foundations", title="BizzGo (CTO)", desc="Co-founded mobile-services start-up") }}
{{ timeline_item(year="2001", phase="foundations", title="Dejima — AI / NLP", desc="French natural-language SMS interface") }}
{{ timeline_item(year="2003", phase="performance", title="SFR S3P", desc="Performance under telecom-scale load") }}
{{ timeline_item(year="2011", phase="performance", title="MEDDE SI RH", desc="Managing 20 consultants") }}
{{ timeline_item(year="2013", phase="performance", title="Bouygues virtual call-centre", desc="3M calls/month, 2,000 staff") }}
{{ timeline_item(year="2016", phase="reliability", title="QOSGUARD + first crises", desc="Defense GMOA · SNCF SPOT (13K users)") }}
{{ timeline_item(year="2019", phase="reliability", title="SNCF Transilien", desc="Performance team lead after the PulsIV / First overhaul — 500+ tests/year") }}
{{ timeline_item(year="2022", phase="reliability", title="Teaching & advisory", desc="CY Cergy (AI · Blockchain · Governance) · Fortuneo · SNCF Matériel") }}
{% end %}

### Industries

| Sector | Key clients |
|--------|-------------|
| Rail | SNCF Voyageurs · SNCF Réseau · SNCF Matériel · Alstom |
| Defense | Ministry of Defense (SGA/SID, SMODI) |
| Telecom | SFR · France Télécom · Bouygues Telecom · NetCracker |
| Banking | Fortuneo |
| Assistance | Europ Assistance · NISSAN |
| Energy & nuclear | AREVA / COGEMA · EDF |
| Aerospace | Dassault Aviation |
| Public sector | Ministry of Education · Ministry of Finance / DGME · DGI · Haute Autorité de Santé · Ministry of Ecology |
| Hospitality | Sodexo Prestige Venues & Events |

### Notable training

- **Green Belt Lean Six Sigma**, ASAPpro (2012)
- **Management & negotiation in complex situations**, Simon Barbechat Conseil (2009)

## A few firsts

Career chronologies hide the texture. A few firsts restore it:

- **First computer** — a [Sinclair ZX81](https://en.wikipedia.org/wiki/ZX81), in the early 1980s: the Cold War on the news, [*WarGames*](https://www.youtube.com/watch?v=TQUsLAAZuhU) at the cinema, and talking to a machine as remote a fantasy as flying cars. Today I hold conversations with AI systems that would make WOPR look like a pocket calculator.
- **First Linux** — Yggdrasil Plug-and-Play Linux, Fall 1994, one of the first distributions shipped on CD-ROM when the alternative was fifteen floppy disks. Two months of kernel compiles and hand-calculated X11 modelines to get a stable desktop — a better systems education than most courses.
- **First Internet connection** — 1994, a US Robotics Sportster modem and a trick worth a student's pride: dial the university's [RENATER](https://en.wikipedia.org/wiki/Renater)-connected server for a single telephone unit and have it call back. Unlimited time online; what a luxury.
- **First job, first failure** — January 1998, a start-up selling public web access by prepaid phone card, over two ISDN lines that cost an arm and a leg. We imagined everyone would surf this way; the company was bankrupt within months. The lesson about business models outlived the business.

Away from keyboards: long-distance trail running (30 to 40 km outings with around 2 000 m of cumulative elevation gain), occasional glider piloting, tenor saxophone and modular-synthesis tinkering, and a steady diet of Stephen Jay Gould and Richard Dawkins.

Three decades of computing have not dulled the appetite that started with the ZX81 and the *WarGames* poster on the wall.

## Get in touch

I'm based near Paris and work remotely with teams across Europe. Currently open to engagements around performance engineering, observability platforms, and the assurance of large IT transformations. Best ways to reach me: [email](mailto:jerome.ramette@gmail.com) or [LinkedIn](https://www.linkedin.com/in/jramette/).
