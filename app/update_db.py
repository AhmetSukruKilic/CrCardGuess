from app.services.service_helper_card_funcs import create_sorted_cards
from app.auto_build.auto_build import register_new_cards
from app.api_funcs.api_leaderboards_funcs import get_top_players_at_season
from app.api_funcs.api_player_funcs import get_player_battlelog
from app.services.service_battle_funcs import (
    get_first_enemy_cards,
    get_first_teammate_cards,
    get_first_opponent_player,
    get_first_opponent_data,
    BATTLE_TYPE,
    BATTLE_TIME,
)
from app.db_methods.database import SessionLocal
from app.db_methods.models import Card, Deck, Player, Battle
from app.services.service_time_funcs import to_mysql_datetime
from app.api_funcs.api_config import health_check
from app.services.service_helper_player_funcs import new_player
from app.services.service_ui_funcs import print_status_bar


def update_database_1v1(players: list[Player]):

    if not health_check():
        return

    register_new_cards()

    with SessionLocal() as db:
        with db.begin():  # single commit at the end
            length = len(players)
            index = 0
            for player in players:
                index += 1
                # simple console progress bar
                print_status_bar(length, index)
                update_players(db, player)
                db.flush()  # ensure Player row exists

                match_history = get_player_battlelog(player.user_code)

                for match in match_history:
                    if match.get(BATTLE_TYPE) != "pathOfLegend":
                        continue

                    opponent_player = get_first_opponent_player(db, match)
                    if opponent_player is None:
                        opponent_player = new_player(get_first_opponent_data(match))
                    update_players(db, opponent_player)
                    db.flush()  # ensure Player row exists

                    deck1 = update_team_decks_1v1(db, player, match)
                    deck2 = update_opponent_decks_1v1(db, opponent_player, match)

                    update_match_history_1v1(
                        db, (player, deck1), (opponent_player, deck2), match
                    )

            db.commit()
            db.flush()
            db.expunge_all()
            db.close()


def update_players(db, player: Player):
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

    return player


def _ensure_card_ids(card_objs) -> list[int]:
    ids = []
    for c in card_objs:
        if hasattr(c, "card_id"):
            ids.append(int(c.card_id))
        elif isinstance(c, dict) and "card_id" in c:
            ids.append(int(c["card_id"]))
        else:
            raise TypeError(f"Cannot extract card_id from {c!r}")
    return ids


def update_team_decks_1v1(db, player: Player, match: dict):
    team_cards = get_first_teammate_cards(db, match)
    card_ids = _ensure_card_ids(team_cards)

    deck = save_deck(db, card_ids, player.user_code)

    return deck


def update_opponent_decks_1v1(db, opponent: Player, match: dict):
    opponent_cards = get_first_enemy_cards(db, match)
    sorted_cards = create_sorted_cards(db, opponent_cards)

    deck = save_deck(db, sorted_cards, opponent.user_code)

    return deck


def compute_signature(card_ids: list[int] | set[int]) -> str:
    return "-".join(str(int(i)) for i in sorted({int(x) for x in card_ids}))


def norm_tag(tag: str) -> str:
    tag = tag.strip()
    return tag if tag.startswith("#") else f"#{tag}"


def save_deck(db, cards: list[Card], player_code: str) -> Deck:
    player_code = norm_tag(player_code)

    sig = compute_signature(card.card_id for card in cards)

    deck = db.query(Deck).filter_by(signature=sig).first()
    if not deck:
        deck = Deck(signature=sig)
        db.add(deck)
        if len(cards) != 8:
            raise ValueError(f"Expected 8 cards, got {len(cards)}")
        deck.cards.extend(cards)
        db.flush()  # assigns deck.deck_id

    # link via relationship
    player = db.query(Player).filter_by(user_code=player_code).one_or_none()
    if not player:
        raise ValueError(f"Player {player_code} not found (FK would fail)")

    # idempotent append
    if deck not in player.decks:
        player.decks.append(deck)

    return deck


def update_match_history_1v1(
    db,
    player_and_deck_1: tuple[Player, Deck],
    player_and_deck_2: tuple[Player, Deck],
    match: dict,
):

    parsed_time = to_mysql_datetime(match[BATTLE_TIME])
    sorted_player_decks = sorted(
        [player_and_deck_1, player_and_deck_2], key=lambda p: p[0].user_code
    )

    first_player = sorted_player_decks[0][0]
    second_player = sorted_player_decks[1][0]
    first_deck = sorted_player_decks[0][1]
    second_deck = sorted_player_decks[1][1]

    existing_battle = (
        db.query(Battle)
        .filter(
            Battle.first_player_code == first_player.user_code,
            Battle.second_player_code == second_player.user_code,
            Battle.battle_time == parsed_time,
            Battle.first_deck_id == first_deck.deck_id,
            Battle.second_deck_id == second_deck.deck_id,
        )
        .first()
    )

    if not existing_battle:
        new_battle = Battle(
            first_player_code=first_player.user_code,
            second_player_code=second_player.user_code,
            first_deck_id=first_deck.deck_id,
            second_deck_id=second_deck.deck_id,
            battle_type=match[BATTLE_TYPE],
            battle_time=parsed_time,
            raw_data=match,
        )
        db.add(new_battle)


def main():
    top_players = get_top_players_at_season()
    players = []

    if not top_players:
        print("No top players found.")
        return

    for p in top_players:
        player = new_player(p)
        players.append(player)

    update_database_1v1(players)


if __name__ == "__main__":
    main()
