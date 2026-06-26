"""
DVF test suite — exercises Golden Masters, Differential, and Mutation runners.

Run: pytest test_dvf.py -v
"""

import pytest
from engine.specs import ALL_SPECS
from dvf.runners.golden import run_golden
from dvf.runners.differential import run_diff, run_golden_diff
from dvf.runners.mutation import run_all_mutations, MUTATIONS
from dvf.coverage import coverage_report
from dvf.generator.matrix import REQUIRED_COVERAGE, GM_COVERAGE_MAP
from dvf.generator.synthesizer import synthesize_input


# ── Golden Master Tests ────────────────────────────────────────────────────────

class TestGoldenMasters:
    def test_all_golden_masters_pass(self):
        results = run_golden()
        assert results, "No golden master cases found"
        failed = [r for r in results if not r.passed]
        msgs = []
        for r in failed:
            msgs.append(f"{r.case_id}: {r.mismatches}")
        assert not failed, f"Golden master failures:\n" + "\n".join(msgs)

    def test_golden_master_count(self):
        results = run_golden()
        assert len(results) >= 8, f"Expected at least 8 GMs, got {len(results)}"

    @pytest.mark.parametrize("gm_id", ["GM-0001", "GM-0002", "GM-0003", "GM-0004",
                                        "GM-0005", "GM-0006", "GM-0007", "GM-0008"])
    def test_individual_golden_master(self, gm_id):
        results = run_golden(gm_id=gm_id)
        assert len(results) == 1, f"Expected 1 result for {gm_id}, got {len(results)}"
        r = results[0]
        assert r.passed, f"{gm_id} failed: {r.mismatches}"

    def test_golden_masters_have_coverage_tags(self):
        results = run_golden()
        untagged = [r for r in results if not r.coverage_tags]
        assert not untagged, f"GMs without coverage tags: {[r.case_id for r in untagged]}"


# ── Differential Tests ─────────────────────────────────────────────────────────

class TestDifferential:
    def test_identity_diff_is_empty(self):
        """Same spec set vs itself should produce zero diffs across all GMs."""
        results = run_golden_diff(ALL_SPECS, ALL_SPECS)
        diffs = [r for r in results if r.has_diff]
        assert not diffs, (
            f"Identity diff produced changes: "
            + ", ".join(f"{r.case_id}: {list(r.changed_fields)}" for r in diffs)
        )

    def test_diff_structure(self):
        """DiffResult has the expected shape."""
        results = run_golden_diff(ALL_SPECS, ALL_SPECS)
        assert results
        for r in results:
            assert hasattr(r, "case_id")
            assert hasattr(r, "changed_fields")
            assert hasattr(r, "has_diff")
            assert isinstance(r.changed_fields, dict)

    def test_manual_diff_single_case(self):
        """Spot-check: run two identical spec sets on a GM-like evidence dict."""
        evidence = {
            "case_id": "manual_test",
            "taxpayer_name": "Test Taxpayer",
            "age_bracket": "general",
            "classified_income": {
                "head_1_salary": [{"source": "Form 16", "gross_salary": 1000000, "employer": "TestCo", "tan": "TEST1234A"}],
                "head_2_house_property": [],
                "head_3_business": [],
                "head_4_capital_gains": [],
                "head_5_other_sources": [],
            },
            "evidence_integrity_checks_passed": True,
            "income_classification_complete": True,
            "tds_credits_from_26AS": [{"tan": "TEST1234A", "section": "192", "amount": 85000, "employer": "TestCo"}],
            "advance_tax_paid": 0,
            "self_assessment_tax_paid": 0,
            "regime_chosen": "new_regime",
            "return_filed_date": "2025-07-15",
            "due_date": "2025-07-31",
            "income_type": "salary_only",
        }
        result = run_diff(evidence, ALL_SPECS, ALL_SPECS, case_id="manual_test")
        assert not result.has_diff
        assert result.case_id == "manual_test"


# ── Mutation Tests ─────────────────────────────────────────────────────────────

