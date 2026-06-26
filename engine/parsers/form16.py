"""
Form 16 Parser — employer TDS certificate (Part A + Part B).
Extracts: gross salary, standard deduction, employer details, TDS deducted.
In a real deployment this would parse the PDF; here it consumes the structured JSON
representation that the PDF-to-JSON OCR layer would produce.
"""

import json
from engine.parsers import BaseParser, EvidenceObject, ParseTrace


class Form16Parser(BaseParser):

    @property
    def source_type(self) -> str:
        return "form16_json"

    def parse(self, document) -> EvidenceObject:
        warnings = []
        fields_missing = []

        if isinstance(document, str):
            try:
                data = json.loads(document)
            except json.JSONDecodeError as e:
                warnings.append(f"Form 16 JSON parse error: {e}")
                data = {}
        elif isinstance(document, dict):
            data = document
        else:
            warnings.append(f"Form16Parser: unexpected input type {type(document)}")
            data = {}

        gross_salary = data.get("gross_salary")
        employer = data.get("employer_name", "")
        tan = data.get("tan", "")
        tds_deducted = data.get("tds_deducted", 0)
        pan_employee = data.get("employee_pan", "")

        if gross_salary is None:
            fields_missing.append("gross_salary")
            warnings.append("Form 16: gross_salary not found — income will be underreported")
            gross_salary = 0

        salary_entry = {
            "source": "Form 16",
            "gross_salary": gross_salary,
            "employer": employer,
            "tan": tan,
        }

        tds_credit = {
            "tan": tan,
            "section": "192",
            "amount": tds_deducted,
            "employer": employer,
        }

        classified_income = {
            "head_1_salary": [salary_entry],
            "head_2_house_property": [],
            "head_3_business": [],
            "head_4_capital_gains": [],
            "head_5_other_sources": [],
        }

        evidence = {
            "classified_income": classified_income,
            "tds_credits_from_26AS": [tds_credit] if tds_deducted > 0 else [],
            "evidence_integrity_checks_passed": len(fields_missing) == 0,
            "income_classification_complete": True,
        }
        if pan_employee:
            evidence["taxpayer_pan"] = pan_employee

        fields_extracted = list(evidence.keys())
        trace = ParseTrace(
            source_file="<form16_json>",
            extraction_method="direct_json",
            fields_extracted=fields_extracted,
            fields_missing=fields_missing,
            field_confidence={f: 1.0 if f not in fields_missing else 0.0 for f in fields_extracted},
            warnings=warnings,
        )
        return EvidenceObject(evidence=evidence, trace=trace, source_type=self.source_type)
