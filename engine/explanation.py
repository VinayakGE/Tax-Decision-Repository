"""
Explanation Engine — converts a populated EvidenceContext into structured,
human-readable explanation blocks. One block per rule executed.
Output is a list of ExplanationBlock dicts consumed by report.py.
"""

from engine.context import EvidenceContext


def _inr(n) -> str:
    """Format integer as Indian-style currency string: ₹X,XX,XXX"""
    if n is None:
        return "₹0"
    n = int(round(n))
    s = str(abs(n))
    if len(s) <= 3:
        return f"₹{s}"
    result = s[-3:]
    s = s[:-3]
    while s:
        result = s[-2:] + "," + result
        s = s[:-2]
    prefix = "-₹" if n < 0 else "₹"
    return f"{prefix}{result}"


def _pct(rate: float) -> str:
    return f"{rate * 100:.0f}%"


def explain(ctx: EvidenceContext) -> dict:
    """
    Returns a structured explanation dict with:
    - case_id, taxpayer_name
    - blocks: list of {rule_id, heading, lines: [str]}
    - summary: the one-paragraph verdict
    """
    blocks = []

    # --- Income Assembly (R-0015) ---
    gross = ctx.get("gross_total_income", 0)
    std_new = ctx.get("standard_deduction_applied_new", 0)
    std_old = ctx.get("standard_deduction_applied_old", 0)
    taxable_new = ctx.get("taxable_income_new_regime", 0)
    taxable_old = ctx.get("taxable_income_old_regime", 0)
    special_items = ctx.get("special_rate_items", [])

    income_lines = [f"Gross total income: {_inr(gross)}"]
    classified = ctx.get("classified_income", {})
    for item in classified.get("head_1_salary", []):
        income_lines.append(f"  Salary ({item.get('employer', 'employer')}): {_inr(item.get('gross_salary', 0))}")
    for item in classified.get("head_5_other_sources", []):
        income_lines.append(f"  Other sources ({item.get('category', 'income')}): {_inr(item.get('amount', 0))}")
    if special_items:
        for si in special_items:
            income_lines.append(
                f"  Capital gains Section {si['section']}: {_inr(si['amount'])} "
                f"(taxable after exemption: {_inr(si.get('taxable_special_amount', si['amount']))} @ {_pct(si['applicable_rate'])})"
            )
    income_lines.append(f"Standard deduction (New Regime): {_inr(std_new)} → taxable income {_inr(taxable_new)}")
    income_lines.append(f"Standard deduction (Old Regime): {_inr(std_old)} → taxable income {_inr(taxable_old)}")

    blocks.append({"rule_id": "R-0015", "heading": "Income Assembly", "lines": income_lines})

    # --- New Regime Slab (R-0017) ---
    slab_detail_new = ctx.get("slab_computation", [])
    slab_tax_new = ctx.get("slab_tax_new_regime", 0)
    new_slab_lines = [f"New Regime slab schedule (Finance Act 2024, Section 115BAC):"]
    for band in slab_detail_new:
        new_slab_lines.append(
            f"  {band.get('band', '')}: {_inr(band.get('applicable_income', 0))} × {_pct(band.get('rate', 0))} = {_inr(band.get('tax', 0))}"
        )
    new_slab_lines.append(f"Slab tax before rebate: {_inr(slab_tax_new)}")
    blocks.append({"rule_id": "R-0017", "heading": "New Regime Slab Computation", "lines": new_slab_lines})

    # --- Old Regime Slab (R-0016) ---
    age_bracket = ctx.get("age_bracket_used", "general")
    slab_tax_old = ctx.get("slab_tax_old_regime", 0)
    old_slab_lines = [
        f"Old Regime slab schedule ({age_bracket} category):",
    ]
    for band in ctx.get("slab_computation", []):
        old_slab_lines.append(
            f"  {band.get('band', '')}: {_inr(band.get('applicable_income', 0))} × {_pct(band.get('rate', 0))} = {_inr(band.get('tax', 0))}"
        )
    old_slab_lines.append(f"Slab tax before rebate: {_inr(slab_tax_old)}")
    blocks.append({"rule_id": "R-0016", "heading": "Old Regime Slab Computation", "lines": old_slab_lines})

    # --- 87A Rebate (R-0019) ---
    total_income = ctx.get("total_income", gross)
    rebate_new = ctx.get("rebate_87A_new_regime", 0)
    rebate_old = ctx.get("rebate_87A_old_regime", 0)
    tax_after_rebate_new = ctx.get("tax_after_rebate_new_regime", slab_tax_new)
    tax_after_rebate_old = ctx.get("tax_after_rebate_old_regime", slab_tax_old)
    rebate_applied = ctx.get("rebate_applied", False)

    rebate_lines = [f"Section 87A Rebate check — total income: {_inr(total_income)}"]
    if rebate_new > 0:
        rebate_lines.append(f"New Regime: income ≤ ₹12,00,000 → rebate = min({_inr(slab_tax_new)}, ₹60,000) = {_inr(rebate_new)}")
        rebate_lines.append(f"Tax after rebate (New Regime): {_inr(tax_after_rebate_new)}")
    else:
        rebate_lines.append(f"New Regime: income {_inr(total_income)} > ₹12,00,000 → no rebate")
        rebate_lines.append(f"Tax after rebate (New Regime): {_inr(tax_after_rebate_new)}")
    if rebate_old > 0:
        rebate_lines.append(f"Old Regime: income ≤ ₹5,00,000 → rebate = {_inr(rebate_old)}")
        rebate_lines.append(f"Tax after rebate (Old Regime): {_inr(tax_after_rebate_old)}")
    else:
        rebate_lines.append(f"Old Regime: income > ₹5,00,000 → no rebate")
        rebate_lines.append(f"Tax after rebate (Old Regime): {_inr(tax_after_rebate_old)}")
    blocks.append({"rule_id": "R-0019", "heading": "Section 87A Rebate", "lines": rebate_lines})

    # --- Surcharge (R-0021) ---
    surcharge_new = ctx.get("surcharge_new_regime", 0)
    surcharge_old = ctx.get("surcharge_old_regime", 0)
    surcharge_bracket = ctx.get("surcharge_bracket", {})
    surcharge_lines = []
    if surcharge_new == 0 and surcharge_old == 0:
        surcharge_lines.append(f"No surcharge — total income {_inr(total_income)} < ₹50,00,000")
    else:
        rate = surcharge_bracket.get("rate", 0)
        surcharge_lines.append(f"Surcharge bracket: {_pct(rate)} (income > ₹{surcharge_bracket.get('income_above', 0) // 100000}L)")
        surcharge_lines.append(f"Surcharge (New Regime): {_inr(surcharge_new)}")
        surcharge_lines.append(f"Surcharge (Old Regime): {_inr(surcharge_old)}")
    blocks.append({"rule_id": "R-0021", "heading": "Surcharge", "lines": surcharge_lines})

    # --- Cess (R-0020) ---
    cess_new = ctx.get("cess_new_regime", 0)
    cess_old = ctx.get("cess_old_regime", 0)
    total_tax_new = ctx.get("total_tax_new_regime", 0)
    total_tax_old = ctx.get("total_tax_old_regime", 0)
    cess_lines = [
        f"Health & Education Cess: 4% on (tax + surcharge)",
        f"New Regime: ({_inr(tax_after_rebate_new)} + {_inr(surcharge_new)}) × 4% = {_inr(cess_new)} → total tax {_inr(total_tax_new)}",
        f"Old Regime: ({_inr(tax_after_rebate_old)} + {_inr(surcharge_old)}) × 4% = {_inr(cess_old)} → total tax {_inr(total_tax_old)}",
    ]
    blocks.append({"rule_id": "R-0020", "heading": "Health & Education Cess", "lines": cess_lines})

    # --- Regime Recommendation (R-0018) ---
    recommendation = ctx.get("regime_recommendation", "new_regime")
    saving = ctx.get("tax_saving_amount", 0)
    rec_lines = [
        f"New Regime total tax: {_inr(total_tax_new)}",
        f"Old Regime total tax: {_inr(total_tax_old)}",
        f"Recommended: {'New Regime' if recommendation == 'new_regime' else 'Old Regime'} — saves {_inr(saving)}",
    ]
    if recommendation == "old_regime":
        rec_lines.append("Action required: submit Form 12BAA to employer before March 31 to switch regime.")
    blocks.append({"rule_id": "R-0018", "heading": "Regime Recommendation", "lines": rec_lines})

    # --- Refund / Demand (R-0023) ---
    outcome = ctx.get("outcome", "")
    refund = ctx.get("refund_amount")
    demand = ctx.get("demand_amount")
    tds_used = ctx.get("tds_credit_used", 0)
    total_paid = ctx.get("total_taxes_paid", 0)
    total_interest = ctx.get("total_interest", 0)
    position_lines = [
        f"Total tax due ({recommendation}): {_inr(total_tax_new if recommendation == 'new_regime' else total_tax_old)}",
    ]
    if total_interest > 0:
        position_lines.append(f"Interest (234A/B/C): {_inr(total_interest)}")
    position_lines.append(f"TDS credits from 26AS: {_inr(tds_used)}")
    if outcome == "refund":
        position_lines.append(f"REFUND: {_inr(refund)} — file ITR to claim.")
    elif outcome == "demand":
        position_lines.append(f"DEMAND: {_inr(demand)} — pay under Challan 280 before filing (Section 140A).")
    else:
        position_lines.append("NIL BALANCE — no refund or demand.")
    blocks.append({"rule_id": "R-0023", "heading": "Final Tax Position", "lines": position_lines})

    # --- One-paragraph summary ---
    regime_label = "New Regime" if recommendation == "new_regime" else "Old Regime"
    final_tax = total_tax_new if recommendation == "new_regime" else total_tax_old

    if outcome == "refund":
        verdict = (
            f"Your total income is {_inr(gross)}. Under the {regime_label}, your final tax liability "
            f"is {_inr(final_tax)}. Your employer deducted {_inr(tds_used)} as TDS — "
            f"you are entitled to a refund of {_inr(refund)}. "
            f"The {regime_label} saves you {_inr(saving)} compared to the other option."
        )
    elif outcome == "demand":
        verdict = (
            f"Your total income is {_inr(gross)}. Under the {regime_label}, your final tax liability "
            f"is {_inr(final_tax)}. After TDS credits of {_inr(tds_used)}, you owe {_inr(demand)}. "
            f"Pay this under Challan 280 before filing your ITR."
        )
    else:
        verdict = (
            f"Your total income is {_inr(gross)}. Under the {regime_label}, your final tax liability "
            f"is {_inr(final_tax)}, fully covered by TDS. No refund or demand."
        )

    return {
        "case_id": ctx.get("case_id", ""),
        "taxpayer_name": ctx.get("taxpayer_name", "Taxpayer"),
        "assessment_year": "AY2025-26",
        "regime_recommendation": recommendation,
        "blocks": blocks,
        "summary": verdict,
    }
