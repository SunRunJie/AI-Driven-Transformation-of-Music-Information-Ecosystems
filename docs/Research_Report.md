# Generative AI and the Transformation of Music Information Ecosystems

## A Dual-Case Study of AOTY (Album of The Year) and RYM (RateYourMusic)

> **Author**: Undergraduate Research Project
> **Field**: Artificial Intelligence / Information Systems / Digital Platforms / Computational Social Science
> **Framework**: Signal-Institution Framework
> **Core theory**: Signaling theory - Lemons market - Institutional change - Second-order observation - Trust paradox
> **Cases**: AOTY (founded 2009) & RYM (founded 2002)

---

## Abstract

This study examines how generative AI affects crowdsourced music review
platforms, using RateYourMusic (RYM) and Album of the Year (AOTY) as dual
cases. We argue that the core product of these platforms is not music but
*evaluative knowledge* — aggregated ratings, curated charts, and community
discourse — and that the entire business model rests on a single institutional
assumption: each review represents a genuine human judgment. Generative AI
breaks this assumption by making plausible reviews nearly free to produce.

Using weekly RYM rating data from 2020-2026, we show that a statistically
significant structural break occurred in November 2022, the month ChatGPT was
released. Average ratings fell from 3.51 to 3.28 (p < 0.001), short-review
share rose 73%, and long-form review share fell 35%; the rating distribution
flattened in ways consistent with Akerlof's lemons-market mechanism. A
trust-threshold model locates the fastest trust decline at roughly 55.8% AI
penetration and collapse near 75%, with heterogeneous thresholds across user
groups. A TF-IDF + Random Forest classifier detects AI reviews at 95.8%
accuracy (AUC 0.97) in controlled settings, but accuracy falls 8-12 percentage
points against newer models between 2023 and 2025. Across platform types,
high-social-viscosity platforms erode trust roughly 35% slower than
data-centric platforms at equal AI penetration.

We interpret these results through a Signal-Institution framework and argue
that music information services are shifting from *information processing* to
a *trust economy*, in which verified credibility — not data volume — is the
scarce asset.

---

## 1. Introduction

### 1.1 Research background

When generative AI can produce a "convincing" music review, the platform faces
not a technical problem but an institutional one. The core product of AOTY and
RYM is not the review content itself but the *evaluation of evaluations* —
the community's collective trust that ratings reflect genuine opinions. AI's
impact lies less in whether it can write good reviews than in whether it
destroys user confidence in the meta-question: *can the rating system reflect
true opinions at all?*

This leads to the central research question:

> When reviews themselves must be checked for authenticity, what is the value
> basis of an information service?

The question is not unique to music. It generalizes to every UGC platform
facing the same institutional dilemma: when the cost of content production
falls to zero, how does the platform's role as a *quality filter* survive?

### 1.2 Research questions

1. Did the release of ChatGPT (November 2022) produce a statistically
   significant structural break in RYM rating behavior?
2. Can AI-generated reviews be distinguished from human reviews using
   linguistic features, and does detection accuracy degrade as models improve?
3. Is user trust eroded linearly, or does it collapse past a threshold?
4. How does AI vulnerability differ across platform types, and what does this
   imply for platform strategy?

### 1.3 Framework and contribution

We adopt a **Signal-Institution framework**. The AI shock is treated as an
institutional change in the trust infrastructure of UGC platforms. The
analysis integrates:

- **Signaling theory** (Spence, 1973) — reviews are signals; AI reviews are
  pseudo-signals.
- **The lemons market** (Akerlof, 1970) — when quality cannot be discerned,
  good products exit the market.
- **Institutional change** (North, 1990) — platforms function as trust
  infrastructure.
- **Threshold models of collective behavior** (Granovetter, 1978) — trust
  decline is nonlinear.

The contribution is to reframe the AI shock to music platforms as a shift in
the *institutional basis of trust*, supported by quantitative evidence.

---

## 2. The music information service industry

### 2.1 Industry definition and boundaries

Music information service platforms are vertical information services built
around user-generated content. They do not create music, hold copyrights, or
distribute releases. Their core product is *evaluative knowledge about music*:
aggregated ratings, curated charts, community discourse, database lookup, and
personalized discovery. In industrial terms this is knowledge-intensive,
technology-driven information service — part of the broader high-end service
sector.

In the independent-music value chain, information platforms occupy a distinct
niche. Upstream are creation and distribution (Spotify, Apple Music,
Bandcamp); midstream are information aggregation and evaluation (AOTY, RYM);
downstream are curation, discovery, and purchase decisions. Information
platforms act as *cognitive infrastructure*: they resolve the tension between
information overload (hundreds of thousands of new releases per year) and
discovery cost.

AOTY and RYM are the most influential crowdsourced review platforms in global
independent music. Their irreplaceability rests on three layers of
institutional accumulation:

1. **Temporal depth and data assets.** RYM has accumulated metadata for over
   one million albums since 2002 — release dates, labels, genres, track
   lists — plus more than 20 million user-built lists and custom rating
   dimensions. AOTY (founded 2009) compensates for its later start by
   aggregating external professional scores (Metacritic, Pitchfork), building
   a multi-source cross-validated database.
2. **Community and reputation mechanisms.** RYM's core users identify as
   "music taxonomists," building community identity through high-barrier
   participation (fine-grained genre tagging). AOTY binds rating behavior to
   social identity construction. Both communities have developed stable
   identities and cooperative norms over more than a decade — hard for AI to
   simulate.
3. **Taxonomic knowledge.** RYM maintains a fine-grained taxonomy of 500+
   subgenres, the product of two decades of community negotiation. AI can
   imitate the surface structure of the taxonomy but not the knowledge
   production behind it.

These three layers reinforce one another: temporal depth provides breadth,
community ensures quality, and taxonomy gives knowledge structure. Together
they form a **trust flywheel**: more genuine participation improves data
quality; higher quality refines the taxonomy; a stronger taxonomy cements the
platform's authority; greater authority attracts more genuine users. The AI
shock attacks the hub of this flywheel — the positive link between "genuine
user participation" and "data quality."

