"""code2schema — Semantic Compiler for Software Systems."""

from code2schema.core.models import SchemaIR, CQRSRole, FunctionIR, ModuleIR
from code2schema.core.extractor import extract_project, extract_module
from code2schema.analyzer.cqrs import analyze

__all__ = [
    "SchemaIR",
    "CQRSRole",
    "FunctionIR",
    "ModuleIR",
    "extract_project",
    "extract_module",
    "analyze",
]
__version__ = "0.1.9"
