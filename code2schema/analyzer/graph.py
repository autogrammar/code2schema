"""
code2schema.analyzer.graph
~~~~~~~~~~~~~~~~~~~~~~~~~~
Zaawansowana analiza grafu wywołań:
  - eksport GraphML (do Gephi / yEd / Neo4j)
  - PageRank centrality (kto jest "centrum" architektury)
  - detekcja hubów i cykli
  - metryki warstw (layered architecture check)
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import networkx as nx

from code2schema.core.models import CQRSRole, SchemaIR


# ── Builder ───────────────────────────────────────────────────────────────────


def build_rich_graph(schema: SchemaIR) -> nx.DiGraph:
    """Buduje pełny graf z atrybutami węzłów (rola, moduł, fan-out)."""
    G = nx.DiGraph()

    func_map: dict[str, str] = {}  # short_name → qualified_name (last wins)
    for mod in schema.modules:
        for f in mod.functions:
            G.add_node(
                f.qualified_name,
                label=f.name,
                role=f.role.value,
                module=mod.name,
                fan_out=f.fan_out,
                lines=f.lines,
                is_async=int(f.is_async),
            )
            func_map[f.name] = f.qualified_name

    for mod in schema.modules:
        for f in mod.functions:
            src = f.qualified_name
            for callee in f.calls:
                dst = func_map.get(callee)
                if dst and dst != src:
                    G.add_edge(src, dst)

    return G


# ── Metrics ───────────────────────────────────────────────────────────────────


def centrality_report(G: nx.DiGraph, top_n: int = 10) -> List[Tuple[str, float]]:
    """PageRank — funkcje najważniejsze architektonicznie.

    Falls back to in-degree ranking when scipy is unavailable
    (networkx pagerank delegates to scipy on some versions).
    """
    if G.number_of_edges() == 0:
        return []
    try:
        pr = nx.pagerank(G, alpha=0.85)
    except ModuleNotFoundError:
        pr = dict(G.in_degree())
        total = sum(pr.values()) or 1
        pr = {node: deg / total for node, deg in pr.items()}
    return sorted(pr.items(), key=lambda x: x[1], reverse=True)[:top_n]


def hub_nodes(G: nx.DiGraph, threshold: int = 5) -> List[str]:
    """Węzły z fan-in >= threshold — potencjalne hub-moduły."""
    return [n for n, d in G.in_degree() if d >= threshold]


def detect_cycles(G: nx.DiGraph) -> List[List[str]]:
    return list(nx.simple_cycles(G))


def layer_violations(schema: SchemaIR) -> List[str]:
    """
    Prosta heurystyka: query nie powinno wołać command.
    Zwraca listę naruszeń.
    """
    func_roles: dict[str, CQRSRole] = {}
    for mod in schema.modules:
        for f in mod.functions:
            func_roles[f.name] = f.role

    violations: list[str] = []
    for mod in schema.modules:
        for f in mod.functions:
            if f.role == CQRSRole.QUERY:
                for callee in f.calls:
                    if func_roles.get(callee) == CQRSRole.COMMAND:
                        violations.append(
                            f"LAYER_VIOLATION: {f.qualified_name} (query) → {callee} (command)"
                        )
    return violations


# ── Export ────────────────────────────────────────────────────────────────────


def write_graphml(G: nx.DiGraph, path: Path) -> None:
    """Eksport do GraphML — kompatybilny z Gephi / yEd / Neo4j importer."""
    nx.write_graphml(G, str(path))


def write_dot(G: nx.DiGraph, path: Path) -> None:
    """Eksport do DOT — renderowany przez Graphviz."""
    lines = ["digraph CallGraph {", "  rankdir=LR;", "  node [shape=box];", ""]
    for n, data in G.nodes(data=True):
        role = data.get("role", "unknown")
        color = {
            "query": "lightblue",
            "command": "lightsalmon",
            "orchestrator": "lightgreen",
        }.get(role, "white")
        label = data.get("label", n.split(".")[-1])
        lines.append(f'  "{n}" [label="{label}" style=filled fillcolor="{color}"];')
    lines.append("")
    for src, dst in G.edges():
        lines.append(f'  "{src}" -> "{dst}";')
    lines += ["}", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def graph_summary(G: nx.DiGraph, schema: SchemaIR) -> str:
    """Tekstowe podsumowanie grafu."""
    cycles = detect_cycles(G)
    hubs = hub_nodes(G)
    top = centrality_report(G, top_n=5)
    violations = layer_violations(schema)

    lines = [
        f"Nodes     : {G.number_of_nodes()}",
        f"Edges     : {G.number_of_edges()}",
        f"Cycles    : {len(cycles)}",
        f"Hubs      : {len(hubs)}",
        f"Violations: {len(violations)}",
        "",
    ]
    if top:
        lines.append("Top-5 PageRank (architektoniczne centra):")
        for name, score in top:
            short = name.split(".")[-1]
            lines.append(f"  {score:.4f}  {short}")
    if violations:
        lines.append("\nLayer violations:")
        for v in violations[:10]:
            lines.append(f"  {v}")
    if cycles:
        lines.append(f"\nCycles (pierwsze {min(5, len(cycles))}):")
        for c in cycles[:5]:
            lines.append(f"  {' → '.join(c[:4])}{'...' if len(c) > 4 else ''}")
    return "\n".join(lines)
