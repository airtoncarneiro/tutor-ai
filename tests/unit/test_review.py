from app.learning.review import ReviewService


def test_review_prioritizes_low_mastery():
    concepts = [{"concept_key": "x", "mastery": .8}, {"concept_key": "y", "mastery": .2}]
    assert ReviewService().review_concepts(concepts)[0]["concept_key"] == "y"


def test_transfer_changes_context_without_solution():
    service = ReviewService()
    apply = service.create_apply_problem("Window Functions")
    transfer = service.create_transfer_test(apply)
    assert transfer.context != apply.context
    assert apply.solution is None
    assert transfer.concepts == apply.concepts