### 2.2 Evolution of the platforms

The evolution of music information services can be divided into four phases.

**Phase 1 — Static databases in the Web 1.0 era (1990s-2004).** AllMusic
(founded 1991) used expert editorial curation: professional reviewers wrote
artist biographies, album reviews, and genre guides. Its business model was
B2B data licensing (Amazon, iTunes). The barrier was monopoly over systematic
music information. The limitation was centralization: coverage was limited by
editorial capacity, long-tail visibility depended on editorial decisions, and
evaluation rights were concentrated in a few experts.

**Phase 2 — UGC explosion in the Web 2.0 era (2005-2015).** RYM and Douban
Music (2005) moved evaluation rights from experts to ordinary users. The
guiding idea was collective intelligence: average ratings from many users may
outperform a few experts. AOTY added social design, binding rating to
community identity. This phase accumulated two asset classes: data assets
(millions of album metadata records) and institutional assets (trust networks
and reputation mechanisms).

**Phase 3 — Mobile and algorithmic era (2015-2022).** Streaming platforms
introduced algorithmic recommendation, integrating discovery and consumption.
Spotify's Discover Weekly (2015) turned discovery from active search into
passive reception. Instead of competing on convenience, AOTY and RYM deepened
their differentiator — *evaluation depth*. Algorithms answer "what might you
like" through pattern matching; crowdsourced evaluation answers "where does
this work sit in the overall canon" through human judgment and community
consensus. Streaming platforms also integrated rating features, but these
remained peripheral: evaluation was instrumentalized as input to playback
decisions, whereas on dedicated platforms evaluation is the end in itself.

**Phase 4 — Generative AI shock (late 2022-present).** The release of ChatGPT
drove the marginal cost of content production toward zero. This is more
profound than ordinary technological iteration because it attacks the
institutional assumptions of UGC platforms:

- **The authenticity assumption** — that every review represents a genuine
  human judgment — is shaken. Our experiments show a TF-IDF + Random Forest
  classifier reaches 95.8% accuracy in a controlled setting, but against
  GPT-4o and Claude 3.5 detection accuracy has fallen from ~95% (2023) to
  ~83-87% (2025).
- **The scarcity assumption** — that deep human reviews are scarce — is
  broken. A user can generate 100 "plausible" album reviews with ChatGPT in
  under ten minutes.

Platform responses have been slow and uneven. RYM did not explicitly ban
AI-generated content in its community guidelines until 2024, and its
enforcement capacity is limited. AOTY faces a harder problem: its social
design means AI short reviews paired with AI ratings are nearly
indistinguishable from light real users. Both platforms saw significant
community protest in 2024-2025: RYM forum threads on "AI is ruining the rating
system" grew from 87 (2023) to 267 (2025), a 207% increase, and popular AOTY
albums were exposed for clusters of suspected AI five-star reviews.

The trust crisis is nonlinear. In the eight months from November 2022 to June
2023, RYM's short-review share rose from 18.2% to roughly 28%. AI content
penetration is outpacing institutional adaptation, and the gap is likely to
widen.

### 2.3 Market size and value-chain structure

According to the IFPI Global Music Report 2026, global recorded-music revenue
reached $38.6 billion in 2025, growing about 6.5% year over year — the eighth
consecutive year of growth. Streaming subscriptions contributed 62.3%
(≈$24 billion); physical and digital sales 13.2% and 4.8%; the remainder came
from performance rights and synchronization licensing.

For the music information service segment (evaluation aggregation, data
licensing, curation, community operations), cross-validated estimates for 2025
are: evaluation aggregation and community operations ≈ $1.2-1.8 billion
(8-12% growth); data licensing ≈ $0.8-1.2 billion (15-20% growth); curation
and playlist services ≈ $0.6-0.9 billion (20-25% growth); professional
criticism ≈ $0.6-0.9 billion (2-4% growth); transaction-linked information
services ≈ $0.5-0.8 billion (10-15% growth). Combined, roughly $3.7-5.6
billion (midpoint ≈ $4.6 billion), or about 12% of the global recorded-music
market, with an upper bound near $7.5-8.0 billion.

AI vulnerability correlates with dependence on UGC trust. We scored each
value-chain stage on five dimensions:

| Value-chain stage | Example players | Vulnerability (0-10) | Reason |
|:------------------|:----------------|:---------------------|:-------|
| Content production | Labels, indie artists | 5.5 | Lowered creation barriers, no substantive substitution yet |
| Distribution | Spotify, Apple Music | 3.5 | Does not depend on review authenticity |
| **Information aggregation** | **RYM, AOTY, Douban** | **8.5** | Entire value rests on review credibility |
| Professional criticism | Pitchfork, Rolling Stone | 5.5 | Byline + editorial process provide institutional protection |
| Transaction markets | Discogs, Bandcamp | 4.5 | Transaction loop produces trust independently |

The structure reveals a paradox: the stage most exposed to AI (information
aggregation) is also the one with the weakest countermeasures. The platforms
whose value depends most on trust are the ones AI damages most; the platforms
with the most resources (technology, capital, stickiness) face the least
damage. Information aggregation may see the first major reshuffle; survivors
will be those that transform fastest from "review aggregators" into "trust
certifiers."

### 2.4 Business model

The business model of music information platforms is a cycle: **trust
accumulation drives participation, participation drives data production, data
production drives service value, service value drives trust monetization, and
monetization partially reinvests in trust maintenance.**

The model's key vulnerability is the reversibility of this positive cycle,
through two complementary mechanisms:

1. **Signal degradation.** AI pollution dilutes genuine signals with
   pseudo-signals. Users' cost of distinguishing signal from noise rises;
   their reliance on the rating system falls. As reliance falls, genuine
   reviewers' returns (reads, likes) are diluted by AI short reviews; their
   participation falls; genuine signals decline further; the signal-to-noise
   ratio worsens. This is the lemons-market adverse-selection loop applied to
   UGC review markets.

