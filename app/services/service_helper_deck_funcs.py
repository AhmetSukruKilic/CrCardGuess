def compute_signature(card_ids: list[int] | set[int]) -> str:
    return "-".join(str(int(i)) for i in sorted({int(x) for x in card_ids}))
