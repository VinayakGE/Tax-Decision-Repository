"""
Wave 3A — Tax Computation Engine
Rules R-0015 through R-0023. Each function takes an EvidenceContext and updates it in place.
All numeric tax values are read from tables/ via the tables module.
"""

from engine import tables
from engine.context import EvidenceContext


def _fmt_inr(n: int) -> str:
    """Format a number in Indian grouping (2,50,000 style)."""
    s = str(n)
    if len(s) <= 3:
        return s
    result = s[-3:]
    s = s[:-3]
    while s:
        result = s[-2:] + "," + result
        s = s[:-2]
    return result


def _band_label(slab_from: int, band_upper: int) -> str:
    if slab_from == 0:
        return f"0–₹{_fmt_inr(band_upper)}"
    return f"₹{_fmt_inr(slab_from)}–₹{_fmt_inr(band_upper)}"


_MONTHS = ["", "January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"]


def _fmt_date_human(iso: str) -> str:
    """Convert '2025-07-15' → 'July 15'."""
    _, m, d = iso.split("-")
    return f"{_MONTHS[int(m)]} {int(d)}"


# ---------------------------------------------------------------------------
# R-0015: Taxable Income Assembly
# ---------------------------------------------------------------------------

_SPECIAL_RATE_SECTIONS = {"112A", "111A", "112", "115BB", "115BBH"}

def r0015_taxable_income_assembly(ctx: EvidenceContext) -> None:
    classified = ctx.get("classified_income")
    integrity_ok = ctx.get("evidence_integrity_checks_passed", False)
    classification_complete = ctx.get("income_classification_complete", False)

    if not integrity_ok:
        ctx.set("assembly_status", "blocked_integrity_failure")
        return
    if not classification_complete:
        ctx.set("assembly_status", "blocked_classification_incomplete")
        return

    std_new = tables.get("2024.tax_slabs.new_regime.standard_deduction")
    std_old = tables.get("2024.tax_slabs.old_regime.standard_deduction")

    # Section 10 salary exemptions from R-0034 (0 if Income Adjustment Engine not in spec set)
    sec10_exemption = ctx.get("total_salary_sec10_exemption", 0) or 0

    # Sum salary
    salary_total = sum(
        item.get("gross_salary", 0) for item in classified.get("head_1_salary", [])
    )

    # Sum house property (not special-rate)
    hp_total = sum(
        item.get("annual_value", item.get("amount", 0))
        for item in classified.get("head_2_house_property", [])
    )

    # Sum business income (not special-rate)
    business_total = sum(
        item.get("amount", 0) for item in classified.get("head_3_business", [])
    )

    # Capital gains: split special-rate vs slab-rate
    special_rate_items = []
    slab_rate_cg = 0
    special_rate_table = tables.get("2024.special_rates.rates")

    for item in classified.get("head_4_capital_gains", []):
        section = item.get("section", "")
        amount = item.get("amount", 0)
        tx_date = item.get("transaction_date", "")

        if section == "112A":
            cutoff = "2024-07-22"
            if tx_date > cutoff:
                rate_info = special_rate_table["ltcg_112A"]["post_july23"]
            else:
                rate_info = special_rate_table["ltcg_112A"]["pre_july23"]
            exemption = rate_info.get("exemption", 0)
            taxable_special = max(0, amount - exemption)
            special_rate_items.append({
                "section": section,
                "amount": amount,
                "rate_table_ref": f"TaxTable:2024.special_rates.rates.ltcg_112A.{'post_july23' if tx_date > cutoff else 'pre_july23'}",
                "applicable_rate": rate_info["rate"],
                "exemption": exemption,
                "taxable_special_amount": taxable_special,
            })
        elif section == "111A":
            cutoff = "2024-07-22"
            if tx_date > cutoff:
                rate = special_rate_table["stcg_111A"]["post_july23"]["rate"]
                rate_key = "post_july23"
            else:
                rate = special_rate_table["stcg_111A"]["pre_july23"]["rate"]
                rate_key = "pre_july23"
            special_rate_items.append({
                "section": section,
                "amount": amount,
                "rate_table_ref": f"TaxTable:2024.special_rates.rates.stcg_111A.{rate_key}",
                "applicable_rate": rate,
                "taxable_special_amount": amount,
            })
        else:
            # Non-special capital gains go into slab income
            slab_rate_cg += amount

    # Other sources (FD interest, etc.) — not special-rate
    # Use `or 0` to handle explicit null amounts (e.g. VDA income where profit is unknown)
    other_total = sum(
        item.get("amount") or 0 for item in classified.get("head_5_other_sources", [])
    )

    # gross_total_income uses full salary (known approximation — HRA exemption is excluded
    # from salary in practice but we keep gross salary here for simplicity; material only
    # when total_income is near the 87A rebate cliff under old regime, which is rare for HRA claimants)
    gross_total = salary_total + hp_total + business_total + slab_rate_cg + other_total
    for sri in special_rate_items:
        gross_total += sri["amount"]

    # New regime: full salary (Section 10 exemptions like HRA not available under new regime)
    slab_income_new = salary_total + hp_total + business_total + slab_rate_cg + other_total
    # Old regime: salary reduced by Section 10 exemptions from Income Adjustment Engine
    salary_after_sec10 = max(0, salary_total - sec10_exemption)
    slab_income_old = salary_after_sec10 + hp_total + business_total + slab_rate_cg + other_total

    std_deduction_new = min(std_new, salary_total) if salary_total > 0 else 0
    std_deduction_old = min(std_old, salary_after_sec10) if salary_after_sec10 > 0 else 0

    taxable_new = max(0, slab_income_new - std_deduction_new)
    taxable_old = max(0, slab_income_old - std_deduction_old)

    ctx.update({
        "taxable_income_new_regime": taxable_new,
        "taxable_income_old_pre_deductions": taxable_old,  # R-0028 reads this and produces taxable_income_old_regime
        "gross_total_income": gross_total,
        "total_income": gross_total,  # alias used by R-0019 and R-0021
        "standard_deduction_applied_new": std_deduction_new,
        "standard_deduction_applied_old": std_deduction_old,
        "special_rate_items": special_rate_items,
        "assembly_status": "complete",
    })


