"""
Parser Framework — every parser implements BaseParser.parse(document) -> EvidenceObject.
The executor never knows whether evidence came from JSON, PDF, OCR, or API.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParseTrace:
    """Source provenance for each parsed field."""
    source_file: str
    extraction_method: str          # "direct_json", "pdf_text", "ocr", "api", "manual"
    fields_extracted: list          # field names successfully populated
    fields_missing: list            # field names the parser could not populate
    field_confidence: dict          # {field_name: float 0.0-1.0}
    warnings: list = field(default_factory=list)


@dataclass
class EvidenceObject:
    """
    The universal input type for the Rule Executor.
    Every parser produces this; the executor consumes it.
    """
    evidence: dict                  # the key-value evidence dict
    trace: ParseTrace               # provenance of each field
    source_type: str                # "ais_json", "form16_json", "manual", etc.


class BaseParser(ABC):
    """
    Contract every parser must implement.
    parse(document) -> EvidenceObject
    document can be a file path, raw string, dict, or bytes — parser decides.
    """

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Identifier for the document type this parser handles."""
        ...

    @abstractmethod
    def parse(self, document: Any) -> EvidenceObject:
        """
        Parse the document and return an EvidenceObject.
        Must never raise — return partial evidence with warnings instead.
        """
        ...