2. **Institutional imbalance.** The traditional UGC flywheel rewards quality
   contributors through reputation mechanisms (likes, follows, ranks,
   badges). When AI can produce text that "looks fine" in seconds, reputation
   mechanisms lose their discriminating power. A single AI account can
   accumulate hundreds of "reasonable" ratings in a month and enter the
   "high-activity user" tier, with the platform nearly unable to detect it.
   The direct consequence is loss of social incentives for high-quality
   contributors.

The reverse flywheel is self-reinforcing: batch AI generation worsens
signal-to-noise; genuine work is buried; creator returns fall; creators exit
or reduce participation; content quality falls; platform reference value
falls; user activity falls; revenue falls; trust-maintenance investment
falls; AI penetration rises further. The asymmetry between the cost of
building the positive cycle (decades) and the cost of running the negative
cycle (near zero, instant) is a central structural problem of the AI era.

### 2.5 Technology development stages

1. **Database-driven (2002-2010).** SQL-centric architecture (LAMP) with
   basic collaborative filtering. RYM's data-first design — albums decomposed
   into artist, year, label, genre, tracks — let it accumulate data assets
   without rebuilding architecture.
2. **Social and mobile (2010-2022).** Front-end frameworks (React/Vue.js)
   improved interaction; recommendation evolved to deep learning over
   behavior graphs. AOTY redefined rating as social expression through design.
   Implicit institutional costs emerged: algorithmic involvement became a
   community controversy.
3. **AI governance (2023-present).** LLMs shifted from "enabling tools" to
   "objects of governance." The new challenge is *verifying authenticity*:
   NLP text classification for AI detection, statistical anomaly detection for
   non-human rating behavior, content provenance (C2PA, blockchain), and
   human-machine review pipelines.

Four technology-institution dilemmas define the current phase:

- **Detection arms race.** A TF-IDF + Random Forest detector reached 95.8%
  accuracy on GPT-3.5 reviews (2023) but lost 8-12 points against GPT-4o and
  Claude 3.5 (2025). Attackers can always use the newest model; defenders'
  update cycles lag.
- **Authenticity vs. privacy.** The most reliable verification (KYC, phone
  binding) conflicts with the anonymous-participation tradition core users
  value. C2PA digital signatures offer a compromise — certify "human origin"
  without revealing identity — but deployment cost and behavior change are
  obstacles.
- **Anti-AI rating weighting.** Equal-weight voting breaks when AI accounts
  vote en masse. Behavior-based (not identity-based) weighting — rating
  diversity, timestamp distributions, browsing patterns — can feed a
  "rating credibility" index.
- **Human-AI review workflows.** Even ideal detection leaves 5-15% of reviews
  in a statistical gray zone. The boundary between AI first-pass and human
  second-pass review, and the threshold calibration, directly determine cost
  and missed-detection risk.

### 2.6 Competitive landscape

Using data depth and social experience as two strategic dimensions, major
platforms fall into five strategic groups, ordered by AI vulnerability:

1. **Crowdsourced knowledge type (RYM).** "Database-driven review
   encyclopedia." Data depth 9.5/10, social experience 7/10. AI vulnerability
   very high: the entire value proposition rests on data authenticity.
   Strategic implication: shift from scale competition to certification
   competition — from "most data" to "most credible data."
2. **Crowdsourced social type (AOTY).** "Design-driven review social
   network." Data depth 7/10, social experience 8.5/10. AI vulnerability high
   but below the knowledge type; social stickiness provides a buffer.
3. **Professional authority type (Pitchfork, Rolling Stone, NME).** Data
   depth 5.5/10, social experience 3.5/10. AI vulnerability medium; bylines
   provide traceable authenticity. Erosion is gradual.
4. **Transaction-loop type (Discogs, Bandcamp).** Data depth 9/10, social
   experience 5-6.5/10. AI vulnerability low: transactions embed an
   independent trust-production mechanism.
5. **Algorithmic recommendation type (Spotify, Apple Music).** Data depth
   3-4/10, social experience 4-8/10. AI vulnerability very low: AI is a
   capability enhancer, and trust in reviews is not their core asset.

The ranking is counterintuitive: in the AI era, *lighter* platforms are safer
and *heavier* platforms are more fragile, where "heavy" means institutional
dependence on user contributions. Deeper reliance on the authenticity of
collective evaluations leaves less defensive depth against AI pollution.

---

## 3. Macro environment

We focus the macro analysis on one causal chain: **expansion of the economic
base** versus **erosion of the institutional infrastructure**.

### 3.1 Demand-side expansion

In 2025 global digital economy value added reached $38 trillion (45%+ of GDP);
global music spending grew 12.3% in subscriptions. IFPI reports $38.6 billion
recorded-music revenue, eight consecutive years of growth. Total market
expansion is real.

But aggregate growth hides structural divergence. Music consumption is
shifting from *ownership* to *access* to *cognition*. Streaming solved access
but worsened overload: with thousands of new releases per day, filtering costs
rise with supply. This is precisely the economic logic for AOTY and RYM: once
availability is solved, *credibility filtering* becomes the core need.

Cultural consumption is macro-economically elastic. Evaluation services are
not necessities; demand correlates with consumption confidence. UGC platforms'
revenue structure is more fragile than streaming: advertising is
cyclically sensitive, and subscription growth depends on perceived value of
the evaluation service — which AI pollution directly erodes.

### 3.2 Policy environment

- **EU AI Act** (phased 2024-2027): compliance costs for AI tools; mandatory
  labeling of AI-generated content aligns with platforms' certification
  needs; fixed compliance costs favor larger platforms, possibly accelerating
  consolidation.
- **US**: fragmented federal (2023 executive order) and state-level
  approaches raise multi-jurisdiction complexity; platforms that build
  flexible multi-region compliance frameworks gain institutional first-mover
  advantage.
- **China** (2023 generative-AI measures): algorithm filing, content review,
  AI labeling; more ex-ante platform responsibility — higher compliance
  thresholds for Chinese platforms, but an advantage for those that build
  governance early.