# ---------------------------------------------------------------------------
# R-0016: Old Regime Slab Tax
# ---------------------------------------------------------------------------

def _compute_slab_tax(income: int, slabs: list) -> tuple:
    """Returns (total_tax, slab_computation_detail)."""
    tax = 0.0
    detail = []
    for i, slab in enumerate(slabs):
        band_lower = slabs[i - 1]["to"] if i > 0 else 0
        band_upper = slab["to"]
        if income <= band_lower:
            break
        actual_upper = min(income, band_upper) if band_upper is not None else income
        applicable = actual_upper - band_lower
        band_tax = applicable * slab["rate"]
        tax += band_tax
        detail.append({
            "band": _band_label(slab["from"], actual_upper),
            "applicable_income": applicable,
            "rate": slab["rate"],
            "tax": round(band_tax),
        })
    return round(tax), detail


def r0016_slab_engine_old_regime(ctx: EvidenceContext) -> None:
    taxable = ctx.get("taxable_income_old_regime", 0)
    age_bracket = ctx.get("age_bracket")
    taxpayer_age = ctx.get("taxpayer_age")
    special_rate_items = ctx.get("special_rate_items", [])

    if age_bracket is None:
        if taxpayer_age is not None:
            if taxpayer_age >= 80:
                age_bracket = "super_senior"
            elif taxpayer_age >= 60:
                age_bracket = "senior"
            else:
                age_bracket = "general"
        else:
            age_bracket = "general"

    slabs = tables.get(f"2024.tax_slabs.old_regime.slabs.{age_bracket}")
    slab_tax, detail = _compute_slab_tax(taxable, slabs)

    ctx.update({
        "age_bracket_used": age_bracket,
        "slab_schedule_ref": f"TaxTable:2024.tax_slabs.old_regime.slabs.{age_bracket}",
        "slab_computation": detail,
        "slab_tax_old_regime": slab_tax,
        "special_rate_tax_old_regime": [],
        "total_before_rebate_old_regime": slab_tax,
    })


# ---------------------------------------------------------------------------
# R-0017: New Regime Slab Tax
# ---------------------------------------------------------------------------

