import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment


header_mapping_en = {
    "Player": "Player",
    "Pos": "Position",
    "Squad": "Team",
    "Age": "Age",
    "MP": "Matches Played",
    "Starts": "Starts",
    "Min": "Minutes Played",
    "Gls": "Goals",
    "Ast": "Assists",
    "G+A": "Goals + Assists",
    "G-PK": "Goals without Penalties",
    "PK": "Penalties Scored",
    "PKatt": "Penalty Attempts",
    "CrdY": "Yellow Cards",
    "CrdR": "Red Cards",
    "xG": "Expected Goals",
    "npxG": "Expected Goals (non-penalty)",
    "xAG": "Expected Assists",
    "npxG+xAG": "Expected Goals + Expected Assists (non-penalty)",
    "PrgC": "Progressive Carries",
    "PrgP": "Progressive Passes",
    "PrgR": "Progressive Receptions",
    "G+A-PK": "Goals + Assists without Penalties",
    "xG+xAG": "Expected Goals + Expected Assists",
    "Matches": "Matches",
    "SCA": "Shot-Creating Actions",
    "SCA90": "Shot-Creating Actions per 90 Minutes",
    "PassLive": "Live Ball Passes",
    "PassDead": "Dead Ball Passes",
    "TO": "Turnovers",
    "Sh": "Shots",
    "Fld": "Fouls Drawn",
    "Def": "Defensive Actions",
    "GCA": "Goal-Creating Actions",
    "GCA90": "Goal-Creating Actions per 90 Minutes",
    "SoT": "Shots on Target",
    "SoT%": "Percentage of Shots on Target",
    "Sh/90": "Shots per 90 Minutes",
    "SoT/90": "Shots on Target per 90 Minutes",
    "G/Sh": "Goals per Shot",
    "G/SoT": "Goals per Shot on Target",
    "Dist": "Shot Distance",
    "FK": "Free Kicks",
    "npxG/Sh": "Expected Goals per Shot (non-penalty)",
    "G-xG": "Difference between Goals and Expected Goals",
    "np:G-xG": "Difference between Non-Penalty Goals and Expected Goals",
    "Cmp": "Completed Passes",
    "Att": "Pass Attempts",
    "Cmp%": "Pass Completion (%)",
    "TotDist": "Total Passing Distance",
    "PrgDist": "Progressive Passing Distance",
    "xA": "Expected Assists",
    "A-xAG": "Difference between Assists and Expected Assists",
    "KP": "Key Passes",
    "1/3": "Passes into Final Third",
    "PPA": "Passes into Penalty Area",
    "CrsPA": "Crosses into Penalty Area",
    'Tkl': 'Tackles',
    'TklW': 'Tackles Won',
    'Def 3rd': 'Tackles (Defensive Third)',
    'Mid 3rd': 'Tackles (Middle Third)',
    'Att 3rd': 'Tackles (Attacking Third)',
    'Att': 'Attempts',
    'Tkl%': 'Tackles Success Percentage',
    'Lost': 'Challenges Lost',
    'Blocks': 'Blocks',
    'Sh': 'Shots Blocked',
    'Pass': 'Passes Blocked',
    'Int': 'Interceptions',
    'Tkl+Int': 'Tackles and Interceptions',
    'Clr': 'Clearances',
    'Err': 'Errors Leading to Goals'
}

