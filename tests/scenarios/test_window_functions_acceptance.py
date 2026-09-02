from app.learning.acceptance import compare_prerequisite_paths


def test_strong_and_weak_learners_follow_different_paths():
    paths = compare_prerequisite_paths()
    assert paths["strong"] == "proceed_to_window_functions"
    assert paths["weak"] == "remediate_aggregation"
    assert paths["strong"] != paths["weak"]