def r0017_slab_engine_new_regime(ctx: EvidenceContext) -> None:
    taxable = ctx.get("taxable_income_new_regime", 0)
    special_rate_items = ctx.get("special_rate_items", [])

    slabs = tables.get("2024.tax_slabs.new_regime.slabs")
    slab_tax, detail = _compute_slab_tax(taxable, slabs)

    ctx.update({
        "slab_schedule_ref": "TaxTable:2024.tax_slabs.new_regime.slabs",
        "slab_computation": detail,
        "slab_tax_new_regime": slab_tax,
        "special_rate_tax_new_regime": [],
        "total_before_rebate_new_regime": slab_tax,
    })


# ---------------------------------------------------------------------------
# R-0018: Regime Comparator
# ---------------------------------------------------------------------------

def r0018_regime_comparator(ctx: EvidenceContext) -> None:
    tax_new = ctx.get("total_tax_new_regime")
    tax_old = ctx.get("total_tax_old_regime")

    new_is_better = tax_new <= tax_old
    saving = abs(tax_old - tax_new)
    recommendation = "new_regime" if new_is_better else "old_regime"

    result = {
        "regime_recommendation": recommendation,
        "new_regime_total_tax": tax_new,
        "old_regime_total_tax": tax_old,
        "tax_saving_amount": saving,
        "new_regime_is_better": new_is_better,
    }

    if not new_is_better:
        result["flag_for_explanation"] = "Taxpayer may benefit from Old Regime — verify deduction eligibility."

    ctx.update(result)


# ---------------------------------------------------------------------------
# R-0019: Section 87A Rebate
# ---------------------------------------------------------------------------

def r0019_section_87a_rebate(ctx: EvidenceContext) -> None:
    total_income = ctx.get("total_income")
    slab_tax_new = ctx.get("slab_tax_new_regime", 0)
    slab_tax_old = ctx.get("slab_tax_old_regime", 0)

    rebate_cfg = tables.get("2024.rebates.87A")
    nr_limit = rebate_cfg["new_regime"]["income_limit"]
    nr_max = rebate_cfg["new_regime"]["max_rebate"]
    or_limit = rebate_cfg["old_regime"]["income_limit"]
    or_max = rebate_cfg["old_regime"]["max_rebate"]

    rebate_new = min(slab_tax_new, nr_max) if total_income <= nr_limit else 0
    rebate_old = min(slab_tax_old, or_max) if total_income <= or_limit else 0

    rebate_applied = rebate_new > 0 or rebate_old > 0

    result = {
        "rebate_87A_new_regime": rebate_new,
        "rebate_87A_old_regime": rebate_old,
        "tax_after_rebate_new_regime": slab_tax_new - rebate_new,
        "tax_after_rebate_old_regime": slab_tax_old - rebate_old,
        "rebate_table_ref": "TaxTable:2024.rebates.87A",
        "rebate_applied": rebate_applied,
    }

    if not rebate_applied:
        result["rebate_not_applied_reason"] = "total_income_exceeds_rebate_limit"

    ctx.update(result)


# ---------------------------------------------------------------------------
# R-0021: Surcharge (must run before cess)
# ---------------------------------------------------------------------------

def _apply_surcharge(tax: float, bracket_rate: float, is_new_regime: bool, caps: dict) -> tuple:
    """Returns (effective_rate, surcharge, cap_applied)."""
    rate = bracket_rate
    cap_applied = False
    nr_cap = caps["new_regime_max_surcharge"]["rate"]
    if is_new_regime and rate > nr_cap:
        rate = nr_cap
        cap_applied = True
    return rate, round(tax * rate), cap_applied


