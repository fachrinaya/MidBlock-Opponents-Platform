# Validation record

The portable package was exercised in a fresh Python 3.11 virtual environment,
installed offline from its included dependency wheels. It does not use the
original app virtual environment or import the original MidBlock application.

- 29 automated checks passed: frozen-data parity, cutoff/source-grain rejection,
  missing-detail exclusions, stored-score preservation, partial contribution
  scope, configurable threats, secret-safe acquisition errors, review binding,
  section IDs/references/charts, prompt preparation and mocked Bedrock transport.
- A complete offline rebuild was recorded through Nutmeg as source project run
  R36 with unchanged declared inputs. Source snapshot, config and code hashes
  remain in its manifest. An earlier packaging run created Python bytecode;
  bytecode writes were disabled for recorded replay after that check.
- The real English Haiku requests were prepared for every section using dry-run.
  No new Bedrock call or live database connection was made for package validation.
- Independent browser review passed at 1440, 768, 390 and 320 pixels: no page
  errors or page-wide overflow; all nine panel switches and three drill toggles
  worked, Geypens remained the default, and the added threats were legible.
- The rebuilt 19-page PDF includes the extra threats, their responses and the
  awareness section. Print exposes every chart panel and proposed drill.
- The packaged source/data/audit text was scanned for locally configured secret
  values and private-key material; none was included. Raw source and generated
  data remain excluded from git.

The included snapshot is a frozen record. Live database reachability, current
fixture completeness, current Bedrock permissions and future model wording are
not established by the offline tests. New drafts need factual coaching review.

`audit/package-checks.json` records the snapshot checksum and packaging checks.
`work/demo/report/browser-checks.json` contains the latest local render checks.
Use `python -m unittest discover -s tests -v` to rerun software checks.

The final Downloads copy was independently installed from the included wheels.
Its own `.venv` passed all 29 tests, rebuilt the evidence/English HTML/PDF, and
prepared the players section request without the original workspace. The local
preview was started directly from that folder on port 4182.
