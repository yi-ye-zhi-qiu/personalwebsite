from riotwatcher import LolWatcher, ApiError
import pandas as pd
import numpy as np
import pprint

pd.set_option('display.max_columns', None)

#define as static variables for now, must be updated via form info
api_key = ''
watcher = LolWatcher(api_key)
region = 'na1'
gamemode = 'CLASSIC'
name = 'Divine Right'
champion_id = 81 #currently dont see how this will be useful but ok

class game_info_by_summoner_name():
    """
    Returns df of user info from a given match (so far).
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
        self.matches = watcher.match.matchlist_by_account(region, self.user['accountId'])

        self.last_match = self.matches['matches'][0]

       # self.last_match = self.matches['matches'][0]
        self.last_match_data = watcher.match.by_id(region, self.last_match['gameId'])

        m = self.last_match_data
        #pprint.pprint(m)

        #n is for each "participant" or player in the match
        def gd():
            n = [] #dump raw stats into here from participants
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
                m_row['totalDamageDealtToChampions'] = row['stats']['totalDamageDealtToChampions']
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
                m_row['firstBloodKill'] = row['stats']['firstBloodKill']
                m_row['firstBloodAssist'] = row['stats']['firstBloodAssist']
                m_row['visionWardsBoughtInGame'] = row['stats']['visionWardsBoughtInGame']
                m_row['visionScore'] = row['stats']['visionScore']
                m_row['creepsPerMinDeltas'] = row['timeline']['creepsPerMinDeltas']
                #m_row['csDiffPerMinDeltas'] = row['timeline']['csDiffPerMinDeltas']
                m_row['goldPerMinDeltas'] = row['timeline']['goldPerMinDeltas']
                m_row['lane'] = row['timeline']['lane']
                m_row['ccScore'] = row['stats']['totalTimeCrowdControlDealt']
                m_row['perkPrimaryStyle'] = row['stats']['perkPrimaryStyle']
                m_row['perkSubStyle'] = row['stats']['perkSubStyle']
                n.append(m_row)
            return n

        n = gd()
        for i in range(0,len(n)):
            n[i]['summonerName'] = m['participantIdentities'][i]['player']['summonerName']
            n[i]['profileIcon'] = m['participantIdentities'][i]['player']['profileIcon']

        latest = watcher.data_dragon.versions_for_region(region)['n']['champion']
        static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')
        static_item_list = watcher.data_dragon.items(latest, 'en_US')
        static_summonerspell_list = watcher.data_dragon.summoner_spells(latest, 'en_US')

        def g_c(n): #gets summoner spells, champions, and items

            #summoner spells
            spell_url = "http://ddragon.leagueoflegends.com/cdn/11.2.1/img/spell/"

            summonerspell_dict = {}
            for key in static_summonerspell_list['data']:
                row = static_summonerspell_list['data'][key]
                summonerspell_dict[row['key']] = row['id']
                summonerspell_dict[row['key']] = spell_url + str(row['image']['full'])

            #champs
            champ_url = "https://ddragon.leagueoflegends.com/cdn/11.2.1/img/champion/"

            champ_name_dict = {}
            champ_image_dict = {}
            for key in static_champ_list['data']:
                row = static_champ_list['data'][key]
                champ_name_dict[row['key']] = row['id']
               # champ_dict[row['image']] = champ_url + str(row['image']['full'])
                champ_image_dict[row['key']] = champ_url +  str(row['image']['full'])

            #items
            item_url = "https://ddragon.leagueoflegends.com/cdn/11.2.1/img/item/"

            item_dict = {}

            for key in static_item_list['data']:
                row = static_item_list['data'][key]
                item_dict[key] = row['name']
            #add to df
            for row in n:
                #print(str(row['item1']) + ' ' + item_dict[str(row['item1'])])
                row['championName'] = champ_name_dict[str(row['champion'])]
                row['championImage'] = champ_image_dict[str(row['champion'])]
                for i in range(0,7):
                    try:
                        row['itemName' +str(i)] = item_dict[str(row['item'+str(i)])]
                        row['itemImage' + str(i)] = item_url + str(row['item'+str(i)]) + '.png'
                    except:
                        row['itemName' +str(i)] = 0
                row['spell1Image'] = summonerspell_dict[str(row['spell1'])]
                row['spell2Image'] = summonerspell_dict[str(row['spell2'])]

                row['profileIconImage'] = 'http://ddragon.leagueoflegends.com/cdn/11.2.1/img/profileicon/' + str(row['profileIcon']) + '.png'

            df = pd.DataFrame(n)
            return df

        df = g_c(n)

        #add in extra columns
        df['gameDuration'] = m['gameDuration'] / 60
        df['gameMode'] = m['gameMode']
        df['gameCreation'] = m['gameCreation']
        df['kda'] = ((df['kills'] + df['assists']) / df['deaths']).round(2)
        df['killParticipation'] = ((df['kills'] + df['assists'])/ df.groupby('teamId')['kills'].transform(np.sum) * 100).astype(int)
        df['minionsKilledPerMinute'] = (df['totalMinionsKilled'] / df['gameDuration']).round(1)

        def g_t(df, m):
            def x(y):
                m_id = m['teams'][0]['teamId']
                m_team = m['teams'][0]
                return np.where(df['teamId']==m_id, m_team[y], m['teams'][0+1][y])
            l = ['firstBlood', 'baronKills', 'firstTower', 'firstRiftHerald', 'towerKills',
                 'inhibitorKills', 'dragonKills','riftHeraldKills']
            for i in l:
                df[i] = x(i)
            return df

        df = g_t(df, m)

        return df, m