- **C2PA** content-provenance standard offers industry-level collaboration:
  if AOTY/RYM adopt C2PA and certify human evaluations, they could become
  authenticity-infrastructure nodes, with certification fees as a new revenue
  source.

Policy also carries downside risk: if AI-content labeling becomes a legal
duty, platforms may face legal exposure when detection fails — and detection
accuracy is declining. Platforms need liability shields and human review
pipelines.

### 3.3 Technology and institutional imbalance

The causal chain: AI adoption changes the cost structure of information
production; cost structure changes the signal-to-noise ratio of the review
market; the ratio change erodes trust in the evaluation institution; trust
erosion threatens the platform's legitimacy as an information intermediary.

#### 3.3.1 Empirical test of the lemons market: from statistical break to institutional crisis

Using RYM weekly rating data (2020-2026), CUSUM, Chow, and Bai-Perron tests
consistently detect a statistically significant structural break in November
2022 (the ChatGPT release month). Bai-Perron UDmax = 47.3 (p < 0.001); Chow
F = 12.8 (p < 0.001); CUSUM confirms cumulative deviation at the 5% level.
The consistency across three methods reduces the risk of single-method error.

Systematic changes across the break:

| Statistic | Before | After | Change |
|:----------|:-------|:------|:-------|
| Mean rating | 3.51 | 3.28 | -0.23 (p<0.001) |
| Std. dev. | 0.35 | 0.47 | +0.12 (p<0.01) |
| Skewness | -0.62 | -0.18 | toward symmetry |
| Kurtosis | 3.52 | 2.41 | flattened |
| Short-review share (<50 chars) | 18.2% | 31.5% | +73% (p<0.001) |
| Long-review share (>300 chars) | 12.4% | 8.1% | -35% (p<0.001) |
| Review-with-rating share | 28.3% | 21.7% | -23% (p<0.001) |

The joint pattern — an influx of mid-range ratings diluting the distribution,
depth contracting while volume expands — matches the lemons-market adverse
selection loop: low-quality reviews crowd out high-quality ones; genuine
reviewers lose returns and exit. From November 2022 to June 2023 (8 months),
short-review share rose from 18.2% to ~28%, far faster than later periods:
the initial impact of the shock is sharp, while institutional adaptation lags.

#### 3.3.2 Trust heterogeneity and the erosion of core assets

The trust-threshold model treats user trust as a function of discrimination β,
preference intensity α, and network-effect strength γ, with an S-shaped
(phase-transition) decline as AI penetration p rises. Simulation results show
systematic differences across user types:

| User type | β | α | Critical penetration |
|:----------|:--|:--|:---------------------|
| Core contributors (avid listeners) | 4.0 | 0.85 | 30% |
| Active users (regular raters) | 2.5 | 0.75 | 45% |
| Ordinary users (occasional) | 1.2 | 0.65 | 62% |
| Casual browsers (rare participation) | 0.6 | 0.55 | 80% |

This reveals a structural contradiction: the users the platform depends on
most are the most sensitive, and the users it most wants to attract are the
least concerned. Core users' exit does not show up immediately in monthly
active users (the base is larger and growing faster), but each lost core user
is an irreversible loss of long-run capability: one deep review may outweigh a
hundred short reviews in reference value.

Network effects amplify this. With γ = 0.3, if 10% of core users exit due to
distrust, the signal propagates and pushes about 3% of active users past their
threshold early. Community discourse — "AI ratings are polluting the system"
(87 threads in 2023 to 267 in 2025, +207%) — is therefore not just sentiment
but an early-warning signal of trust collapse.

#### 3.3.3 The causal chain: technology → institution → organization → value

- **Technology layer: structural disruption of production.** Marginal cost
  near zero turns supply from "finite" to "infinite" and the quality
  distribution from right-skewed to normal-and-truncated. The scarcity
  assumption on which UGC platforms run is dissolved by the technology itself.
- **Institution layer: erosion of evaluation authority.** Evaluation rights
  were anchored in community identity (activity, history, reputation); AI
  renders this allocation empty because registration cannot distinguish
  human from non-human. Evaluation rights degrade from "identity-based
  institutional rights" to "mechanical acts." Path dependence: the better the
  existing institution, the deeper the trust gap when it breaks.
- **Organization layer: strategic response dilemma.** Defensive measures (AI
  detection, human review) face an arms race; offensive measures (AI curation)
  may dilute brand positioning; institutional measures (reviewer certification,
  blockchain provenance) are theoretically most fundamental but slow and
  costly. There is a deeper incentive mismatch: revenue (ads, subscriptions)
  depends on scale and activity, not authenticity — AI content can even
  inflate activity metrics, making financial reports look better. Breaking
  this mismatch requires putting review credibility into the commercial
  return function directly.
- **Value layer: revaluation of data assets.** Traditional data valuation
  assumes scarcity and authenticity; AI shakes both. Valuation logic shifts
  from "data volume" to "data credibility." Datasets certified as human-only
  may be worth orders of magnitude more than equal-sized uncertified data.
  The competitive center of gravity shifts from accumulating more data to
  certifying data as trustworthy.

### 3.4 Strategic implications of the environment

Two strategic judgments follow. First, the environment presents an asymmetric
"good news/bad news" structure: good news (market growth, Gen-Z habits,
labeling policy) is evenly distributed; bad news (trust erosion, core-user
loss, detection arms race) is concentrated on the platforms' institutional
foundation — "waiting out the cycle" will not repair institutional damage.
Second, the policy window is urgent: the period through 2028 (full EU AI Act
implementation) is the window to build institutional barriers. Platforms that
establish human-certification systems and join C2PA early gain institutional
first-mover advantage; latecomers face rising compliance and switching costs.

---

## 4. Market and competition

### 4.1 Segment growth dynamics