def createPlayerDatabase():
    url = 'https://fbref.com/en/comps/9/stats/Premier-League-Stats'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    table = BeautifulSoup(soup.select_one('#all_stats_standard').find_next(text=lambda x: isinstance(x, Comment)), 'html.parser')
   
    url2 = 'https://fbref.com/en/comps/9/gca/Premier-League-Stats'
    soup2 = BeautifulSoup(requests.get(url2).content, 'html.parser')
    table2 = BeautifulSoup(soup2.select_one('#all_stats_gca').find_next(text=lambda x: isinstance(x, Comment)), 'html.parser')

    url3 = 'https://fbref.com/en/comps/9/shooting/Premier-League-Stats'
    soup3 = BeautifulSoup(requests.get(url3).content, 'html.parser')
    table3 = BeautifulSoup(soup3.select_one('#all_stats_shooting').find_next(text=lambda x: isinstance(x, Comment)), 'html.parser')
    
    url4 = 'https://fbref.com/en/comps/9/passing/Premier-League-Stats'
    soup4 = BeautifulSoup(requests.get(url4).content, 'html.parser')
    table4 = BeautifulSoup(soup4.select_one('#all_stats_passing').find_next(text=lambda x: isinstance(x, Comment)), 'html.parser')

    url5 = 'https://fbref.com/en/comps/9/defense/Premier-League-Stats'
    soup5 = BeautifulSoup(requests.get(url5).content, 'html.parser')
    table5 = BeautifulSoup(soup5.select_one('#all_stats_defense').find_next(text=lambda x: isinstance(x, Comment)), 'html.parser')


    tds=[]
    thx = [th.get_text(strip=True) for th in table.select('tr:has(th)')[1].select('th')]
    for tr in table.select('tr:has(td)'):
        tdx = [td.get_text(strip=True) for td in tr.select('td')]
        tds.append(tdx)
        #print('{:<30}{:<20}{:<10}'.format(tds[0], tds[3], tds[5]))
    tds2=[]
    thx2 = [th.get_text(strip=True) for th in table2.select('tr:has(th)')[1].select('th')]
    for tr in table2.select('tr:has(td)'):
        tdx = [td.get_text(strip=True) for td in tr.select('td')]
        tds2.append(tdx)
        #print('{:<30}{:<20}{:<10}'.format(tds[0], tds[3], tds[5]))
    tds3=[]
    thx3 = [th.get_text(strip=True) for th in table3.select('tr:has(th)')[1].select('th')]
    for tr in table3.select('tr:has(td)'):
        tdx = [td.get_text(strip=True) for td in tr.select('td')]
        tds3.append(tdx)
        #print('{:<30}{:<20}{:<10}'.format(tds[0], tds[3], tds[5]))
    tds4=[]
    thx4 = [th.get_text(strip=True) for th in table4.select('tr:has(th)')[1].select('th')]
    for tr in table4.select('tr:has(td)'):
        tdx = [td.get_text(strip=True) for td in tr.select('td')]
        tds4.append(tdx)
        #print('{:<30}{:<20}{:<10}'.format(tds[0], tds[3], tds[5]))
    tds5=[]
    thx5 = [th.get_text(strip=True) for th in table5.select('tr:has(th)')[1].select('th')]
    for tr in table5.select('tr:has(td)'):
        tdx = [td.get_text(strip=True) for td in tr.select('td')]
        tds5.append(tdx)
        #print('{:<30}{:<20}{:<10}'.format(tds[0], tds[3], tds[5]))

    df = pd.DataFrame(tds,columns=list(thx[1:]))
    df2 = pd.DataFrame(tds2,columns=list(thx2[1:]))
    df3 = pd.DataFrame(tds3,columns=list(thx3[1:]))
    df4 = pd.DataFrame(tds4,columns=list(thx4[1:]))
    df5 = pd.DataFrame(tds5,columns=list(thx5[1:]))

    df['Min'] = df['Min'].str.replace(',', '').astype(float)

    main_df = pd.merge(df, df2, on=['Player','Nation','Pos','Squad','Age','Born','90s'],copy=False,suffixes=('', '_y'))
    main_df.drop(main_df.filter(regex='_y$').columns, axis=1, inplace=True)
    main_df = pd.merge(main_df,df3, on=['Player','Nation','Pos','Squad','Age','Born','90s'],copy=False,suffixes=('', '_y'))
    main_df.drop(main_df.filter(regex='_y$').columns, axis=1, inplace=True)
    main_df = pd.merge(main_df,df4, on=['Player','Nation','Pos','Squad','Age','Born','90s'],copy=False,suffixes=('', '_y'))
    main_df.drop(main_df.filter(regex='_y$').columns, axis=1, inplace=True)
    main_df = pd.merge(main_df,df5, on=['Player','Nation','Pos','Squad','Age','Born','90s'],copy=False,suffixes=('', '_y'))
    main_df.drop(main_df.filter(regex='_y$').columns, axis=1, inplace=True)
    main_df = main_df.drop(["Nation","Born","90s","Matches"],axis=1)



    main_df = main_df.rename(columns=dict(header_mapping_en))
    main_df = main_df.loc[:,~main_df.columns.duplicated()].copy()
    main_df[main_df.columns[5:]]=main_df[main_df.columns[5:]].apply(pd.to_numeric, axis=1)

    return main_df