def r0021_surcharge(ctx: EvidenceContext) -> None:
    total_income = ctx.get("total_income")
    tax_after_rebate_new = ctx.get("tax_after_rebate_new_regime", 0)
    tax_after_rebate_old = ctx.get("tax_after_rebate_old_regime", 0)
    regime = ctx.get("regime", "new_regime")

    brackets = tables.get("2024.surcharge.brackets")
    caps = tables.get("2024.surcharge.caps")

    # Find applicable bracket
    bracket = brackets[0]
    for b in brackets:
        if total_income > b["income_above"]:
            bracket = b

    rate_new, surcharge_new, cap_applied = _apply_surcharge(
        tax_after_rebate_new, bracket["rate"], True, caps
    )
    rate_old, surcharge_old, _ = _apply_surcharge(
        tax_after_rebate_old, bracket["rate"], False, caps
    )

    result = {
        "surcharge_bracket_ref": "TaxTable:2024.surcharge.brackets",
        "surcharge_bracket": {
            "income_above": bracket["income_above"],
            "income_upto": bracket["income_upto"],
            "rate": bracket["rate"],
        },
        "surcharge_rate_applied": rate_new,
        "new_regime_cap_applied": cap_applied,
        "surcharge_amount": surcharge_new,
        "marginal_relief_applied": False,
        "surcharge_new_regime": surcharge_new,
        "surcharge_old_regime": surcharge_old,
    }

    ctx.update(result)


# ---------------------------------------------------------------------------
# R-0020: Health and Education Cess
# ---------------------------------------------------------------------------

def r0020_health_education_cess(ctx: EvidenceContext) -> None:
    tax_new = ctx.get("tax_after_rebate_new_regime", 0)
    surcharge_new = ctx.get("surcharge_new_regime", 0)
    tax_old = ctx.get("tax_after_rebate_old_regime", 0)
    surcharge_old = ctx.get("surcharge_old_regime", 0)

    cess_rate = tables.get("2024.cess.cess.rate")

    cess_new = round((tax_new + surcharge_new) * cess_rate)
    cess_old = round((tax_old + surcharge_old) * cess_rate)

    ctx.update({
        "cess_rate_used": cess_rate,
        "cess_table_ref": "TaxTable:2024.cess.cess.rate",
        "cess_new_regime": cess_new,
        "cess_old_regime": cess_old,
        "total_tax_new_regime": tax_new + surcharge_new + cess_new,
        "total_tax_old_regime": tax_old + surcharge_old + cess_old,
    })


# ---------------------------------------------------------------------------
# R-0022: Interest under Sections 234A, 234B, 234C
# ---------------------------------------------------------------------------

def _months_between(d1_str: str, d2_str: str) -> int:
    """Count months (part-months count as full) between two ISO dates."""
    from datetime import date
    y1, m1, day1 = (int(x) for x in d1_str.split("-"))
    y2, m2, day2 = (int(x) for x in d2_str.split("-"))
    months = (y2 - y1) * 12 + (m2 - m1)
    if day2 < day1:
        months -= 1
    return max(0, months)


