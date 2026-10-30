## What this changes

<!-- One line per company or tool change. For data, name the YAML files. -->

## Type

- [ ] Add a company
- [ ] Correct a company
- [ ] Status change (closed, acquired, renamed)
- [ ] Tools, schema, site or docs

## Source checklist (data changes)

- [ ] Every new or changed number has a `source` URL, and that URL is also in `sources`.
- [ ] Every source is public and dated where possible: the company's own pricing, About, Terms or Imprint page, an announcement, an investor page, a bylined article or a filing.
- [ ] No source is a data aggregator (Crunchbase, PitchBook and similar), a screenshot or a private document.
- [ ] HQ is the legal seat from the company's Terms, Imprint or Legal Notice (not a registered agent or mail-forwarding address).
- [ ] Prices are exactly as listed by the vendor on its own site, before tax.
- [ ] Unknown fields are left out, never set to 0.
- [ ] `last_verified` is the date I checked the sources.
- [ ] I work at or for a company changed here: yes / no

## Checks

- [ ] `python3 tools/fmt.py` and `python3 tools/validate.py` pass
- [ ] `python3 tools/build.py` was run and `dist/`, `STATS.md` and `README.md` are committed
- [ ] `python3 -m unittest discover -s tests -t .` passes (tool changes)

By opening this pull request I agree that data contributions are published under CC BY 4.0 and code under the MIT License.
