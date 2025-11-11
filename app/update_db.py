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
    is_winner_team,
)
from app.db.database import SessionLocal
from app.db.models import Card, Deck, Player, Battle
from app.services.service_helper_deck_funcs import compute_signature
from app.services.service_time_funcs import to_mysql_datetime
from app.api_funcs.api_config import health_check
from app.services.service_helper_player_funcs import new_player, norm_tag
from app.services.service_ui_funcs import print_status_bar
from app.db.models import DeckWinrate


from collections import defaultdict
from app.db.models import CardWinrate, DeckWinrate  # make sure these exist


def update_database_1v1(players: list[Player]):
    if not health_check():
        return

    register_new_cards()

    totals = {"new": 0, "existing": 0}
    deck_results: list[tuple[Deck, Deck]] = []
    card_counts: dict[int, list[int]] = defaultdict(
        lambda: [0, 0]
    )  # card_id -> [wins, losses]

    with SessionLocal() as db:
        with db.begin():
            length = len(players)
            index = -1
            for player in players:
                index += 1
                print_status_bar(length, index)

                update_players(db, player)
                db.flush()

                match_history = get_player_battlelog(player.user_code)

                for match in match_history:
                    if match.get(BATTLE_TYPE) != "pathOfLegend":
                        continue

                    opponent_player = get_first_opponent_player(db, match)
                    if opponent_player is None:
                        opponent_player = new_player(get_first_opponent_data(match))
                    update_players(db, opponent_player)
                    db.flush()

                    deck1 = update_team_decks_1v1(db, player, match)
                    deck2 = update_opponent_decks_1v1(db, opponent_player, match)

                    is_existing, winner_deck, loser_deck = update_match_history_1v1(
                        db, (player, deck1), (opponent_player, deck2), match
                    )

                    if is_existing:
                        totals["existing"] += 1
                        continue

                    totals["new"] += 1

                    # collect deck result
                    deck_results.append((winner_deck, loser_deck))

                    # collect per-card tallies
                    for c in winner_deck.cards:
                        card_counts[c.card_id][0] += 1  # win
                    for c in loser_deck.cards:
                        card_counts[c.card_id][1] += 1  # loss

            # single write phase
            update_deck_winrates(db, deck_results)
            update_card_winrates(db, card_counts)

            db.flush()
            db.expunge_all()

            index += 1
            print_status_bar(length, index)

            print(
                f"\n\ntotal_fights {totals['existing'] + totals['new']}"
                + f"| existing_fights {totals['existing']} | new_fights {totals['new']}"
            )


def update_deck_winrates(db, deck_results: list[tuple[Deck, Deck]]):
    if not deck_results:
        return
    # prefetch existing rows
    deck_ids = {d.deck_id for tup in deck_results for d in tup}
    existing = {
        r.deck_id: r
        for r in db.query(DeckWinrate).filter(DeckWinrate.deck_id.in_(deck_ids))
    }
    # ensure rows exist
    for did in deck_ids:
        if did not in existing:
            row = DeckWinrate(deck_id=did, wins=0, losses=0)
            db.add(row)
            existing[did] = row

    # increment
    for winner_deck, loser_deck in deck_results:
        existing[winner_deck.deck_id].wins = (
            existing[winner_deck.deck_id].wins or 0
        ) + 1
        existing[loser_deck.deck_id].losses = (
            existing[loser_deck.deck_id].losses or 0
        ) + 1


from app.db.models import CardWinrate


def update_card_winrates(db, card_counts: dict[int, list[int]]):
    if not card_counts:
        return

    card_ids = list(card_counts.keys())

    # 1) Prefetch existing rows once
    existing = {
        r.card_id: r
        for r in db.query(CardWinrate).filter(CardWinrate.card_id.in_(card_ids))
    }

    # 2) Create missing rows once
    to_create = []
    for cid in card_ids:
        if cid not in existing:
            row = CardWinrate(card_id=cid, wins=0, losses=0)
            db.add(row)
            existing[cid] = row
            to_create.append(cid)

    db.flush()

    # 3) Increment
    for cid, (wins_inc, losses_inc) in card_counts.items():
        row = existing[cid]
        row.wins = (row.wins or 0) + int(wins_inc)
        row.losses = (row.losses or 0) + int(losses_inc)


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


def update_team_decks_1v1(db, player: Player, match: dict):
    team_cards = get_first_teammate_cards(db, match)
    sorted_cards = create_sorted_cards(db, team_cards)

    deck = save_deck(db, sorted_cards, player.user_code)

    return deck


def update_opponent_decks_1v1(db, opponent: Player, match: dict):
    opponent_cards = get_first_enemy_cards(db, match)
    sorted_cards = create_sorted_cards(db, opponent_cards)

    deck = save_deck(db, sorted_cards, opponent.user_code)

    return deck


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
) -> tuple[bool, Deck | None, Deck | None]:

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

    if existing_battle:
        return True, None, None

    # ---- determine winner/loser ----
    # Replace these with your actual crown / winner fields
    is_won_team = is_winner_team(match)

    if is_won_team:
        winner_player, winner_deck = player_and_deck_1
        loser_player, loser_deck = player_and_deck_2
    else:
        winner_player, winner_deck = player_and_deck_2
        loser_player, loser_deck = player_and_deck_1

    new_battle = Battle(
        first_player_code=first_player.user_code,
        second_player_code=second_player.user_code,
        first_deck_id=first_deck.deck_id,
        second_deck_id=second_deck.deck_id,
        winner_player_code=winner_player.user_code,
        winner_deck_id=winner_deck.deck_id,
        battle_type=match[BATTLE_TYPE],
        battle_time=parsed_time,
    )
    db.add(new_battle)

    return False, winner_deck, loser_deck


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