def createTeamDatabase():
    
    shooting_mapping = {
    'Squad': 'Squad',
    '# Pl': 'Number of players',
    '90s': '90s played',
    'Gls': 'Goals scored',
    'Sh': 'Shots taken',
    'SoT': 'Shots on target',
    'SoT%': 'Percentage of shots on target',
    'Sh/90': 'Shots per 90 minutes',
    'SoT/90': 'Shots on target per 90 minutes',
    'G/Sh': 'Goals per shot',
    'G/SoT': 'Goals per shot on target',
    'Dist': 'Average shot distance (yd)',
    'FK': 'Shots from free kicks',
    'PK': 'Penalties made',
    'PKatt': 'Penalty attempts',
    'xG': 'Expected goals (xG)',
    'npxG': 'Non-penalty xG',
    'npxG/Sh': 'Non-penalty xG per shot',
    'G-xG': 'Difference between goals and xG',
    'np:G-xG': 'Difference between goals and non-penalty xG'
    }

    passing_mapping = {
    'Squad': 'Squad',
    '# Pl': 'Number of players',
    '90s': '90s played',
    'Cmp1': 'Completed passes',
    'Att1': 'Pass attempts',
    'Cmp%1': 'Pass completion percentage',
    'TotDist': 'Total passing distance (m)',
    'PrgDist': 'Progressive passing distance (m)',
    'Cmp2': 'Completed short passes',
    'Att2': 'Short pass attempts',
    'Cmp%2': 'Short pass completion percentage',
    'Cmp3': 'Completed medium passes',
    'Att3': 'Medium pass attempts',
    'Cmp%3': 'Medium pass completion percentage',
    'Cmp4': 'Completed long passes',
    'Att4': 'Long pass attempts',
    'Cmp%4': 'Long pass completion percentage',
    'Ast': 'Assists',
    'xAG': 'Expected assists (xAG)',
    'xA': 'Expected assists (xA)',
    'A-xAG': 'A-xA',
    'KP': 'Key passes',
    '1/3': 'Passes into the final third',
    'PPA': 'Passes into the penalty area',
    'CrsPA': 'Crosses into the penalty area',
    'PrgP': 'Progressive passes'
    }
    gca_mapping = {
    'Squad': 'Squad',
    '# Pl': 'Number of players',
    '90s': '90s played',
    'SCA': 'Shot-creating actions',
    'SCA90': 'Shot-creating actions per 90 minutes',
    'PassLive1': 'Live-ball passes leading to shots',
    'PassDead1': 'Dead-ball passes leading to shots',
    'TO1': 'Take-ons leading to shots',
    'Sh1': 'Shots leading to shot-creating actions',
    'Fld1': 'Fouls drawn leading to shots',
    'Def1': 'Defensive actions leading to shots',
    'GCA': 'Goal-creating actions',
    'GCA90': 'Goal-creating actions per 90 minutes',
    'PassLive2': 'Live-ball passes leading to goals',
    'PassDead2': 'Dead-ball passes leading to goals',
    'TO2': 'Take-ons leading to goals',
    'Sh2': 'Shots leading to goal-creating actions',
    'Fld2': 'Fouls drawn leading to goals ',
    'Def2': 'Defensive actions leading to goals'
}

    defending_mapping = {
    'Squad': 'Squad',
    '# Pl': 'Number of players',
    '90s': '90s played',
    'Tkl1': 'Tackles',
    'TklW': 'Tackles won',
    'Def 3rd': 'Tackles in the defensive third',
    'Mid 3rd': 'Tackles in the middle third',
    'Att 3rd': 'Tackles in the attacking third',
    'Tkl2': 'Dribblers tackled',
    'Att': 'Dribbles challenged',
    'Tkl%': 'Tackle success rate against dribblers',
    'Lost': 'Unsuccessful challenges',
    'Blocks': 'Total blocks',
    'Sh': 'Blocked shots',
    'Pass': 'Blocked passes',
    'Int': 'Interceptions',
    'Tkl+Int': 'Tackles and interceptions combined',
    'Clr': 'Clearances',
    'Err': 'Errors leading to shots'
}
    
    possession_mapping = {
    'Squad': 'Team name',
    '# Pl': 'Number of players',
    'Poss': 'Possession percentage',
    '90s': '90s played',
    'Touches': 'Total touches',
    'Def Pen': 'Touches in the defensive penalty area',
    'Def 3rd': 'Touches in the defensive third',
    'Mid 3rd': 'Touches in the middle third',
    'Att 3rd': 'Touches in the attacking third',
    'Att Pen': 'Touches in the attacking penalty area',
    'Live': 'Touches from live-ball situations',
    'Att': 'Take-on attempts (dribbles)',
    'Succ': 'Successful take-ons',
    'Succ%': 'Success rate of take-ons',
    'Tkld': 'Times tackled while dribbling',
    'Tkld%': 'Percentage of take-ons resulting in being tackled',
    'Carries': 'Number of carries',
    'TotDist': 'Total carrying distance (m)',
    'PrgDist': 'Progressive carrying distance (m)',
    'PrgC': 'Progressive carries',
    '1/3': 'Carries into the final third',
    'CPA': 'Carries into the penalty area',
    'Mis': 'Miscontrols',
    'Dis': 'Times dispossessed',
    'Rec': 'Passes received',
    'PrgR': 'Progressive passes received'
}


    url = 'https://fbref.com/en/comps/9/Premier-League-Stats'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    gkping = soup.find("table", {"id": "stats_squads_keeper_for"})
    shooting = soup.find("table", {"id": "stats_squads_shooting_for"})
    passing = soup.find("table", {"id": "stats_squads_passing_for"})
    gca = soup.find("table", {"id": "stats_squads_gca_for"})
    defending = soup.find("table", {"id": "stats_squads_defense_for"})
    possession = soup.find("table", {"id": "stats_squads_possession_for"})

    # Przetwarzanie tabel na DataFrame
    gkping = pd.read_html(gkping.prettify(), encoding='utf-8')[0]
    shooting = pd.read_html(shooting.prettify(), encoding='utf-8')[0]
    passing = pd.read_html(passing.prettify(), encoding='utf-8')[0]
    gca = pd.read_html(gca.prettify(), encoding='utf-8')[0]
    defending = pd.read_html(defending.prettify(), encoding='utf-8')[0]
    possession = pd.read_html(possession.prettify(), encoding='utf-8')[0]

    # Usuwanie wielopoziomowych nagłówków
    for df in [gkping, shooting, passing, gca, defending, possession]:
        df.columns = df.columns.droplevel(0)

    # Usuwanie ostatniej kolumny z possession
   # possession = possession.iloc[:, :-1]
    gkping = gkping.iloc[:, :-1]
    
    shooting.columns=list(shooting_mapping.keys())
    passing.columns=list(passing_mapping.keys())
    gca.columns=list(gca_mapping.keys())
    defending.columns=list(defending_mapping.keys())
    possession.columns=list(possession_mapping.keys())
        
    shooting = shooting.rename(columns=dict(shooting_mapping))
    passing = passing.rename(columns=dict(passing_mapping))
    gca = gca.rename(columns=dict(gca_mapping))
    defending= defending.rename(columns=dict(defending_mapping)) 
    possession= possession.rename(columns=dict(possession_mapping)) 
    
    return {
        "gkping": gkping,
        "shooting": shooting,
        "passing": passing,
        "gca": gca,
        "defending": defending,
        "possession": possession
    }
    