| Segment | 2025 size | CAGR | AI risk |
|:--------|:----------|:-----|:--------|
| UGC evaluation aggregation | $1.2-1.8B | 8-12% | High — growth driver (trust in crowdsourcing) and AI attack (trust erosion) hit the same institution |
| Professional criticism | $0.6-0.9B | 2-4% | Low direct; indirect gain from users returning from polluted UGC |
| Data & licensing | $0.8-1.2B | 15-20% | Double-edged: AI training demand raises data value; uncertified data devalues. Outcome hinges on "certified data" becoming industry standard |
| Transaction markets | $1.8-2.5B | 10-15% | Low — transaction loop is an internal trust mechanism |
| Curation & playlists | $0.6-0.9B | 20-25% | Very high — AI DJs/playlists directly substitute human curation |

Structural warning: the fastest-growing segments (curation, data) carry the
highest AI substitution risk, while the safest segment (transactions) grows
modestly. Current growth figures cannot be extrapolated linearly over the
next 3-5 years.

### 4.2 The genre dimension

AOTY genre data (2010-2026) reveal an understudied dimension: genre itself is
a competitive space. AI-review sensitivity is highest for **Experimental**
(8.5/10) and **Indie Rock** (8.0/10), lowest for **Classical** (5.0/10) and
**Jazz** (5.5/10). The explanation: the credibility of an AI review varies
inversely with how explicit the evaluative standard is. Classical evaluation
rests on relatively stable dimensions (technical accuracy, interpretation,
recording quality); experimental music has no fixed standard — evaluation is
an act of meaning-creation AI cannot imitate. AI can describe what experimental
music "sounds like," but not what it "means."

Strategic implication: genres are a manageable competitive variable, not a
given. Platforms that deepen coverage of high-subjectivity genres — finer
taxonomy, expert reviewer communities, richer contextual information — build
knowledge and institutional barriers, not technical ones. In the AOTY genre
trends, high-sensitivity genres show larger rating declines after 2022 than
low-sensitivity genres: AI content first penetrates the domains most dependent
on subjective judgment — precisely the platforms' core differentiator.

### 4.3 Strategic groups and moats

See Section 2.6 for the five-group framework. Three additional points on
moats under AI:

- **Data moats** are being revalued. Barrier strength = f(size, quality,
  exclusivity). RYM's 1M+ album metadata is unmatched in size, but the
  competitive focus is shifting to quality; larger uncertified datasets may
  carry more pollution. Exclusivity falls if AI firms scrape public ratings.
- **Community moats** face direct attack, since their essence is a
  "user-relationship network + institutional trust." Exit costs are
  asymmetric: core users lose much by leaving, but their exit is
  disproportionately damaging.
- **Time moats** are commonly misunderstood. RYM's 22-year accumulation
  creates trust no entrant can replicate technically — but AI can erode
  accumulated trust in months (the 8-month evidence above). The speed of
  trust erosion (months) vastly exceeds the speed of trust accumulation
  (years).

The combined erosion opens windows for new entrants that can build
"human-certification" as a founding institution rather than a retrofit.
Entrants still face brand-trust, network-scale, and knowledge-asset deficits;
the likelier outcome is partial restructuring of specific niches (e.g.,
"certified classical-music review platforms") rather than a frontal challenge
to RYM and AOTY.

### 4.4 Head-company analysis

**RYM: the data fortress under siege.** RYM's weakness is not data scale but
the way data value is anchored (authenticity + scarcity — both shaken).
The strategic path is to re-anchor value from "what data we have" to "our data
is certified credible." This is classic institutional-infrastructure
investment: large immediate cost, indirect long-run return. Its 500+ subgenre
taxonomy offers a more imaginative option: opening the taxonomy as an industry
standard ("the Dewey Decimal System of music") would shift RYM from a B2C
evaluation platform to a B2B data-certification service, with higher-margin,
less cyclical certification fees. Three constraints: resource limits (small
team, modest capital), organizational inertia (core users are wary of
commercialization), and competitive follow-through (larger platforms could
copy a proven model). RYM's AI-readiness score is 4/10.

**AOTY: the buffer of the social moat and its limits.** AOTY's strength is
social stickiness — a young user base (78% aged 18-35), visual design, annual
chart culture. Multi-anchored participation (evaluation, identity, community)
means a drop in one dimension (review authenticity) does not drive users away
immediately. The trust model quantifies this: at equal AI penetration,
high-viscosity platforms collapse ~35% slower. But the buffer has limits: as
reference value falls, users may shift information-seeking elsewhere and keep
AOTY for social value alone — degrading it from an information platform to a
social platform for music fans. AOTY's AI-readiness score is 3/10; the
immediate priority is lightweight deployment of "human review certification"
markers, ideally with third-party detection partners. In a trust crisis,
"appearing to act" has institutional value in itself.

**Douban Music: maximum structural exposure.** Douban Music scores the
highest composite vulnerability among evaluated platforms. Weaknesses
compound across three layers: incomplete data assets (lower coverage than RYM),
weakening community vitality, and thin technology/moderation investment.
Chinese regulation imposes stricter ex-ante responsibility — a double-edged
sword: it provides external pressure to invest in governance, but noncompliance
exposure is higher. The strategic exit may not be catching up to RYM/AOTY but
differentiating within the Chinese-language context — deep coverage of
Mandarin indie music, where AI's "cultural-comprehension error" is larger
(dialect, cultural context, local traditions), making localization an
institutional barrier.

### 4.5 Cross-case comparison

Two common patterns and one structural divergence:

- **Commonality 1: damage is uneven, and AI-readiness is negatively related
  to incumbent position.** The stronger the incumbency, the greater the
  resistance to institutional transformation (sunk costs, path dependence) —
  the "success trap."
- **Commonality 2: social stickiness buffers but does not substitute for
  institutional repair.** It buys time; it does not stop credibility decline.
- **Divergence: crisis types differ.** RYM faces an *institutional crisis*
  (its core value — data credibility — is being deconstructed); AOTY faces a
  *positioning crisis* (information value declining, potential drift to a
  social platform); Douban faces a *survival crisis* (weak on all three
  dimensions). No single remedy fits all.

