# Changelog

All notable changes to the data and the tools. Data editions follow the published studies; tool versions follow [Semantic Versioning](https://semver.org/). Dates are in UTC.

## [Unreleased]

### Source audit, 2026-10-30

Every figure in both datasets was checked against the page text of its source, so that each `source` now points at a page that states its figure. Method and coverage are in [METHODOLOGY.md](METHODOLOGY.md#source-audit-2026-10-30). 1,057 sources were re-pointed or added, 42 values were corrected and 36 values were removed; no company was removed.

**Headline numbers changed.** These are corrections found during the source audit, so the totals below now differ from the published studies:

* AI search disclosed equity funding: $2.60B to $2.59B (Jasper $131M to $125M, Synup $6.5M to $6M).
* AI agent disclosed equity funding: $40.19B to $40.28B (about +$90M, from the funding corrections below).
* Founded years known: AI search 72 to 70, AI agents 306 to 299 (founded 2023 or later: 25 to 25, and 143 to 131).
* Rows with an HQ country: AI search 144 to 139, AI agents 431 to 430.

**Funding totals corrected** (all `ai-agents` unless marked):

* Lovable $930M to $952.57M (adds the disclosed pre-seed and pre-Series A rounds)
* Mindgard $11.99M to $41.99M, latest round now the $30M Series A of August 2026
* Rasa $56M to $70.1M; Galileo $50.1M to $68M; Dialpad $415M to $418M; Hebbia $160M to $161M
* Whatagraph $7.87M to $8.81M; QA.tech $4.34M to $5M; Linkup $13.34M to $13.2M (rate stated with the round); TestSprite $8.2M to $8.1M
* Jasper (`ai-search`) $131M to $125M; Synup (`ai-search`) $6.5M to $6M

**Founded years corrected** (the row held a public launch or stealth-exit year; the company, an investor, a registry or a filing states the founding year): Augment Code 2024 to 2022, Warp 2022 to 2020, Vectara 2022 to 2020, Eudia 2025 to 2023, Credal 2023 to 2022, Rogo 2024 to 2022, Ultravox 2023 to 2022, Siena 2023 to 2022, Alex 2024 to 2023, Stytch 2021 to 2020, Avoca 2023 to 2022, Straiker 2025 to 2024, Viktor 2026 to 2023, Paid 2025 to 2024, Anything 2025 to 2021, Similarweb (`ai-search`) 2007 to 2009.

**Founded years removed** (no page states one): Skyfire, Sema4.ai, Supermemory, Goodcall, Sinequa, Rabbit, Letta, Copy.ai (`ai-search`), Nightwatch (`ai-search`).

**Headquarters corrected** under the legal-seat rule (`ai-search`): Otterly.AI Vienna to Persenbeug, Rankscale Konigstetten to Vienna, Typeface San Francisco to Palo Alto, getmint Paris to Ris-Orangis, Thryv Dallas to Grapevine. **Removed** (no acceptable page states them): Arcade, Am I On AI, Byword, iPullRank, Siege Media, Arvow. The placeholder city "Unknown" was removed from six AI search rows.

**Prices.** Every remaining price now has a vendor `pricing.source`; "custom" links the vendor's pricing, contact-sales or demo page. Where the vendor lists a price the row said "custom" or "not public": OptimizeGEO, Serpier, Tely AI, Obsero, Coinbase x402, Genspark, Google Gemini Enterprise and Meta Muse now carry the listed price. Removed: prices with no vendor page (Fetch.ai Agentverse, Mastercard Agent Pay, Murphy, SolveAI, Unusual, Ryze AI, Paid, Yoast) and entries that were not prices ("not verified" or "n/a": Raven Tools, Visiblie, Wincher, Ubersuggest, SpyFu, Hall, XFunnel).

### Schema and tools

* `hq.source`, `funding.latest_round.source` and `funding.total_sources` (the round pages behind a total that no single page states). The validator requires each to be listed in `sources`; the CSV exports gain `hq_source`, `latest_round_source` and `funding_total_sources`.

### Site

* Open Graph and Twitter card meta with a social preview image, and Quicksand self-hosted under `site/fonts/` with its SIL Open Font License.

## [0.1.0] - 2026-10-30

First public release: both October 2026 editions as open, sourced YAML records.

### Data editions

* **AI search optimization companies, October 2026 edition** (`data/ai-search/`): 151 companies, checked on 26 October 2026, from the study published at <https://growthofinfluence.com/ai-search-optimization-companies/> on 26 October 2026.
* **AI agent companies, October 2026 edition** (`data/ai-agents/`): 437 products from 420 companies, checked on 29 October 2026, from the study published at <https://growthofinfluence.com/ai-agent-companies/> on 29 October 2026. Includes the study's own update of 29 October 2026: Salesforce's closed acquisition of Intercom (Fin) on 10 September 2026, price left blank because it was stated only as approximate, and Mechanical Orchard's disclosed funding raised to a floor of $80 million.

### Corrections applied since publication

Confirmed by the company with a public source and checked on 27 October 2026:

* **LLM Pulse** (`ai-search`): HQ Barcelona, Spain (legal notice); founded 2025 and bootstrapped (company About page).
* **ZipTie** (`ai-search`): HQ Austin, United States, the legal seat in its Terms of Service, under the legal-seat HQ rule both studies now use.

Pending corrections without a public source yet (a founding year and a funding total) are not applied.

### Source fixes

* Two acquisition sources now point at the deal announcements: Intercom (Fin) to the Salesforce closing release, GitHub (Copilot coding agent) to Microsoft's completed-acquisition announcement.
* 88 rows priced as "custom" now link the vendor's pricing page as `pricing.source`.

### Differences from the published pages

* **Revenue is not included** in this release (see METHODOLOGY.md).
* **Third-party prices are not included.** The AI search study showed 10 prices from third-party listings or reports, labelled as such. They are not prices listed by the vendor, so this dataset drops them: First Page Sage, Kalungi, Ryze AI, Ten Speed and iPullRank keep "custom" (the vendor shows no price); Peec AI, Geostar, Mangools, Moz, Serpstat and Birdeye have no price.
* **Two prices without a vendor source are not included**: Searchable (`ai-search`) and Amazon Alexa+ (`ai-agents`), whose source sets held no page on the vendor's own site.
* Websites are stored as bare domains (four AI search rows were published with `https://` or `www.`).

### Tools

* `tools/yamlite.py`: strict, dependency-free YAML subset loader and canonical dumper.
* `tools/schemalite.py` and `schema/company.schema.json`: JSON Schema validation of every record.
* `schema/vocab/`: segments, ISO 3166-1 alpha-2 countries, statuses and pricing models.
* `tools/validate.py`: schema, vocabularies, uniqueness, URL format, a listed source for every number, status consistency, dash ban and canonical form.
* `tools/fmt.py`: canonical formatter.
* `tools/build.py`: `dist/` CSV and JSON, `STATS.md`, the README numbers block and the Pages site.
* `tools/check_links.py`: rate-limited, report-only link checker, run weekly by a scheduled workflow.
* `site/`: framework-free browser deployed to GitHub Pages.

[Unreleased]: https://github.com/chris-fountoulis/ai-search-landscape/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/chris-fountoulis/ai-search-landscape/releases/tag/v0.1.0
