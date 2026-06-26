"""
Manual / dict passthrough parser.
Used when evidence is already structured (synthetic cases, test fixtures, API payloads).
Every field is marked as extraction_method='direct_json' with confidence 1.0.
"""

from engine.parsers import BaseParser, EvidenceObject, ParseTrace


class ManualParser(BaseParser):

    @property
    def source_type(self) -> str:
        return "manual"

    def parse(self, document: dict) -> EvidenceObject:
        if not isinstance(document, dict):
            raise TypeError(f"ManualParser expects a dict, got {type(document)}")

        fields = list(document.keys())
        trace = ParseTrace(
            source_file="<dict>",
            extraction_method="direct_json",
            fields_extracted=fields,
            fields_missing=[],
            field_confidence={f: 1.0 for f in fields},
        )
        return EvidenceObject(
            evidence=dict(document),
            trace=trace,
            source_type=self.source_type,
        )
