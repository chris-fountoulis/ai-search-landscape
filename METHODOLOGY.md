<p align="right"><a href="README.md">Back to README</a></p>

# Methodology

How every row in this dataset was chosen, checked and sourced, and how it stays correct. This repository is the open , structured form of two data studies published by Growth Of Influence:

| Dataset | Folder | Study | Edition | Rows |
|---|---|---|---|---|
| AI search optimization companies | `data/ai-search/` | [AI Search Optimization Companies](https://growthofinfluence.com/ai-search-optimization-companies/) | October 2026, checked 26 October 2026 | 151 companies |
| AI agent companies | `data/ai-agents/` | [AI Agent Companies](https://growthofinfluence.com/ai-agent-companies/) | October 2026, checked 29 October 2026 | 437 products from 420 companies |

The rules below are adapted from the methodology sections of the two studies. Where the studies differ , this file says so.

## Contents

- [Principles](#principles)
- [What counts as an AI search optimization company](#what-counts-as-an-ai-search-optimization-company)
- [What counts as an AI agent company](#what-counts-as-an-ai-agent-company)
- [Field rules](#field-rules): [headquarters](#headquarters-hq), [founded year](#founded-year-founded), [funding](#funding-funding), [acquisitions](#acquisitions-acquisition-status), [prices](#prices-pricing), [sources](#sources-sources-source), [last verified](#last-verified-last_verified)
- [How the studies were checked](#how-the-studies-were-checked)
- [Source audit, 2026-10-30](#source-audit-2026-10-30)
- [What this repository does not include](#what-this-repository-does-not-include)
- [Conflicts of interest](#conflicts-of-interest)
- [Known limits](#known-limits)
- [Updates](#updates)

## Principles

> [!IMPORTANT]
> These four rules apply to every row in both datasets. The validator enforces the first two on every pull request.

1. **A blank means "not disclosed or not verified", never zero.** When a figure could not be confirmed in a credible public source, it was left out rather than guessed.
2. **Every number carries a source URL.** Founded year, funding, rounds, valuations, acquisition prices and listed prices each sit in a block with its own `source`. If a figure had no source URL in the study's verified source set, the figure was dropped from this repository and the company kept.
3. **No estimates.** Neither study publishes modelled revenue, headcount or market size estimates as data, and neither does this repository.
4. **No company paid to be included, excluded or described**, and none was told in advance.

## What counts as an AI search optimization company

A company is in `data/ai-search/` if, on the check date, it sold software or a service whose main purpose includes getting brands found in search, and either:

* it markets an AI search feature: AI visibility tracking , generative engine optimization (GEO), answer engine optimization (AEO), or AI content for search; or
* it is a major established SEO or local search platform that buyers compare aginst the new entrants.

Each company appears once, in the segment that best fits what it sells (`schema/vocab/segments.json`). Companies acquired during the period stay in the dataset as their own rows , so the dataset records each deal.

**Left out:** general marketing suites where search is a small feature, pure link-building marketplaces, freelancers, and agencies with no public footprint beyond a directory listing.

## What counts as an AI agent company

**Definition.** An AI agent product is software that, given a goal, plans and takes multi-step actions in other systems with limited human input per step, using a large language model to decide what to do next. Chatbots that only answer questions, rules-based automations and model APIs on their own are out.

**Inclusion.** A row is in `data/ai-agents/` if all five are true on the check date:

1. the company's own website clearly markets an AI agent product, an agent-building platform , agent infrastructure or agents delivered as a service;
2. the offer is available now: generally available, a paid beta, or a public waitlist with pricing;
3. the company is identifiable by name, website and at least one of headquarters, founded year or a named founder;
4. for a big company, the agent product is a named product line with its own page, and the row describes that product;
5. **notability floor:** at least one dated , independent source names the company: a funding announcement by an investor or in bylined press , a bylined press article, or a regulatory filing. An accelerator page alone does not meet this test. A company-issued wire release meets it only when confirmed by the investor or bylined press.

**Left out:** custom AI agent development shops (consultancies that build agents for one client at a time), pure model labs without a named agent product, open-source projects whithout a commercial offer , products that were shut down, sunset or not yet available, and duplicates after an acquisition.

**Segments.** Each row sits in the segment its homepage leads with. The `vertical` segment holds the 25 best funded agent companies in law, finance, health and real estate, each with more than $50 million in disclosed funding or a disclosed round above $50 million.

**Companies and products.** One company can have several product rows (for example a large software company with several agent products). The `company` field groups them, and funding is counted once per company.

> [!NOTE]
> **Model labs.** The frontier model labs (OpenAI, Anthropic , Mistral AI, Cohere and Moonshot AI) carry `model_lab: true`. Their capital would dwarf every other total, so they are reported apart and excluded from every funding sum in `STATS.md`, the README and the site, as in the published study.

**Deferred candidates.** 136 further candidates met the other rules but their independant source could not be checked in time. They are queued for the January 2027 edition and are not in this dataset.

## Field rules

### Headquarters (`hq`)

The legal seat stated in the company's own Terms, Imprint or Legal Notice. A state of incorporation on its own , a registered agent's address or a shared mail-forwarding address is not a headquarters; in those cases the headquarters the company states on its own site is used, then a reliable press source. A virtual office the company presents as its own counts.

The AI agent study used this rule from the start. The AI search study adopted it on 29 October 2026; its rows are being rechecked against it, and corrections land as they are confirmed (see `CHANGELOG.md`). Countries use ISO 3166-1 alpha-2 codes.

### Founded year (`founded`)

The year the company or product first started operating commercially, as stated by the company or a dated press source, not a stock market listing. A year is never inferred from phrases such as "an eight-year-old company". Product lines inside large companies carry no founded year.

### Funding (`funding`)

* Disclosed **equity** funding in US dollars. Debt, grants and revenue-based financing are never added.
* Totals are **minimums**. A total that adds separately disclosed rounds, or that uses a "more than" figure , is a floor.
* **Public companies** and product lines of public companies carry no funding total (`public_company: true`).
* **Acquired startups** keep the equity they disclosed before the deal.
* Where a regulatory filing and press coverage disagree, the filing wins. Example : one company was reported as raising a $12 million Series A while its SEC Form D shows $29.12 million in equity sold; the dataset uses $29.12 million.
* A company's own funding announcement is a valid source for the amount. Data aggregators (Crunchbase, PitchBook and similar) were used only as leads, never as sources.
* **Currency.** Rounds in other currencies use the rate stated with the round. Otherwise the AI search edition used EUR 1.08, GBP 1.27 and CAD 0.73 per US dollar , and the AI agent edition used the European Central Bank reference rates of 28 October 2026: EUR 1.1133, GBP 1.3288, CAD 0.7119.
* `latest_round` holds the round name, and its date and amount where the study published them. `valuation_usd` appears only where the study published a valuation from named press or a filing.
* `bootstrapped: true` is set only when a public source says the company raised no outside funding.

### Acquisitions (`acquisition`, `status`)

* AI agent study: `acquired` only when the deal has **closed**. A signed or announced deal stays `active`. `date_type` is `closed`.
* AI search study: deals are recorded from their **announcement**; `date_type` is `announced`.
* `price_usd` appears only when the price was disclosed or reported by named press, with `price_note` keeping the published qualifier (for example "about" or "reported").

### Prices (`pricing`)

`as_listed_by_vendor` is the monthly list price **as listed by the vendor on its own pricing page**, before tax , in the currency shown, on the `last_verified` date. Annual-only prices are divided by 12. "custom" means no price is published. Some pricing pages show euros to visitors from Europe; where no dollar version was offered , the euro price is kept as listed. `model` (AI agent rows only) is the pricing model from `schema/vocab/pricing-models.json`.

> [!NOTE]
> The AI search study showed a few prices taken from third-party listings, labelled as such. Those are **not** prices listed by the vendor, so this repository drops them (keeping "custom" where the vendor itself shows no price).

### Sources (`sources`, `source`)

Company websites , pricing and legal pages, company announcements, investor pages, regulatory filings (SEC EDGAR for US-listed companies , annual reports and national registries elsewhere) and tier-one or bylined press.

The studies recorded a main source URL for each row plus the further URLs checked during verification. All of them are in `sources`, together with any page added during the source audit below. Each figure points at the page that states it:

| Field | `source` is the page that states |
|---|---|
| `hq.source` | the headquarters city: the legal seat in Terms, Imprint or a privacy notice first, then the company's own About or Contact page, then a filing or press |
| `founded.source` | the founding, launch or incorporation year, in words ("founded in 2022", "Founded: 2022") or a registry entry, never inferred from an age or an article date |
| `funding.source` | the total, when one page states it; otherwise the latest round |
| `funding.latest_round.source` | the latest round, when that is a different page from the total |
| `funding.total_sources` | each round added into a total that no single page states; their amounts sum to `total_usd` |
| `acquisition.source` | the deal (and the price, when one is given) |
| `pricing.source` | the price on the vendor's own pricing page; for "custom", the vendor's pricing or contact-sales page |

> [!TIP]
> If you find a figure whose `source` does not support it, please open a correction: the fix is usually a better URL, which is exactly the kind of pull request this repository is for.

### Last verified (`last_verified`)

The date the row was last checked against its sources. The AI search rows were checked on 26 October 2026 and the AI agent rows on 29 October 2026, except rows changed later by a confirmed correction.

## How the studies were checked

**AI search.** A first pass was built on 26 October 2026. Every funding, acquisition, valuation and revenue figure in every row was then re-verified the same day, largest money first: 47 rows were confirmed as recorded, 59 corrected, 20 had gaps filled and 25 had at least one figure that could not be confirmed and was left blank.

**AI agents.** 810 candidate names came from investor market maps, two years of funding news, accelerator batches, software directories , agent marketplaces and conference lists , with a separate search for Europe and Greece. A first researcher filled each row from the company's own pages and primary sources. A second researcher re-verified every row independently, without seeing the first values, and every disagreement went back to the source. A sample of the largest rows and a random 10% were then rechecked by hand. Of the 437 rows, 58 were confirmed as first recorded, 202 had at least one field corrected, 143 had gaps filled and 34 had at least one money figure that could not be confirmed and was left blank. The news check for new rounds, acquisitions and shutdowns covered July to October 2026; for some of the largest rows it covered TechCrunch and SiliconANGLE only.

## Source audit, 2026-10-30

Before this repository went public, the figure-level `source` links (first assigned by rule from each row's verified set) were audited so that each one points at a page that actually states its figure. Every figure in both datasets was in scope: 2,312 figures in 588 rows (funding totals , latest rounds and valuations, founded years, headquarters, acquisitions and prices).

**How.** Every URL in every row's `sources` was fetched once (about 2,500 pages , one request at a time per site). A script then checked, for each figure, whether a page's text states the value: money amounts in any common notation (and in EUR, GBP or CAD at the study rates), a year next to words such as "founded", "launched" or "incorporated", a city name , an acquirer next to "acquired". On third-party pages the match had to sit near the company's name, so a figure in a sidebar or a related headline does not count. Aggregator profiles (Crunchbase profiles, PitchBook, getlatka, Wikipedia, G2 and similar) never count as a source. Figures the script could not confirm on any listed page (about 280) were researched by hand: the listed pages in a browser or the Wayback Machine, then the company's own pages, investor pages, filings and bylined press. Every hand-checked figure is backed by a verbatim quote, which was matched against the page text by script where the page can be fetched.

**Result (share of figures still in the dataset).**

| Figures | Count | Page text states it (script) | Stated, confirmed by hand | Sum of sourced rounds | Not confirmed |
|---|---:|---:|---:|---:|---:|
| Funding totals, rounds, valuations | 722 | 633 | 42 | 47 | 0 |
| Founded years | 369 | 327 | 42 | | 0 |
| Acquisitions | 57 | 55 | 2 | | 0 |
| Headquarters | 569 (37 with a country only) | 477 | 24 | | 31 |
| Prices | 564 | 286 | 247 (vendor pricing or contact-sales page for "custom") | | 31 |

So every funding, founded-year and acquisition figure was audited and now rests on a page that states it. The 31 headquarters without a `hq.source` are mostly product lines of large public companies (Google , Salesforce , OpenAI, SAP and others) plus seven AI search rows whose only match was an aggregator. The 31 listed prices not confirmed sit on vendor pricing pages that render their prices only in a browser; they keep their vendor `pricing.source` and are queued for a browser check (see the [roadmap](README.md#roadmap)).

**What changed.** 1,057 sources were re-pointed or added, 42 values were corrected and 36 values were removed (the company always stays). Totals that no single page states are now the sum of separately disclosed rounds, listed in `funding.total_sources`. Founded years that were in fact a public launch or stealth-exit year were replaced where the company, an investor , a registry or a filing states the founding year, and removed where no page states any year. Every correction is listed in `CHANGELOG.md`. Because of these corrections , the funding totals in this repository differ slightly from the figures published in the two studies on 26 and 29 October 2026.

## What this repository does not include

The published studies also show yearly revenue figures (filed, company-stated or reported). This repository publishes the fields listed in `schema/company.schema.json` only and leaves revenue out of this first release: each revenue figure needs its own dated source, basis and scope note, which the row-level source set does not yet carry field by field. The studies' internal working columns (verification notes , research batches, contact routes and review flags) are not data and are not published.

## Conflicts of interest

> [!IMPORTANT]
> Growth Of Influence is a digital marketing agency that sells SEO, content and AI systems to its own clients, so it competes with some companies in both datasets. It is not included in either dataset, the same public-source rules were applied to every row, and no company paid to be listed or ranked. Growth Of Influence is a paying customer of some of the software listed, which did not affect how it is described.

## Known limits

> [!WARNING]
> Read these before you quote a total from this dataset.

* Founded year is known for 70 of 151 AI search rows and 299 of 437 AI agent rows.
* The sweep for very recent news was thorough for the companies with the most money and lighter for the smallest ones.
* The datasets cover companies that could be found and verified. They are not a census of every product in either market.

## Updates

Both studies are refreshed quarterly (January, April, July, October) at the same URLs. Between editions , corrections with a public source are reviewed within five working days , applied here as pull requests and listed in `CHANGELOG.md`. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

<p align="center"><a href="README.md">Back to README</a> · <a href="CONTRIBUTING.md">Contributing</a> · <a href="CHANGELOG.md">Changelog</a></p>

<p align="center">Built by <a href="https://chrisfountoulis.com">Chris Fountoulis</a> at <a href="https://growthofinfluence.com/">Growth Of Influence</a>. Read the studies: <a href="https://growthofinfluence.com/ai-search-optimization-companies/">AI Search Optimization Companies</a> · <a href="https://growthofinfluence.com/ai-agent-companies/">AI Agent Companies</a></p>