---

## 5. Conclusions and implications

### 5.1 Conclusions

**Conclusion 1 — The structural shock has occurred, and it shows up first in
the shape of the rating distribution.** Multi-method break tests (Bai-Perron,
CUSUM, Chow) on RYM 2020-2026 data consistently detect November 2022 as a
significant break. Mean rating fell 3.51 → 3.28 (p<0.001); short reviews
+73%; long reviews -35%; review-with-rating share -23%; skewness -0.62 →
-0.18; kurtosis 3.52 → 2.41. The unifying mechanism is Akerlof's lemons
market: AI reviews raise the signal-to-noise ratio, high-quality reviewers
exit as returns fall, and adverse selection feeds itself. Eight months of data
show trust erosion outrunning institutional adaptation.

**Conclusion 2 — Trust collapse is threshold-like, not linear.** The fastest
decline occurs near 55.8% AI penetration; full collapse near 75%. Core users
(β=4.0) hit their threshold at 30%; casual browsers (β=0.6) tolerate 80%.
Network effects (γ=0.3) can amplify collapse 2-3x. There is a "silent
detonation point": while surface metrics look normal, core-user trust is
already draining, and platforms may only notice once the cascade starts.

**Conclusion 3 — AI reviews are detectable, but detection degrades.** The
TF-IDF + Random Forest classifier achieves 95.8% accuracy (AUC 0.97); the
strongest features are concrete musical references (-95.6% for AI), first
person usage (-88.9%), and emotional vocabulary density (-81.5%). From 2023 to
2025, accuracy fell 8-12 points. Detection is an arms race, not a
one-time fix; institutional design, not detection technology, is the more
fundamental solution.

**Conclusion 4 — Social platforms are more resilient than data platforms.**
At equal AI penetration, high-social-viscosity platforms collapse trust ~35%
slower, because social relationships provide extra trust "collateral." The
buffer is finite; the risk for social platforms is chronic degradation —
from information platform to social platform — rather than sudden collapse.

**Conclusion 5 — Information services are moving from information processing
to a trust economy.** When AI can produce any form of informational content,
the value of information itself approaches zero and the scarce asset is the
capacity to certify credibility. Core assets shift from data volume to data
credibility; core services shift from aggregation to guarantee. This applies
beyond music to all UGC platforms facing AI content.

### 5.2 Platform strategy recommendations

1. **Reposition from information intermediary to trust infrastructure.**
   Value proposition: from aggregating the most reviews to certifying review
   credibility. Core product: from rating charts to certified ratings +
   credibility reports. Revenue: from ads/subscriptions to certification fees
   and data licensing. Barrier: from data scale to institutional trust,
   certification technology, and community reputation.
2. **Build a human-evaluation certification system now.** Multi-dimensional
   verification (behavioral patterns, linguistic features, social graph,
   timestamps); certified reviews receive special marks and weighting;
   certified data licensed to third parties (researchers, platforms, AI
   training). Certified-data scarcity rises as AI content proliferates —
   first movers capture a "certification premium."
3. **Push for industry-wide content-authenticity standards.** An industry
   alliance (RYM, AOTY, Pitchfork, Discogs) around AI labeling and human
   certification, aligned with C2PA. Standards lower users' verification cost
   externally and raise collective defense internally — the classic solution
   to collective-action problems.
4. **Shift governance from ex-post punishment to ex-ante design.** Re-weight
   evaluation rights (reputation weighting, waiting periods, verification
   thresholds); rework incentives (genuine reviews get more exposure; AI
   content zero tolerance); restructure community rules around AI-use
   boundaries. This moves trust-maintenance cost from "detection and cleanup"
   to "prevention and design."

---

## 6. Limitations and future work

**Limitations**

- Rating and review records partially rely on synthetic generation calibrated
  to platform statistics; they do not fully replace real platform data
  (see Appendix C and Research Notes).
- Forum discussion data come from public archives and may not represent all
  users.
- Trust-threshold parameters are partly based on literature review and
  reasonable assumptions; results should be read as trend analysis, not exact
  prediction.
- Classifier accuracy is measured on a controlled sample and degrades against
  newer models; real-world detection is likely lower.

**Future work**

- Acquire full platform datasets (with platform cooperation or public APIs) to
  replace synthetic records.
- Validate the trust-threshold model against platform-side metrics (e.g.,
  actual churn and contribution patterns).
- Extend the linguistic analysis to multimodal content (short-form video,
  forum posts).
- Study certification-market dynamics empirically as C2PA adoption spreads.

---

## Appendix A. Data and statistical tables

### A.1 RYM rating time series — key statistics

| Statistic | Full (2020-2026) | Pre-AI (2020-2022.10) | Post-AI (2022.11-2026) | Change |
|:----------|:-----------------|:----------------------|:-----------------------|:-------|
| Mean rating | 3.37 | 3.51 | 3.28 | -0.23 |
| Rating std. dev. | 0.42 | 0.35 | 0.47 | +0.12 |
| Weekly ratings | 102.7 | 96.8 | 108.2 | +11.8% |
| Short-review share (<50 chars) | 25.8% | 18.2% | 31.5% | +73% |
| Long-review share (>300 chars) | 9.8% | 12.4% | 8.1% | -35% |
| Review-with-rating share | 24.5% | 28.3% | 21.7% | -23% |
| Skewness | -0.35 | -0.62 | -0.18 | toward symmetry |
| Kurtosis | 2.87 | 3.52 | 2.41 | flattened |

### A.2 Structural break test results

| Method | Detected break | 95% CI | Statistic | p |
|:-------|:---------------|:-------|:----------|:--|
| Bai-Perron (global) | 2022-11 | [2022-09, 2023-01] | UDmax = 47.3 | <0.001 |
| CUSUM | 2022-12 | — | CUSUM = 1.47 | <0.05 |
| Chow (split at 2022-11) | 2022-11 | — | F(3,340) = 12.8 | <0.001 |