class TestMutation:
    def test_all_mutations_are_effective(self):
        """Every mutation must be detected by at least one golden master."""
        results = run_all_mutations()
        ineffective = [r for r in results if not r.effective]
        assert not ineffective, (
            "Mutations not detected (blind spots):\n"
            + "\n".join(
                f"  {r.mutation_name}: should affect {next(m.should_affect for m in MUTATIONS if m.name == r.mutation_name)}"
                for r in ineffective
            )
        )

    def test_no_missed_cases(self):
        """Every GM listed in should_affect must actually detect the mutation."""
        results = run_all_mutations()
        missed = [(r.mutation_name, r.cases_missed) for r in results if r.cases_missed]
        assert not missed, (
            "GMs that should have caught mutations but didn't:\n"
            + "\n".join(f"  {name}: missed {cases}" for name, cases in missed)
        )

    @pytest.mark.parametrize("mut", MUTATIONS, ids=[m.name for m in MUTATIONS])
    def test_mutation_effective(self, mut):
        from dvf.runners.mutation import run_mutation
        result = run_mutation(mut)
        assert result.effective, (
            f"Mutation '{mut.name}' not detected by any golden master. "
            f"Expected to affect: {mut.should_affect}"
        )


# ── Coverage Tests ─────────────────────────────────────────────────────────────

class TestCoverage:
    def test_coverage_report_structure(self):
        report = coverage_report()
        assert "overall" in report
        assert "by_dimension" in report
        assert "covered_cells" in report
        assert "pending_cells" in report
        assert "gm_ids" in report

    def test_known_gms_are_covered(self):
        report = coverage_report()
        gm_ids = set(report["gm_ids"].keys())
        assert {"GM-0001", "GM-0002", "GM-0003", "GM-0004"} <= gm_ids

    def test_overall_coverage_at_least_40_pct(self):
        report = coverage_report()
        assert report["overall"]["pct"] >= 40, (
            f"Coverage dropped below 40%: {report['overall']}"
        )

    def test_coverage_totals_match_required_coverage(self):
        report = coverage_report()
        ov = report["overall"]
        assert ov["total"] == len(REQUIRED_COVERAGE)
        # covered = unique required cells that have a GM (may be < total GMs due to multiple GMs per cell)
        assert ov["covered"] == len(GM_COVERAGE_MAP)

    def test_pending_cells_plus_covered_equals_total(self):
        report = coverage_report()
        total = len(report["covered_cells"]) + len(report["pending_cells"])
        assert total == report["overall"]["total"]


# ── Synthesizer Tests ──────────────────────────────────────────────────────────

class TestSynthesizer:
    def test_synthesize_salary_case(self):
        from dvf.generator.matrix import MatrixCell
        cell = MatrixCell("salary_only", "general", "7L_to_12L", "new_regime", "none", "on_time")
        case = synthesize_input(cell, seq=1)
        assert "case_id" in case
        assert "taxpayer" in case
        assert "evidence" in case
        ev = case["evidence"]
        assert "gross_salary" in ev
        assert ev["regime_chosen"] == "new_regime"

    def test_synthesize_business_case(self):
        from dvf.generator.matrix import MatrixCell
        cell = MatrixCell("business_only", "general", "above_12L_to_15L", "new_regime", "none", "on_time")
        case = synthesize_input(cell, seq=2)
        ev = case["evidence"]
        assert "business_income" in ev
        assert ev["tds_section"] == "194J"

    def test_synthesize_with_ltcg(self):
        from dvf.generator.matrix import MatrixCell
        cell = MatrixCell("salary_ltcg", "general", "above_12L_to_15L", "new_regime", "ltcg_112A", "on_time")
        case = synthesize_input(cell, seq=3)
        ev = case["evidence"]
        assert "ltcg_112A" in ev

    def test_synthesize_senior(self):
        from dvf.generator.matrix import MatrixCell
        cell = MatrixCell("salary_only", "super_senior", "below_5L", "new_regime", "none", "on_time")
        case = synthesize_input(cell, seq=4)
        assert case["taxpayer"]["age"] == 82
        assert case["taxpayer"]["age_bracket"] == "super_senior"

    def test_all_required_cells_synthesizable(self):
        """Every pending cell can be synthesized without error."""
        from dvf.coverage import coverage_report
        report = coverage_report()
        for i, cell in enumerate(report["pending_cells"]):
            case = synthesize_input(cell, seq=100 + i)
            assert "evidence" in case, f"Synthesis failed for {cell}"
