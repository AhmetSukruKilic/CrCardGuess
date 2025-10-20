def get_team_cards_from_battles(battle):
    members = battle.get("team") or []

    team_cards = {
        member.get("tag"): [] for member in members
    }  # assuming max 2 team members

    for i in range(0, len(members)):
        team_cards[members[i].get("tag")] = [
            c.get("name") for c in members[i].get("cards", [])
        ]
    return team_cards


def get_opponent_cards_from_battles(battle):
    opponents = battle.get("opponent") or []

    opponent_cards = {
        opponent.get("tag"): [] for opponent in opponents
    }  # assuming max 2 opponents

    for i in range(0, len(opponents)):
        opponent_cards[opponents[i].get("tag")] = [
            c.get("name") for c in opponents[i].get("cards", [])
        ]
    return opponent_cards
