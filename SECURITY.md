# Security policy

## Reporting a vulnerability

Please report security issues privately by email to **chris@growthofinfluence.com**, not in a public issue. Include what you found, how to reproduce it and which file, workflow or page is affected. You will get an acknowledgement within five working days.

## Scope

* `tools/`: the validator, formatter, build and link checker.
* `.github/workflows/`: for example a way for a pull request from a fork to gain write access or secrets.
* `site/`: the static page published on GitHub Pages, for example a script injection through a data value.

Data accuracy problems are not security issues: please use the [Correct a company](https://github.com/chris-fountoulis/ai-search-landscape/issues/new?template=correct-company.yml) form.

## How the repository limits risk

* The tools use the Python standard library only; there are no third-party packages to compromise.
* Data files are parsed by a strict loader (`tools/yamlite.py`) that never executes or constructs objects.
* Every workflow starts with a read-only token. Only the Pages deploy job (`pages: write`) and the scheduled link check (`issues: write`) get more, and neither runs on pull requests.
* The site escapes every data value before inserting it into the page and loads no third-party scripts, fonts or trackers.

## Supported versions

Only the latest commit on `main` is supported.
