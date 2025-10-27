from app.helper_card_funcs import create_deck


def get_team_cards_from_battles(battle):
    members = battle.get("team") or []

    player0 = [c.get("name") for c in members[0].get("cards", [])]
    player1 = [c.get("name") for c in members[1].get("cards", [])]

    return create_deck(player0), create_deck(player1)


def get_opponent_cards_from_battles(battle):
    members = battle.get("opponents") or []

    player0 = [c.get("name") for c in members[0].get("cards", [])]
    player1 = [c.get("name") for c in members[1].get("cards", [])]
    return create_deck(player0), create_deck(player1)
