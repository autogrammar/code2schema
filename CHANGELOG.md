# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.9] - 2026-09-13

### Docs
- Update README.md
- Update project/README.md
- Update project/context.md

### Other
- Update .gitignore
- Update .planfile/.store.lock
- Update .planfile/config.yaml
- Update .planfile/config.yaml.fast.json
- Update .planfile/events/.logs.dsl.date
- Update .planfile/events/.logs.dsl.v1
- Update .planfile/events/history/logs-2026-09-08.dsl.txt
- Update .planfile/events/logs.dsl.txt
- Update .planfile/events/operations.jsonl
- Update .planfile/sprints/current.yaml
- ... and 18 more files

## [0.1.8] - 2026-06-29

### Docs
- Update README.md

## [0.1.7] - 2026-05-07

### Docs
- Update README.md

### Other
- Update uv.lock

## [0.1.6] - 2026-05-07

### Docs
- Update CHANGELOG.md
- Update README.md
- Update project/SUMR.md

### Test
- Update testql-scenarios/cli.testql.yaml
- Update testql-scenarios/generated-cli-tests.testql.toon.yaml

### Other
- Update Taskfile.yml
- Update VERSION
- Update code2schema/__init__.py
- Update code2schema/analyzer/cqrs.py
- Update code2schema/analyzer/events.py
- Update code2schema/analyzer/graph.py
- Update code2schema/cli.py
- Update code2schema/codegen/__init__.py
- Update code2schema/codegen/visualizer.py
- Update code2schema/core/extractor.py
- ... and 5 more files

## [0.1.5] - 2026-05-07

### Refactor
- Split `cli._resolve_paths` (CC=11) into `_validate_root` + `_build_output_paths`; `_resolve_paths` kept as thin orchestrator for test compatibility.
- Split `analyzer.events._find_command_handlers` (CC=9) into `_is_command_candidate` + `_collect_emitted_events` helpers.
- Split `codegen.visualizer._build_graph_data` (CC=9) into `_build_nodes`, `_build_links`, `_group_rules_by_target`, `_build_stats`.

### Test
- Strengthen testql self-analysis assertion from `grep -q modules` to `jq '.modules | length' > 10` to catch extractor regressions.
- Switch testql CLI scenarios to `python3 -m code2schema.cli` so they execute end-to-end against the installed entrypoint.

### Other
- Add `task testql` target running both testql scenario files.
- Add roadmap-aligned summary header in `goal.yaml` (versioning, version_files, publish targets).
- Clean ruff/black baseline across the package (no behavior changes).

## [0.1.4] - 2026-05-07

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update docs/CHANGELOG.md
- Update docs/README.md
- Update docs/examples/api/basic.py
- Update docs/examples/cli/semcod.sh
- Update project/README.md
- Update project/context.md

### Test
- Update testql-scenarios/cli.testql.yaml
- Update tests/test_code2schema.py

### Other
- Update .gitignore
- Update Taskfile.yml
- Update VERSION
- Update app.doql.less
- Update code2schema/__init__.py
- Update code2schema/analyzer/events.py
- Update code2schema/cli.py
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- ... and 14 more files

## [0.1.2] - 2026-05-04

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update docs/README.md
- Update docs/examples/api/advanced.py
- Update docs/examples/api/basic.py
- Update docs/examples/cli/basic.sh
- Update docs/examples/outputs/report-sample.md
- Update docs/examples/outputs/schema-sample.json
- Update project/README.md
- ... and 1 more files

### Test
- Update testql-scenarios/generated-cli-tests.testql.toon.yaml

### Other
- Update app.doql.less
- Update code2schema/cli.py
- Update project.sh
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- ... and 11 more files

## [0.1.1] - 2026-05-04

### Docs
- Update README.md
- Update report.md

### Test
- Update tests/__init__.py
- Update tests/test_code2schema.py

### Other
- Update .env.example
- Update .idea/.gitignore
- Update .idea/code2schema.iml
- Update .idea/inspectionProfiles/Project_Default.xml
- Update .idea/inspectionProfiles/profiles_settings.xml
- Update .idea/modules.xml
- Update .idea/vcs.xml
- Update code2schema/__init__.py
- Update code2schema/analyzer/__init__.py
- Update code2schema/analyzer/cqrs.py
- ... and 11 more files

