from report_conversation_eval import score, paired, percentile


def row(case, expected, predicted, repetition=0, status="idle"):
    return dict(case_id=case, expected=expected, classification=predicted, repetition=repetition,
                status=status, wall_s=2, calls=[])


def test_uncertainty_is_valid_only_for_unknown_ground_truth():
    result = score([row('a','INCERTO','INCERTO'), row('b','EMERGENCIA','INCERTO'),
                    row('c','NAO_EMERGENCIA','NAO_EMERGENCIA')])
    assert result['accuracy'] == 2/3
    assert result['emergency_to_uncertain'] == 1
    assert result['emergency_to_non_emergency'] == 0
    assert result['binary_coverage'] == 1/3


def test_failed_call_cannot_reuse_previous_correct_classification():
    result = score([row('a','EMERGENCIA','EMERGENCIA',status='failed')])
    assert result['accuracy'] == 0
    assert result['confusion_matrix']['EMERGENCIA']['ERROR'] == 1


def test_repetitions_are_bootstrapped_as_case_clusters():
    before=[row('a','EMERGENCIA','INCERTO',i) for i in range(2)]
    after=[row('a','EMERGENCIA','EMERGENCIA',i) for i in range(2)]
    result=paired(before,after)
    assert result['paired_predictions'] == 2
    assert result['independent_case_clusters'] == 1
    assert result['cluster_bootstrap_ci95'] == [1,1]
    assert percentile([1,2,3],.5) == 2


def test_exploratory_rechecks_do_not_inflate_main_form_sample():
    from report_conversation_eval import summarize
    records = []
    for phase in ('finish', 'recheck'):
        for arm, predicted in [('after_form', 'EMERGENCIA'), ('after_same_text', 'INCERTO')]:
            records.append(row('c03', 'EMERGENCIA', predicted) | {'kind': 'turn', 'phase': phase, 'arm': arm})
    result = summarize(records)
    assert result['dialogs']['after_form']['n'] == 1
    assert result['dialogs']['after_same_text']['n'] == 1
    assert result['form_vs_identical_text']['paired_predictions'] == 1
    assert result['exploratory_recheck']['after_form']['n'] == 1


def test_legacy_recheck_does_not_change_primary_sample():
    from report_conversation_eval import summarize
    records = [row('c03', 'EMERGENCIA', 'EMERGENCIA') |
               {'kind': 'turn', 'phase': 'legacy_recheck', 'arm': arm}
               for arm in ('after_form', 'after_same_text')]
    result = summarize(records)
    assert result['legacy_recheck']['after_form']['n'] == 1
    assert result['legacy_recheck']['after_same_text']['accuracy'] == 1
    assert result['dialogs'] == {}
    assert result['form_vs_identical_text']['paired_predictions'] == 0
