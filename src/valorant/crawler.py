from database import sql_statements as db
import valorant



def main():
    ''' 
    Go through all players in the DB and get their matches ID's.
    '''
    for player in db.get_all_players():
        player_matches = valorant.get_matches_json_by_puuid(player.puuid)
        for match in valorant.get_match_ids(player_matches):
            print(f'{player.username}#{player.tagline} played match with ID {match}')



if __name__ == '__main__':
    main()
