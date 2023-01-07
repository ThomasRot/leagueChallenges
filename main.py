import requests
from functools import partial
from dotenv import load_dotenv
import os

# You'll need a file called '.env' next to this script containing the line 'RIOT_API=<RGAPI-...>'
load_dotenv()

RIOT_API = os.getenv("RIOT_API")
space = "                                                                                                   " \
        "                                                                                                   "

date = "2022-05-11"

anoname = "µ DerAnonym"
anonym = "THhs11o_qe2vjr8Wc7m_Lj7RLfvtlyal8WZrIRc3Y8A3jqpxCZq9KEucX6zGDw7j8ulKrPfc1vEMaw"


def summoner_by_name(name):
    return requests.get(
        f'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}?api_key={RIOT_API}'
    ).json()


def summoner_by_puuid(puid):
    return requests.get(
        f'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puid}?api_key={RIOT_API}'
    ).json()


def summoner_by_sumid(summonerid):
    return requests.get(
        f'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/{summonerid}?api_key={RIOT_API}'
    ).json()


def challenges_names():
    return requests.get(
        f'https://euw1.api.riotgames.com/lol/challenges/v1/challenges/config?api_key={RIOT_API}'
    ).json()


def challenges_for_player(puid):
    return requests.get(
        f'https://euw1.api.riotgames.com/lol/challenges/v1/player-data/{puid}?api_key={RIOT_API}'
    ).json()


def get_leaderboard(challenge_id):
    return requests.get(
        f'https://euw1.api.riotgames.com/lol/challenges/v1/challenges/{challenge_id}/leaderboards/by-level/CHALLENGER?api_key={RIOT_API}'
    ).json()


def iterate_pages_to_qualifying_date(puid, queue):
    result = []
    for page in range(100):
        matchIds = requests.get(
            f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puid}/ids?queue={queue}&startTime=1652227200&start={page * 100}&count=100&api_key=RGAPI-26025dcf-72e4-4657-9564-408f107c076d'
        ).json()
        result += matchIds
        if len(matchIds) < 100:
            return result
    raise Exception("Too many pages")


def get_5v5_match_history(puid):
    return sum([iterate_pages_to_qualifying_date(puid, q) for q in [400, 420, 430, 440]],
               [])  # Draft, SoloQ, Blind, FlexQ


def print_challenges_by_rarity(challenges, player):
    for c in player['challenges']:
        description = challenges[c['challengeId']]
        title = f'{description["name"]} [{description["shortDescription"]}]:'
        print(
            f'{title}{space[:130 - len(title)]} The Value of {c["value"]} puts {player["name"]} in the top'
            f' {c["percentile"] * 100:.1f}% of players.')


def main():
    all_players = [
        {'name': 'Minimary'},
        {'name': 'µ DerAnonym'},
        {'name': 'µ DerPhoenix'},
        {'name': '21 Tiramisu'},
        {'name': 'Simsa Lá Bim'},
        {'name': 'Ambiverted'},
        {'name': 'Asher2ashes'},
        {'name': 'RAD Svenjamin'},
        {'name': 'damdididum'},
        {'name': 'SuperEngel'},
    ]
    challenges = {ch["id"]: ch["localizedNames"]["en_US"] for ch in challenges_names()}
    for p in all_players:
        populate_player(p)

    # print_challenges_by_rarity(challenges, all_players[0])
    for c_id in challenges:
        sorted_players = sorted(all_players, key=lambda p: normalized_value(c_id, p), reverse=True)
        # partial(normalized_value, challenge_id=c_id)
        description = challenges[c_id]
        title = f'\"{description["name"]}\" [{description["shortDescription"]}] (normalized by SR games played):'
        print(f'For the Challenge {title}')
        for i, p in enumerate(sorted_players):
            p_c = p['current_challenge']
            if p_c:
                print(f'{i + 1}. {p["name"]} with an average of {p_c["normalized_value"]:.3f} points per game. '
                      f'The total value of'
                      f' {p_c["value"]} puts {p["name"]} in the top {p_c["percentile"] * 100:.1f}% of players.')
            else:
                print(f'{i + 1}. {p["name"]} without any progress on the challenge')
        print()


def normalized_value(challenge_id, player):
    player['current_challenge'] = next((c for c in player['challenges'] if c['challengeId'] == challenge_id), None)
    return player['current_challenge']['normalized_value'] if player['current_challenge'] is not None else 0


def populate_player(player):
    name = player['name']
    player['puid'] = puuid = summoner_by_name(name)['puuid']
    challenges = challenges_for_player(puuid)
    player['challenges'] = sorted(challenges['challenges'], key=lambda c: c['percentile'])
    player['history'] = get_5v5_match_history(puuid)
    for c in player['challenges']:
        c['normalized_value'] = c['value'] / len(player['history'])


if __name__ == '__main__':
    main()
