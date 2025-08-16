def compute_interaction_score(
    like: bool | int,
    watchtime: float,
    duration: float | None = None,
    dont_suggest: bool | int = False,
    comment: str | None = None,
    *,
    weights: dict | None = None,
    min_watch_ratio_for_full: float = 0.98
) -> float:
    """
    Compute an interaction score based on various factors.
    
    :param like: Whether the user liked the content (True/False or 1/0)
    :param watchtime: Time spent watching the content
    :param duration: Total duration of the content (optional)
    :param dont_suggest: Whether to not suggest this content again (True/False or 1/0)
    :param comment: User's comment on the content (optional)
    :param weights: Weights for each factor (optional)
    :param min_watch_ratio_for_full: Minimum watch ratio to consider full watch
    :return: Computed interaction score
    """
    # pesos por defecto
    if weights is None:
        weights = {
            "w_watch": 0.6,
            "like_bonus": 0.4,
            "comment_bonus": 0.05,
            "dont_penalty": -0.6
        }

    # normalizar inputs básicos
    like = bool(like)
    dont = bool(dont_suggest)
    has_comment = False #bool(comment) and str(comment).strip() != ""

    # calcular watch_ratio
    if duration and duration > 0:
        watch_ratio = float(watchtime) / float(duration)
    else:
        # fallback: si no hay duration, asumimos que watchtime ya está en ratio [0,1],
        # si es muy grande lo normalizamos por ejemplo a 1.0
        watch_ratio = float(watchtime)
        if watch_ratio > 1.0:
            # intentar asumir que watchtime está en segundos: escalamos con min cap
            # (esto es heurístico; preferible proporcionar duration)
            watch_ratio = min(1.0, watch_ratio / (watch_ratio + 60.0))  # suave fallback

    # clip y tratamiento near-full
    watch_ratio = max(0.0, min(1.0, watch_ratio))
    if watch_ratio >= min_watch_ratio_for_full:
        watch_ratio = 1.0

    # construir score
    score = weights["w_watch"] * watch_ratio
    if like:
        score += weights["like_bonus"]
    if has_comment:
        score += weights["comment_bonus"]
    if dont:
        score += weights["dont_penalty"]

    # recortar a [0,1]
    score = max(0.0, min(1.0, score))

    return float(score)