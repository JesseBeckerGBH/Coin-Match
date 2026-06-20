"""Research engine configuration constants."""

SCORING_WEIGHTS = {
    "relevance": 0.25, "novelty": 0.20, "data_readiness": 0.20,
    "benchmark_potential": 0.20, "explainability": 0.15,
}

PROMOTION_THRESHOLD = 0.78

BENCHMARK_METRICS = [
    "top1_accuracy", "top5_recall", "mean_reciprocal_rank",
    "expected_calibration_error", "manual_review_rate",
    "grade_mae", "valuation_mape", "krippendorff_alpha",
]

RESEARCH_TOPICS = [
    "coin identification", "feature matching", "metric learning",
    "image retrieval", "multimodal matching", "confidence calibration",
    "inter-rater reliability", "anomaly detection", "probabilistic ranking",
    "numismatic grading",
]

SOURCE_TRUST_RANKING = {
    "peer_reviewed_paper": 0.95, "survey_paper": 0.90,
    "benchmark_report": 0.85, "implementation_repo": 0.80,
    "technical_blog": 0.65, "general_blog": 0.40, "marketing_page": 0.10,
}