def createTable():
    url = 'https://fbref.com/en/comps/9/Premier-League-Stats'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    table = soup.find("table",{"id":"results2024-202591_overall"})
    table = pd.read_html(table.prettify(),encoding='utf-8')
    table_df = pd.DataFrame(table[0])
    return table_df

def save_to_db(df, db_path, table_name):
    try:
        conn = sqlite3.connect(db_path)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f'Data saved to table "{table_name}" in database "{db_path}".')
    except Exception as e:
        print(f"Error saving to database: {e}")
    finally:
        conn.close()


def save_multiple_tables_to_db(tables, db_path):
    try:
        conn = sqlite3.connect(db_path)
        for table_name, df in tables.items():
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f'Table "{table_name}" saved to database.')
    except Exception as e:
        print(f"Error saving to database: {e}")
    finally:
        conn.close()
        
        
# Funkcja główna (pipeline)
def main():
    db_path = "football_data.db"  # Ścieżka do bazy danych SQLite
    table_name = "premier_league_stats"  # Nazwa tabeli

    # Scrapowanie danych
    print("Starting data scraping...")
    main_df = createPlayerDatabase()
    print("Data scraping completed.")
    tables = createTeamDatabase()

    # Zapis do bazy danych
    print(f"Saving data to database '{db_path}'...")
    save_to_db(main_df, db_path, table_name)
    save_multiple_tables_to_db(tables,db_path)
    print("Pipeline completed successfully.")

if __name__ == "__main__":
    main()