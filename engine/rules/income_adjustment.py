"""
Income Adjustment Engine — Stage 3 of the tax pipeline.
Section 10 salary exemptions that reduce effective salary before Gross Total Income is
assembled in R-0015. HRA (10(13A)) is the first rule in this stage; LTA, transport
allowance, and other Sec 10 exemptions slot in here as they are implemented.

Rules R-0029 through R-0034. Each takes EvidenceContext and updates it in place.
"""

from engine.context import EvidenceContext

_METRO_CITIES = {"Delhi", "Mumbai", "Kolkata", "Chennai"}


# ---------------------------------------------------------------------------
# R-0029: HRA Evidence Completeness
# ---------------------------------------------------------------------------

def r0029_hra_evidence_completeness(ctx: EvidenceContext) -> None:
    """
    Assess whether the HRA exemption can be computed.
    Produces hra_evidence_status with status COMPLETE / INCOMPLETE / NOT_APPLICABLE
    and a suggested_questions list that the future Intake Engine can surface to the user.
    """
    regime = ctx.get("regime_chosen", "new_regime")

    if regime == "new_regime":
        ctx.set("hra_evidence_status", {
            "status": "NOT_APPLICABLE",
            "reason": "HRA exemption u/s 10(13A) is not available under the New Regime",
            "missing_fields": [],
            "suggested_questions": [],
        })
        return

    classified = ctx.get("classified_income") or {}
    salary_items = classified.get("head_1_salary", [])
    if not salary_items:
        ctx.set("hra_evidence_status", {
            "status": "NOT_APPLICABLE",
            "reason": "No salary income — HRA exemption applies only to salary taxpayers",
            "missing_fields": [],
            "suggested_questions": [],
        })
        return

    hra_actual = ctx.get("hra_actual")
    if not hra_actual:
        ctx.set("hra_evidence_status", {
            "status": "NOT_APPLICABLE",
            "reason": "No HRA received from employer",
            "missing_fields": [],
            "suggested_questions": [],
        })
        return

    # HRA received — verify the three inputs needed for the exemption formula
    missing_fields = []
    suggested_questions = []

    if ctx.get("basic_salary") is None:
        missing_fields.append("basic_salary")
        suggested_questions.append("What is your annual basic salary component?")

    if ctx.get("rent_paid") is None:
        missing_fields.append("rent_paid")
        suggested_questions.append("What is the total annual rent you paid during the year?")

    if ctx.get("city_type") is None:
        missing_fields.append("city_type")
        suggested_questions.append(
            "Is your rented accommodation in a metro city (Delhi, Mumbai, Kolkata, or Chennai)?"
        )

    if missing_fields:
        ctx.set("hra_evidence_status", {
            "status": "INCOMPLETE",
            "missing_fields": missing_fields,
            "suggested_questions": suggested_questions,
        })
    else:
        ctx.set("hra_evidence_status", {
            "status": "COMPLETE",
            "missing_fields": [],
            "suggested_questions": [],
        })


# ---------------------------------------------------------------------------
# R-0030: HRA Candidate 1 — Actual HRA Received
# ---------------------------------------------------------------------------

def r0030_hra_candidate_1(ctx: EvidenceContext) -> None:
    """Candidate 1: Actual HRA amount received from employer during the year."""
    status_info = ctx.get("hra_evidence_status") or {}
    if status_info.get("status") == "COMPLETE":
        ctx.set("hra_candidate_1", int(ctx.get("hra_actual", 0)))
    else:
        ctx.set("hra_candidate_1", 0)


# ---------------------------------------------------------------------------
# R-0031: HRA Candidate 2 — Metro / Non-Metro Percentage of Basic
# ---------------------------------------------------------------------------

def r0031_hra_candidate_2(ctx: EvidenceContext) -> None:
    """
    Candidate 2: 50% of basic salary for metro cities, 40% for non-metro.
    Metro cities per Section 10(13A): Delhi, Mumbai, Kolkata, Chennai.
    city_type may be a city name or the labels 'metro' / 'non_metro'.
    """
    status_info = ctx.get("hra_evidence_status") or {}
    if status_info.get("status") != "COMPLETE":
        ctx.set("hra_candidate_2", 0)
        return

    basic = int(ctx.get("basic_salary", 0))
    city = (ctx.get("city_type") or "").strip()
    is_metro = city in _METRO_CITIES or city.lower() == "metro"
    rate = 0.50 if is_metro else 0.40
    candidate_2 = round(basic * rate)

    ctx.update({
        "hra_candidate_2": candidate_2,
        "hra_metro_rate_applied": rate,
        "hra_city_is_metro": is_metro,
    })


# ---------------------------------------------------------------------------
# R-0032: HRA Candidate 3 — Rent Paid Minus 10% of Basic
# ---------------------------------------------------------------------------

def r0032_hra_candidate_3(ctx: EvidenceContext) -> None:
    """Candidate 3: Excess of rent paid over 10% of basic salary (floored at 0)."""
    status_info = ctx.get("hra_evidence_status") or {}
    if status_info.get("status") != "COMPLETE":
        ctx.set("hra_candidate_3", 0)
        return

    rent = int(ctx.get("rent_paid", 0))
    basic = int(ctx.get("basic_salary", 0))
    candidate_3 = max(0, rent - round(basic * 0.10))
    ctx.set("hra_candidate_3", candidate_3)


# ---------------------------------------------------------------------------
# R-0033: HRA Final Exemption — min(c1, c2, c3)
# ---------------------------------------------------------------------------

def r0033_hra_final_exemption(ctx: EvidenceContext) -> None:
    """Final HRA exemption = min(candidate_1, candidate_2, candidate_3)."""
    status_info = ctx.get("hra_evidence_status") or {}

    if status_info.get("status") != "COMPLETE":
        ctx.update({
            "hra_exemption": 0,
            "hra_limiting_candidate": None,
        })
        return

    c1 = ctx.get("hra_candidate_1", 0)
    c2 = ctx.get("hra_candidate_2", 0)
    c3 = ctx.get("hra_candidate_3", 0)

    exemption = min(c1, c2, c3)
    if c1 == exemption:
        limiting = "c1"
    elif c2 == exemption:
        limiting = "c2"
    else:
        limiting = "c3"

    ctx.update({
        "hra_exemption": exemption,
        "hra_limiting_candidate": limiting,
        "hra_section_ref": "Section 10(13A)",
        "hra_table_ref": "TaxTable:2024.deductions.salary_exemptions.HRA_10_13A",
    })


# ---------------------------------------------------------------------------
# R-0034: Income Adjustment Aggregator
# ---------------------------------------------------------------------------

def r0034_income_adjustment_aggregator(ctx: EvidenceContext) -> None:
    """
    Aggregate all Section 10 salary exemptions.
    Produces total_salary_sec10_exemption consumed by R-0015 (Income Assembly).
    """
    hra = ctx.get("hra_exemption", 0) or 0
    # Future: lta_exemption, children_education_allowance, etc.

    total = hra
    breakdown = {}
    if hra:
        breakdown["HRA_10_13A"] = hra

    ctx.update({
        "total_salary_sec10_exemption": total,
        "income_adjustment_breakdown": breakdown,
    })
