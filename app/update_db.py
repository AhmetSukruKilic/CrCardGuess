from app.helper_deck_funcs import get_player_decks
from database import SessionLocal
from app.models import Card, Deck, Player, Battle
from app.api_funcs.leaderboards_funcs import get_top_players_at_season
from app.api_funcs.player_funcs import get_player_battlelog
from app.helper_battle_funcs import (
    get_team_cards_from_battles,
    get_opponent_cards_from_battles,
)


def update_database_1v1(players: list[Player]):
    db = SessionLocal()
    for player in players:
        update_players(player)
        match_history = get_player_battlelog(player.user_code)
        for match in match_history:
            if match.get("battle_type") != "1v1":
                continue
            opponent = match.get("opponents", [])[0]
            opponent_player = (
                db.query(Player).filter(Player.user_code == opponent.get("tag")).first()
            )

            update_match_history_1v1(player, opponent_player, match)
            update_decks(player, match)
    db.close()


def update_players(player: Player):
    db = SessionLocal()
    existing_player = (
        db.query(Player).filter(Player.user_code == player.user_code).first()
    )
    if existing_player:
        existing_player.name = player.name
        existing_player.rank = player.rank
    else:
        new_player = Player(
            user_code=player.user_code, name=player.name, rank=player.rank
        )
        db.add(new_player)
    db.commit()
    db.close()

    return player


def update_decks(player: Player, opponent: Player, match: dict):
    db = SessionLocal()

    team_cards: list[Card] = get_team_cards_from_battles(match)[0]
    opponent_cards: list[Card] = get_opponent_cards_from_battles(match)[0]

    player_decks = get_player_decks(player)
    opponent_decks = get_player_decks(opponent)

    for existing_deck in player_decks:
        if existing_deck.cards == team_cards:
            break
    else:
        new_deck = Deck(
            player_code=player.user_code,
        )
        db.add(new_deck)

    for existing_deck in opponent_decks:
        if existing_deck.cards == opponent_cards:
            break
    else:
        new_deck = Deck(
            player_code=opponent.user_code,
        )
        db.add(new_deck)
    db.commit()
    db.close()


def update_match_history_1v1(player: Player, match: dict):
    db = SessionLocal()

    if match.get("battle_type") != "1v1":
        return

    existing_battle = (
        db.query(Battle)
        .filter(
            Battle.player_code == player.user_code,
            Battle.battle_time == match["battle_time"],
        )
        .first()
    )

    if not existing_battle:
        new_battle = Battle(
            player_code=player.user_code,
            battle_type=match["battle_type"],
            battle_time=match["battle_time"],
            raw_data=match,
        )
        db.add(new_battle)
    db.commit()
    db.close()