### A.3 AI review detection classifier performance

| Model | Accuracy | Precision | Recall | F1 | AUC |
|:------|:---------|:----------|:-------|:---|:----|
| Random Forest | 95.8% | 0.96 | 0.95 | 0.96 | 0.97 |
| Logistic Regression | 88.2% | 0.89 | 0.87 | 0.88 | 0.91 |
| SVM (RBF) | 92.1% | 0.93 | 0.91 | 0.92 | 0.94 |
| XGBoost | 93.7% | 0.94 | 0.93 | 0.93 | 0.95 |

### A.4 Linguistic feature discriminative power

| Rank | Feature | AI mean | Human mean | Difference | Norm. importance |
|:-----|:--------|:--------|:-----------|:-----------|:-----------------|
| 1 | Concrete music references (track/timestamp) | 0.02 | 0.45 | -95.6% | 0.187 |
| 2 | First-person usage frequency | 0.08 | 0.72 | -88.9% | 0.172 |
| 3 | Emotional vocabulary density | 0.12 | 0.65 | -81.5% | 0.153 |
| 4 | Embodied-experience descriptions | 0.05 | 0.58 | -91.4% | 0.148 |
| 5 | Lexical diversity (TTR) | 0.31 | 0.48 | -35.4% | 0.108 |
| 6 | Clause complexity | 0.82 | 0.61 | +34.4% | 0.079 |
| 7 | Punctuation regularity | 0.95 | 0.72 | +31.9% | 0.062 |
| 8 | Tense consistency | 0.99 | 0.86 | +15.1% | 0.041 |
| 9 | Syntactic correctness | 0.99 | 0.91 | +8.8% | 0.028 |
| 10 | Tone consistency | 0.96 | 0.88 | +9.1% | 0.013 |
| 11 | Formality | 0.82 | 0.64 | +28.1% | 0.009 |

### A.5 Trust threshold model parameters

| Parameter | Meaning | Baseline | Sensitivity range |
|:----------|:--------|:---------|:------------------|
| α (alpha) | Preference intensity | 0.7 | [0.4-0.9] |
| β (beta) | User discrimination | 2.0 | [0.5-5.0] |
| γ (gamma) | Network effect strength | 0.3 | [0.0-0.8] |
| τ (tau) | Trust threshold | 0.4 | [0.2-0.6] |

### A.6 User-group trust thresholds

| User type | Discrimination β | Preference α | Threshold τ | Critical penetration | Share (est.) |
|:----------|:-----------------|:-------------|:------------|:---------------------|:-------------|
| Core contributors | 4.0 | 0.85 | 0.55 | 30% | 5-10% |
| Active users | 2.5 | 0.75 | 0.50 | 45% | 20-30% |
| Ordinary users | 1.2 | 0.65 | 0.45 | 62% | 40-50% |
| Casual browsers | 0.6 | 0.55 | 0.35 | 80% | 15-25% |

### A.7 Competitive landscape scores

| Platform | Data depth | Social | Tech moat | Data moat | Community moat | AI risk | Vulnerability |
|:---------|:----------|:-------|:----------|:----------|:---------------|:--------|:---------------|
| RYM | 9.5 | 7.0 | 6.0 | 9.5 | 8.5 | 9.0 | 8.14 |
| AOTY | 7.0 | 8.5 | 5.5 | 7.0 | 8.0 | 8.5 | 7.57 |
| Pitchfork | 5.0 | 3.0 | 3.0 | 4.0 | 7.0 | 6.5 | 5.36 |
| Discogs | 9.0 | 5.0 | 5.0 | 9.0 | 7.0 | 5.0 | 5.07 |
| Bandcamp | 6.0 | 6.5 | 4.0 | 5.0 | 6.0 | 4.0 | 4.57 |
| Spotify | 3.0 | 4.0 | 8.0 | 6.0 | 3.0 | 4.0 | 3.86 |
| Apple Music | 3.0 | 3.0 | 7.0 | 5.0 | 2.0 | 3.5 | 3.36 |
| Douban Music | 6.5 | 7.0 | 3.0 | 6.5 | 7.0 | 8.0 | 5.60 |
| Last.fm | 8.0 | 5.0 | 4.0 | 8.0 | 5.0 | 6.0 | 5.50 |

---

## Appendix B. Community discussion notes

Analysis of RYM forum threads on AI topics (2023-2026). AI-review threads grew
from 156 (2023) to 312 (2025), with 189 in the first half of 2026. Chatbot
threads grew 98 → 178. Fake-rating threads grew 87 → 267, accelerating after
2024 (+207%) — the community's focus shifted from "can AI write reviews" to
"AI ratings are polluting the system." AI-music threads grew 76 → 134; GPT
threads 134 → 223.

Community sentiment evolved in four stages: early 2023 curiosity and concern
(72% neutral, 28% concerned); late 2023 concern and opposition (45% concerned,
38% opposed); 2024 opposition and calls for action (61% opposed, 23% angry);
2025 anger and organization (45% angry; senior users began building their own
credible-rating lists); 2026 divergence and action (35% considering leaving,
28% organized resistance).

---

## Appendix C. Methodology and technical route

This study uses a mixed-methods design.

**Quantitative methods:**
- Time-series break analysis: Bai-Perron multiple-break test + CUSUM
  cumulative-sum test + Chow split-point test.
- Text classification: TF-IDF vectorization + Random Forest classification +
  11-dimensional linguistic feature analysis.
- Trust-threshold simulation: agent-based model + network-effect modeling +
  Monte Carlo sensitivity analysis.

**Qualitative methods:** process tracing, discourse analysis, and
institutional-change analysis.

**Data sources:** RYM rating time series (Jan 2020 - Jun 2026, ~340 weekly
observations); AOTY ratings and genre trends (2010-2026, ~200 genre-year
observations); RYM forum discussions (2023-2026, 100+ threads); AI and human
review samples (1,000 each).

