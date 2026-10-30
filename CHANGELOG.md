# Changelog

All notable changes to the data and the tools. Data editions follow the published studies; tool versions follow [Semantic Versioning](https://semver.org/). Dates are in UTC.

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

[0.1.0]: https://github.com/chris-fountoulis/ai-search-landscape/releases/tag/v0.1.0
