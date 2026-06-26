"""
Synthesizer — generates input.json cases from MatrixCell specifications.
Used to populate the pending cells in REQUIRED_COVERAGE with runnable inputs.
"""

from dvf.generator.matrix import MatrixCell

# Income amounts representative of each bracket's midpoint
_INCOME_FOR_LEVEL = {
    "below_5L":          400000,
    "5L_to_7L":          600000,
    "7L_to_12L":        1000000,
    "above_12L_to_15L": 1400000,
    "above_15L_to_50L": 3000000,
    "above_50L":        7500000,
}

# Age representative values per bracket
_AGE_FOR_BRACKET = {
    "general":     35,
    "senior":      65,
    "super_senior": 82,
}

# TDS as fraction of gross income — rough proxy for withholding
_TDS_RATE = 0.08


def synthesize_input(cell: MatrixCell, seq: int) -> dict:
    """
    Convert a MatrixCell into a minimal input.json dict that the pipeline can run.
    seq is a monotone counter used to produce stable, unique case IDs for pending cells.
    """
    gross = _INCOME_FOR_LEVEL[cell.income_level]
    age = _AGE_FOR_BRACKET[cell.age_bracket]
    tds = round(gross * _TDS_RATE)

    case_id = f"GM-SYNTH-{seq:04d}"
    taxpayer = {
        "name": f"Synthetic Taxpayer {seq:04d}",
        "pan": f"SYNTH{seq:04d}P",
        "age": age,
        "age_bracket": cell.age_bracket,
    }

    evidence: dict = {
        "filing_timing": cell.filing_timing,
    }

    income_type = cell.income_type
    if income_type in ("salary_only", "salary_fd", "salary_ltcg", "salary_business", "salary_hp"):
        if income_type == "salary_fd":
            # Split gross into salary + FD interest
            fd = round(gross * 0.05)
            salary = gross - fd
            evidence["gross_salary"] = salary
            evidence["fd_interest"] = fd
        elif income_type == "salary_ltcg":
            ltcg = round(gross * 0.10)
            salary = gross - ltcg
            evidence["gross_salary"] = salary
            evidence["ltcg_112A"] = ltcg
        elif income_type == "salary_business":
            biz = round(gross * 0.20)
            salary = gross - biz
            evidence["gross_salary"] = salary
            evidence["business_income"] = biz
        elif income_type == "salary_hp":
            hp = round(gross * 0.15)
            salary = gross - hp
            evidence["gross_salary"] = salary
            evidence["house_property_income"] = hp
        else:
            evidence["gross_salary"] = gross

        evidence["tds_deducted"] = tds
        evidence["tds_section"] = "192"

    elif income_type == "business_only":
        evidence["business_income"] = gross
        evidence["tds_deducted"] = tds
        evidence["tds_section"] = "194J"
        # Business taxpayers may have advance tax; keep simple for synthesis
        evidence["advance_tax_paid"] = 0

    # Special items override
    if cell.has_special_items == "ltcg_112A":
        ltcg = round(gross * 0.10)
        evidence.setdefault("ltcg_112A", ltcg)
    elif cell.has_special_items == "stcg_111A":
        stcg = round(gross * 0.10)
        evidence["stcg_111A"] = stcg
    elif cell.has_special_items == "lottery_115BB":
        lottery = round(gross * 0.05)
        evidence["lottery_115BB"] = lottery

    evidence["regime_chosen"] = cell.regime if cell.regime != "compare" else "new_regime"

    return {
        "case_id": case_id,
        "taxpayer": taxpayer,
        "evidence": evidence,
        "matrix_cell": {
            "income_type": cell.income_type,
            "age_bracket": cell.age_bracket,
            "income_level": cell.income_level,
            "regime": cell.regime,
            "has_special_items": cell.has_special_items,
            "filing_timing": cell.filing_timing,
        },
    }
