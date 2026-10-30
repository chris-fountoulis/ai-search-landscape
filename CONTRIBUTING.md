# Contributing

Thank you for helping keep this dataset accurate. Most contributions are one of three things:

| You want to | Do this |
|---|---|
| Add a company | Open an [Add a company](https://github.com/chris-fountoulis/ai-search-landscape/issues/new?template=add-company.yml) issue, or a pull request with a new YAML file |
| Fix a field in an existing row | Open a [Correct a company](https://github.com/chris-fountoulis/ai-search-landscape/issues/new?template=correct-company.yml) issue, or a pull request editing the YAML file |
| Report a shutdown or acquisition | Open a [Company closed or acquired](https://github.com/chris-fountoulis/ai-search-landscape/issues/new?template=company-closed.yml) issue |

Vendors are welcome to open pull requests about their own company. Every change is judged on its public source, never on who sent it, and no company pays to be listed, ranked or described.

## The one rule: a public source for every change

A correction is accepted when a public URL supports it: your own pricing, About, Terms or Imprint page, a press release, an investor's announcement, a bylined article or a regulatory filing. If the fact is not public anywhere yet, the simplest route is to add it to your About page and send us that link. Data aggregators (Crunchbase, PitchBook and similar), private documents, screenshots and emails are not sources.

Corrections are reviewed within five working days.

## Inclusion rubric

A row must pass every test for its dataset. The full rules are in [METHODOLOGY.md](METHODOLOGY.md).

### AI search optimization (`data/ai-search/`)

1. **Real AI search product.** The company sells software or a service whose main purpose includes getting brands found in search, and it markets an AI search feature on its own site: AI visibility tracking, GEO, AEO or AI content for search. Major established SEO or local search platforms that buyers compare against the new entrants also qualify.
2. **Live offer.** The product or service is sold today.
3. **Notability floor.** At least one dated, independent public source names the company (see below).
4. **Out of scope:** general marketing suites where search is a small feature, pure link-building marketplaces, freelancers, and agencies with no public footprint beyond a directory listing.

### AI agents (`data/ai-agents/`)

1. **Real agent product.** The company's own website clearly markets an AI agent product, an agent-building platform, agent infrastructure or agents delivered as a service. An agent plans and takes multi-step actions in other systems with limited human input per step, using a large language model to decide the next step. Chatbots that only answer, rules-based automations and bare model APIs do not qualify.
2. **Available now.** Generally available, a paid beta, or a public waitlist with pricing.
3. **Identifiable.** Name, website and at least one of headquarters, founded year or a named founder.
4. **Big companies:** the agent product is a named product line with its own page, and the row describes that product.
5. **Notability floor.** At least one dated, independent source names the company.
6. **Out of scope:** custom AI agent development shops (consultancies that build agents for one client at a time), pure model labs without a named agent product, open-source projects without a commercial offer, and products that are shut down or not yet available.

### Notability floor (both datasets)

At least one dated source that the company did not write itself: a funding announcement by an investor or in bylined press, a bylined press article, or a regulatory filing. An accelerator or directory page on its own does not count. A company-issued wire release counts only when an investor or bylined press confirms it.

### Headquarters means the legal seat

Use the legal seat stated in the company's own Terms, Imprint or Legal Notice. A state of incorporation alone, a registered agent's address or a shared mail-forwarding address is not a headquarters; in that case use the headquarters the company states on its own site, then a reliable press source.

## Editing a record

Each company is one file, `data/<dataset>/<slug>.yaml`. The schema is [`schema/company.schema.json`](schema/company.schema.json); the allowed segments, countries, statuses and pricing models are in [`schema/vocab/`](schema/vocab/).

```yaml
# AI Search Landscape, by Growth Of Influence. Data licensed CC BY 4.0.
# Schema: schema/company.schema.json. A missing field means not disclosed, never zero.
name: "Acme Search"
slug: "acme-search"
dataset: "ai-search"
company: "Acme Search"
website: "acme.example"
segment: "geo-tracking"
hq:
  city: "Berlin"
  country: "DE"
founded:
  year: 2024
  source: "https://acme.example/about"
status: "active"
funding:
  total_usd: 21000000
  latest_round:
    name: "Series A"
    date: "2025-11"
    amount_usd: 21000000
  source: "https://news.example/acme-raises-21m-series-a"
pricing:
  as_listed_by_vendor: "$95 to $495; Enterprise custom"
  source: "https://acme.example/pricing"
sources:
  - "https://acme.example/about"
  - "https://news.example/acme-raises-21m-series-a"
  - "https://acme.example/pricing"
last_verified: "2026-11-02"
```

Rules the validator enforces:

* Leave a field out when it is not disclosed. Never write `0` for unknown.
* Every number sits in a block with a `source`, and that URL is also listed in `sources`.
* Prices are exactly as listed by the vendor on its own site, before tax. Third-party price listings are not accepted.
* Funding is disclosed equity in US dollars; convert other currencies at the rate stated with the round.
* Set `last_verified` to the date you checked the sources.
* No en dashes or em dashes anywhere. Use commas, colons, periods or hyphens.

Before you open a pull request, run the same checks as CI (Python 3.9 or newer, no packages needed):

```bash
python3 tools/fmt.py                          # put files in canonical form
python3 tools/validate.py                     # schema, vocabularies, sources, dashes
python3 tools/build.py                        # regenerate dist/, STATS.md and the README numbers
python3 -m unittest discover -s tests -t .    # tool tests
```

Commit the regenerated `dist/`, `STATS.md` and `README.md` together with your YAML change. CI fails if they are out of date.

## Changing the tools

The tools in `tools/` use the Python standard library only. Add a test in `tests/` for any behaviour you change, keep Python 3.9 compatibility, and use [Conventional Commits](https://www.conventionalcommits.org/) (`feat(tools): ...`, `fix(data/ai-agents): ...`, `docs: ...`).

## Licensing of contributions

By contributing data you agree that it is published under [CC BY 4.0](LICENSE-DATA) as part of this dataset. Contributions to code are published under the [MIT License](LICENSE).

## Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Questions that are not corrections can go to chris@growthofinfluence.com.