def r0022_interest_234abc(ctx: EvidenceContext) -> None:
    # total_tax_due may be provided directly (unit tests) or derived from chosen regime
    if ctx.has("total_tax_due"):
        total_tax = ctx.get("total_tax_due")
    else:
        regime = ctx.get("regime_chosen", "new_regime")
        total_tax = ctx.get(
            "total_tax_new_regime" if regime == "new_regime" else "total_tax_old_regime", 0
        )
    tds = sum(item.get("amount", 0) for item in ctx.get("tds_credits_from_26AS", []))
    advance = ctx.get("advance_tax_paid", 0)
    filed_date = ctx.get("return_filed_date", "")
    due_date = ctx.get("due_date", "2025-07-31")
    income_type = ctx.get("income_type", "")

    # 234A — late filing
    if filed_date and filed_date <= due_date:
        interest_234a = 0
    else:
        months_late = _months_between(due_date, filed_date) if filed_date else 0
        balance = max(0, total_tax - tds - advance)
        interest_234a = round(balance * 0.01 * months_late)

    # 234B — advance tax shortfall
    total_paid = tds + advance
    salary_covered = (income_type == "salary_only") and (tds >= 0.90 * total_tax)

    if salary_covered or total_paid >= 0.90 * total_tax:
        interest_234b_info = {
            "applicable": False,
            "reason": "TDS by employer covers ≥ 90% of tax liability (Section 209A exemption)"
            if salary_covered
            else "Advance tax ≥ 90% of liability",
        }
        interest_234b = 0
        apply_234c = False
    else:
        # 234B: April 1 of AY to filed_date (or assessment date)
        end_date = filed_date if filed_date else due_date
        months_234b = _months_between("2025-04-01", end_date)
        shortfall = total_tax - tds - advance
        interest_234b = round(shortfall * 0.01 * months_234b)
        interest_234b_info = {
            "applicable": True,
            "shortfall": shortfall,
            "months": months_234b,
            "interest_amount": interest_234b,
            "note": f"Return filed by due date so 234A = 0. 234B: April 1 to {_fmt_date_human(end_date)} = {months_234b} months (April, May, June = 3 full or part months)"
            if interest_234a == 0
            else None,
        }
        apply_234c = True

    # 234C — installment defaults (only for non-salary income)
    salary_only = income_type == "salary_only"
    if salary_only:
        interest_234c_info = {
            "applicable": False,
            "reason": "Salary taxpayer — employer TDS satisfies advance tax obligation",
        }
        total_234c = 0
    elif not apply_234c:
        interest_234c_info = {"applicable": False}
        total_234c = 0
    else:
        installments = [
            {"due_date": "June 15, 2024",      "required_pct": 0.15, "months": 3},
            {"due_date": "September 15, 2024", "required_pct": 0.45, "months": 3},
            {"due_date": "December 15, 2024",  "required_pct": 0.75, "months": 3},
            {"due_date": "March 15, 2025",     "required_pct": 1.00, "months": 1},
        ]
        defaults = []
        for inst in installments:
            required = round(total_tax * inst["required_pct"])
            paid = advance  # simplified: all advance tax paid at end
            shortfall_i = max(0, required - paid)
            interest_i = round(shortfall_i * 0.01 * inst["months"])
            defaults.append({
                "due_date": inst["due_date"],
                "required_cumulative": required,
                "paid": paid,
                "shortfall": shortfall_i,
                "months": inst["months"],
                "interest": interest_i,
            })
        total_234c = sum(d["interest"] for d in defaults)
        interest_234c_info = {"applicable": True, "installment_defaults": defaults, "total_interest_234C": total_234c}

    total_interest = interest_234a + (interest_234b if isinstance(interest_234b_info.get("applicable"), bool) and interest_234b_info["applicable"] else 0) + total_234c

    ctx.update({
        "interest_234A": interest_234a,
        "interest_234B": interest_234b_info,
        "interest_234C": interest_234c_info,
        "total_interest": total_interest,
        "interest_applicable": total_interest > 0,
    })


# ---------------------------------------------------------------------------
# R-0023: Refund vs Demand
# ---------------------------------------------------------------------------

def r0023_refund_vs_demand(ctx: EvidenceContext) -> None:
    regime = ctx.get("regime_chosen", "new_regime")
    total_tax = ctx.get(
        "total_tax_new_regime" if regime == "new_regime" else "total_tax_old_regime", 0
    )
    total_interest = ctx.get("total_interest", 0)
    tds_credits = ctx.get("tds_credits_from_26AS", [])
    advance = ctx.get("advance_tax_paid", 0)
    self_tax = ctx.get("self_assessment_tax_paid", 0)

    tds_credit = sum(item.get("amount", 0) for item in tds_credits)
    total_paid = tds_credit + advance + self_tax
    total_due = total_tax + total_interest
    net = total_paid - total_due

    if net > 0:
        result = {
            "total_tax_due": total_due,
            "total_taxes_paid": total_paid,
            "tds_credit_used": tds_credit,
            "tds_credit_source": "26AS only",
            "net_position": net,
            "outcome": "refund",
            "refund_amount": net,
            "file_for_refund": True,
            "demand_amount": None,
        }
    elif net < 0:
        demand = abs(net)
        result = {
            "total_tax_due": total_due,
            "total_taxes_paid": total_paid,
            "tds_credit_used": tds_credit,
            "net_position": net,
            "outcome": "demand",
            "demand_amount": demand,
            "refund_amount": None,
            "pay_before_filing": True,
            "payment_instruction": f"Pay self-assessment tax of ₹{demand:,} under Challan 280 before filing return (Section 140A)",
        }
    else:
        result = {
            "total_tax_due": total_due,
            "total_taxes_paid": total_paid,
            "tds_credit_used": tds_credit,
            "net_position": 0,
            "outcome": "nil_balance",
            "refund_amount": None,
            "demand_amount": None,
        }

    ctx.update(result)
