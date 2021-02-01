from riotwatcher import LolWatcher, ApiError
import pandas as pd
import numpy as np
import pprint

pd.set_option('display.max_columns', None)


#define as static variables for now, must be updated via form info
api_key = ''
watcher = LolWatcher(api_key)
region = 'na1'
name = 'Divine Right'
champion_id = 81 #currently dont see how this will be useful but ok


class user_info:
    """
    Returns df of user info from your last match (so far).
    """

    #define private variables to use in class
    user = watcher.summoner.by_name(region, name)

    def __init__(self, api_key, region, name, champion_id, gamemode):
        self.api_key = api_key
        self.region = region
        self.champion_id = champion_id
        self.gamemode = gamemode

    def rank_stats(self):
        #league, division, games played, etc.
        encrypted_summoner_id = user['id']
        self.rank_stats = watcher.league.by_summoner(region, self.user['id'])
        return self.rank_stats

    def match_data(self):
        #matches, last match, etc.
        self.matches = watcher.match.matchlist_by_account(region, self.user['accountId'])
#         for i in range(0,len(self.matches['matches'])):
#             lane = self.matches['matches'][i]['lane']
#             this_match = self.matches['matches'][i]
#             this_gamemode = watcher.match.by_id(region, this_match['gameId'])['gameMode']
#             if this_gamemode == self.gamemode:
#                 print(this_gamemode)
#                 self.last_match = self.matches['matches'][i]
        self.last_match = self.matches['matches'][0]

       # self.last_match = self.matches['matches'][0]
        self.last_match_data = watcher.match.by_id(region, self.last_match['gameId'])

        m = self.last_match_data
        #pprint.pprint(m)

        #n is for each "participant" or player in the match
        def gd():
            n = [] #dump raw stats into here
            for row in m['participants']:
                m_row = {}
                m_row['champion'] = row['championId']
                m_row['spell1'] = row['spell1Id']
                m_row['spell2'] = row['spell2Id']
                m_row['teamId'] = row['teamId']
                m_row['win'] = row['stats']['win']
                m_row['kills'] = row['stats']['kills']
                m_row['deaths'] = row['stats']['deaths']
                m_row['assists'] = row['stats']['assists']
                m_row['totalDamageDealt'] = row['stats']['totalDamageDealt']
                m_row['goldEarned'] = row['stats']['goldEarned']
                m_row['champLevel'] = row['stats']['champLevel']
                m_row['totalMinionsKilled'] = row['stats']['totalMinionsKilled']
                m_row['item0'] = row['stats']['item0']
                m_row['item1'] = row['stats']['item1']
                m_row['item2'] = row['stats']['item2']
                m_row['item3'] = row['stats']['item3']
                m_row['item4'] = row['stats']['item4']
                m_row['item5'] = row['stats']['item5']
                m_row['item6'] = row['stats']['item6']
                n.append(m_row)
            return n

        n = gd()

        pprint.pprint(m)

        for i in range(0,len(n)):
            n[i]['summonerName'] = m['participantIdentities'][i]['player']['summonerName']
            n[i]['profileIcon'] = m['participantIdentities'][i]['player']['profileIcon']

        latest = watcher.data_dragon.versions_for_region(region)['n']['champion']
        static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')

        # champ static list data to dict for looking up
        def g_c(n):

            champ_dict = {}
            for key in static_champ_list['data']:
                row = static_champ_list['data'][key]
                champ_dict[row['key']] = row['id']
            for row in n:
                #print(str(row['champion']) + ' ' + champ_dict[str(row['champion'])])
                row['championName'] = champ_dict[str(row['champion'])]

            df = pd.DataFrame(n)
            return df

        df = g_c(n)

        #add in extra columns
        df['gameDuration'] = m['gameDuration'] / 60
        df['gameMode'] = m['gameMode']
        df['kda'] = ((df['kills'] + df['assists']) / df['deaths']).round(2)
        df['killParticipation'] = (df['kills'] / df.groupby('teamId')['kills'].transform(np.sum) * 100).astype(int)
        return df


user_1 = user_info(api_key, name, region, champion_id, gamemode)
