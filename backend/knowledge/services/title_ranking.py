"""按标题和问题的字面重叠做粗排。空标题直接跳过，避免排序时缺少分数。"""


def rough_rank_metadata(user_query, mds_metadata, limit=50, word_weight=0.7, cut_words=None):
    if not user_query or not mds_metadata:
        return []
    if cut_words is None:
        import jieba
        cut_words = jieba.lcut

    ranked = []
    for md_metadata in mds_metadata:
        title = md_metadata.get("title") if isinstance(md_metadata, dict) else None
        if not isinstance(title, str) or not title.strip():
            continue
        user_chars = set(user_query)
        title_chars = set(title)
        unique_chars = user_chars | title_chars
        char_score = len(user_chars & title_chars) / len(unique_chars) if unique_chars else 0

        user_words = set(cut_words(user_query))
        title_words = set(cut_words(title))
        unique_words = user_words | title_words
        word_score = len(user_words & title_words) / len(unique_words) if unique_words else 0

        md_metadata["roughing_score"] = float(word_score * word_weight + char_score * (1 - word_weight))
        ranked.append(md_metadata)

    return sorted(ranked, key=lambda item: item["roughing_score"], reverse=True)[:limit]
