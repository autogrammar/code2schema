# code2schema Documentation

## Structure

```
docs/
├── examples/
│   ├── cli/
│   │   ├── basic.sh          # CLI usage examples
│   │   └── semcod.sh         # Semcod project analysis
│   ├── api/
│   │   ├── basic.py          # Basic Python API
│   │   └── advanced.py       # Advanced Python API
│   └── outputs/
│       ├── schema-sample.json
│       └── report-sample.md
└── README.md                 # This file
```

## Quick Links

- [CLI Examples](examples/cli/basic.sh) - Command-line usage patterns
- [Semcod CLI](examples/cli/semcod.sh) - Analysis for semcod `www/`
- [Python API Basic](examples/api/basic.py) - Basic programmatic usage
- [Python API Advanced](examples/api/advanced.py) - Advanced analysis
- [Sample JSON Output](examples/outputs/schema-sample.json)
- [Sample Markdown Report](examples/outputs/report-sample.md)
- [Documentation Changelog](CHANGELOG.md)

## CLI Usage

See [examples/cli/basic.sh](examples/cli/basic.sh) for common patterns:

```bash
# Basic analysis
code2schema ./backend

# Generate all formats
code2schema ./backend --proto --md --html

# Full analysis with diagnostics
code2schema ./backend --proto --md --html --graph-summary --events --cycles
```

## Python API

See [examples/api/](examples/api/) for programmatic usage:

```python
from code2schema import extract_project, analyze
from code2schema.codegen import to_json, to_proto, to_markdown

modules = extract_project(Path("./backend"))
schema = analyze(modules)

# Export
Path("schema.json").write_text(to_json(schema))
Path("api.proto").write_text(to_proto(schema))
Path("report.md").write_text(to_markdown(schema))
```

## Automatyzacja repozytorium

- [Synchronizacja metadanych](information/org-metadata-sync.md) — koordynator, harmonogram i diagnostyka.