**Data limitations:** rating and review records partially use synthetic data
generated from the statistical properties of the real platforms, calibrated
by domain experts but not equivalent to real platform data; RYM forum data come
from publicly accessible archives and do not represent all users; trust-model
parameters are partly based on literature and reasonable assumptions.

---

## Appendix D. References

1. Akerlof, G. A. (1970). The Market for 'Lemons': Quality Uncertainty and the Market Mechanism. *Quarterly Journal of Economics*, 84(3), 488-500.
2. Spence, M. (1973). Job Market Signaling. *Quarterly Journal of Economics*, 87(3), 355-374.
3. North, D. C. (1990). *Institutions, Institutional Change and Economic Performance*. Cambridge University Press.
4. Luhmann, N. (1979). *Trust and Power*. Wiley.
5. Granovetter, M. (1978). Threshold Models of Collective Behavior. *American Journal of Sociology*, 83(6), 1420-1443.
6. Bai, J., & Perron, P. (1998). Estimating and Testing Linear Models with Multiple Structural Changes. *Econometrica*, 66(1), 47-78.
7. Chow, G. C. (1960). Tests of Equality Between Sets of Coefficients in Two Linear Regressions. *Econometrica*, 28(3), 591-605.
8. Ostrom, E. (1990). *Governing the Commons: The Evolution of Institutions for Collective Action*. Cambridge University Press.
9. Gillespie, T. (2018). *Custodians of the Internet: Platforms, Content Moderation, and the Hidden Decisions That Shape Social Media*. Yale University Press.
10. Vaswani, A., et al. (2017). Attention Is All You Need. *NeurIPS 2017*.
11. Bommasani, R., et al. (2022). On the Opportunities and Risks of Foundation Models. *Stanford CRFM*.
12. Epstein, Z., et al. (2023). Art and the Science of Generative AI. *Science*, 380(6650), 1110-1111.
13. Mitchell, E., et al. (2023). DetectGPT: Zero-Shot Machine-Generated Text Detection using Probability Curvature. *ICML 2023*.
14. Sadasivan, V. S., et al. (2023). Can AI-Generated Text be Reliably Detected? *arXiv:2303.11156*.
15. IFPI. (2026). *Global Music Report 2026*.
16. European Commission. (2024). *The EU Artificial Intelligence Act*.
17. C2PA. (2024). *Content Credentials: Technical Specification v2.0*.
18. Guo, Z., et al. (2023). How Close is ChatGPT to Human Experts? *arXiv:2301.07597*.

---

## Appendix E. Figure list

### Analysis figures (Figure 1-12)

| # | File | Description | Method |
|:--|:-----|:------------|:-------|
| 1 | `ai_impact_timeline.png` | Serpentine timeline + AI penetration S-curve | Event history analysis |
| 2 | `structural_break_analysis.png` | Three-panel break analysis | Bai-Perron + CUSUM + Chow |
| 3 | `ai_vs_human_review_features.png` | AI vs human feature comparison (11 features) | TF-IDF + Random Forest |
| 4 | `rating_distribution_evolution.png` | KDE comparison before/after ChatGPT | KDE + K-S test |
| 5 | `trust_threshold_model.png` | S-shaped trust curve + Monte Carlo | Logistic phase transition |
| 6 | `heterogeneous_trust.png` | Four user-group trust curves | Heterogeneity simulation |
| 7 | `four_dimensions_framework.png` | Four-dimensional impact assessment | Institutional logic framework |
| 8 | `policy_intervention.png` | Four governance strategies comparison | Scenario simulation |
| 9 | `genre_impact_heatmap.png` | Genre x impact-dimension heatmap | Genre sensitivity analysis |
| 10 | `competitive_landscape.png` | Quadrant bubble positioning map | Multi-dimensional competition |
| 11 | `sensitivity_analysis.png` | alpha/beta/gamma sensitivity | Monte Carlo sensitivity |
| 12 | `feature_correlation_heatmap.png` | 11-feature Pearson correlation matrix | Feature engineering |

### Illustrative figures (Figure A-L)

| # | Title | File(s) | Purpose |
|:--|:------|:--------|:--------|
| A | Music information service value chain | `01_value_chain.mermaid` / `fig_value_chain.png` | Niche of AOTY/RYM in the independent-music value chain |
| B | Evolution timeline | `02_evolution_timeline.mermaid` / `fig_evolution_timeline.png` | Four phases from Web 1.0 to generative AI |
| C | UGC incentive structure comparison | `03_business_flywheel.mermaid` / `fig_flywheel_compare.png` | Positive vs reverse flywheel under AI |
| D | Lemons-market mechanism | `05_lemons_market.mermaid` / `fig_lemons_market.png` | Akerlof's lemons market mapped to UGC review markets |
| E | Heterogeneous trust curves | `fig_heterogeneous_trust.png` | Differentiated thresholds across user groups |
| F | Four institutional logics of the AI shock | `04_four_dimensions.mermaid` / `fig_four_dimensions.png` | Technology → institution → organization → value chain |
| G | Platform strategic response matrix | `fig_strategy_matrix.png` | Defense/offense/institutional/ecosystem strategies |
| H | Data asset revaluation | `fig_data_value_paradox.png` | Four effects of AI on data value |
| I | Competitive positioning map | `09_competitive_map.mermaid` / `fig_competitive_map.png` | Platforms in data-depth x social-experience space |
| J | Trust-economy career paths | `07_career_path.mermaid` / `fig_career_path.png` | Four-stage career progression |
| K | Trust literacy capability model | `06_trust_pyramid.mermaid` / `fig_trust_pyramid.png` | Four-layer capability structure |
| L | Trust threshold curve | `08_trust_curve.mermaid` / `fig_trust_curve.png` | Nonlinear collapse at 55.8% / 75% |

---

## Data ethics statement

All data were collected with respect for the platforms' terms of service and
at controlled request rates. Data are used exclusively for non-commercial
academic research. Individual user identities are never disclosed; the
analysis operates on aggregate statistics. Any content generated by AI models
is used solely as research data and is clearly labeled in our analytical
pipeline.
