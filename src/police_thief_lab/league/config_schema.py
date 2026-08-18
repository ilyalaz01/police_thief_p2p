"""Exact Appendix-B field inventory, fixed values, and quantitative minima."""

TOP_LEVEL_FIELDS = {
    "schema_version",
    "agreed_between",
    "board_and_agents",
    "world",
    "movement_and_barriers",
    "scoring",
    "pheromones",
    "network_and_league",
    "rate_limiter_gatekeeper",
}
SECTION_FIELDS = {
    "board_and_agents": {
        "grid_size", "num_agents", "thief_start", "cop_start",
        "axis_origin_corner", "axis_start_index",
    },
    "world": {"map_area", "hint_max_words"},
    "movement_and_barriers": {
        "move_set", "max_barriers", "max_moves", "survival_threshold",
    },
    "scoring": {
        "capture_cop", "capture_thief", "survival_cop", "survival_thief",
        "tie_score", "technical_loss",
    },
    "pheromones": {
        "pheromone_center_intensity", "pheromone_decay", "pheromone_grid_size",
    },
    "network_and_league": {
        "response_timeout_sec", "watchdog_timeout_sec", "num_games",
        "diversity_reward", "min_games_to_pass", "max_games_per_team",
        "token_budget_per_series",
    },
    "rate_limiter_gatekeeper": {
        "requests_per_minute", "concurrent_requests", "retry_backoff_sec",
        "max_retries", "queue_depth",
    },
}
FIXED_VALUES = {
    ("board_and_agents", "grid_size"): 7,
    ("board_and_agents", "num_agents"): 2,
    ("board_and_agents", "thief_start"): [3, 3],
    ("board_and_agents", "cop_start"): [0, 0],
    ("board_and_agents", "axis_origin_corner"): "top-left",
    ("board_and_agents", "axis_start_index"): 0,
    ("world", "map_area"): "New York",
    ("world", "hint_max_words"): 15,
    ("movement_and_barriers", "move_set"): ["N", "S", "E", "W", "STAY"],
    ("movement_and_barriers", "max_barriers"): 14,
    ("movement_and_barriers", "max_moves"): 35,
    ("movement_and_barriers", "survival_threshold"): 35,
    ("scoring", "capture_cop"): 20,
    ("scoring", "capture_thief"): 5,
    ("scoring", "survival_cop"): 5,
    ("scoring", "survival_thief"): 10,
    ("scoring", "tie_score"): 2,
    ("scoring", "technical_loss"): 0,
    ("pheromones", "pheromone_center_intensity"): 0.9,
    ("pheromones", "pheromone_decay"): 0.10,
    ("pheromones", "pheromone_grid_size"): 5,
    ("network_and_league", "num_games"): 6,
    ("network_and_league", "diversity_reward"): 10,
    ("network_and_league", "min_games_to_pass"): 2,
    ("network_and_league", "max_games_per_team"): 10,
}
MINIMUM_VALUES = {
    "requests_per_minute": 30,
    "concurrent_requests": 2,
    "retry_backoff_sec": 5,
    "max_retries": 3,
    "queue_depth": 100,
}
