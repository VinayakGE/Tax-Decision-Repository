"""
Rule Spec registry for the Wave 3A Tax Computation Engine.
Each spec declares requires/produces so the scheduler can build the dependency graph.
"""

from engine.scheduler import RuleSpec
from engine.rules.wave3a import (
    r0015_taxable_income_assembly,
    r0016_slab_engine_old_regime,
    r0017_slab_engine_new_regime,
    r0018_regime_comparator,
    r0019_section_87a_rebate,
    r0020_health_education_cess,
    r0021_surcharge,
    r0022_interest_234abc,
    r0023_refund_vs_demand,
)

WAVE3A_SPECS = [
    RuleSpec(
        rule_id="R-0015",
        requires=["classified_income", "evidence_integrity_checks_passed"],
        produces=["taxable_income_new_regime", "taxable_income_old_regime", "gross_total_income", "total_income"],
        fn=r0015_taxable_income_assembly,
    ),
    RuleSpec(
        rule_id="R-0016",
        requires=["taxable_income_old_regime"],
        produces=["slab_tax_old_regime", "total_before_rebate_old_regime"],
        fn=r0016_slab_engine_old_regime,
    ),
    RuleSpec(
        rule_id="R-0017",
        requires=["taxable_income_new_regime"],
        produces=["slab_tax_new_regime", "total_before_rebate_new_regime"],
        fn=r0017_slab_engine_new_regime,
    ),
    RuleSpec(
        rule_id="R-0019",
        requires=["total_income", "slab_tax_new_regime", "slab_tax_old_regime"],
        produces=["tax_after_rebate_new_regime", "tax_after_rebate_old_regime", "rebate_applied"],
        fn=r0019_section_87a_rebate,
    ),
    RuleSpec(
        rule_id="R-0021",
        requires=["total_income", "tax_after_rebate_new_regime", "tax_after_rebate_old_regime"],
        produces=["surcharge_new_regime", "surcharge_old_regime", "surcharge_amount"],
        fn=r0021_surcharge,
    ),
    RuleSpec(
        rule_id="R-0020",
        requires=["tax_after_rebate_new_regime", "surcharge_new_regime",
                  "tax_after_rebate_old_regime", "surcharge_old_regime"],
        produces=["total_tax_new_regime", "total_tax_old_regime", "cess_new_regime", "cess_old_regime"],
        fn=r0020_health_education_cess,
    ),
    RuleSpec(
        rule_id="R-0018",
        requires=["total_tax_new_regime", "total_tax_old_regime"],
        produces=["regime_recommendation", "tax_saving_amount", "new_regime_is_better"],
        fn=r0018_regime_comparator,
    ),
    RuleSpec(
        rule_id="R-0022",
        requires=["total_tax_new_regime", "return_filed_date"],
        produces=["total_interest", "interest_234A", "interest_234B", "interest_234C"],
        fn=r0022_interest_234abc,
    ),
    RuleSpec(
        rule_id="R-0023",
        requires=["total_tax_new_regime", "total_interest", "tds_credits_from_26AS"],
        produces=["outcome", "refund_amount", "demand_amount"],
        fn=r0023_refund_vs_demand,
    ),
]
