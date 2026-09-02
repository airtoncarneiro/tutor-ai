from typing import Literal


class AcceptanceLearner:
    """Small deterministic scenario driver used to prove V1 path divergence."""

    def next_action(self, prerequisite_mastery: float) -> Literal["proceed_to_window_functions", "remediate_aggregation"]:
        return "proceed_to_window_functions" if prerequisite_mastery >= 0.8 else "remediate_aggregation"


def compare_prerequisite_paths() -> dict[str, str]:
    learner = AcceptanceLearner()
    return {"strong": learner.next_action(0.9), "weak": learner.next_action(0.2)}

