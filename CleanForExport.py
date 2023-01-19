import pandas as pd
import re

# Source Material Sites, Thank You Fantasy Pros for being great
# https://www.fantasypros.com/nfl/advanced-stats-wr.php
# https://www.fantasypros.com/nfl/stats/wr.php
# https://www.fantasypros.com/nfl/reports/leaders/half-ppr-wr.php?year=2022

# pandas settings to print more of the table to the screen
desired_width = 320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns', 16)

# Load Advanced WR stats csv and drop bottom two rows (all null stuff)
wr_adv = pd.read_csv(
    r'C:\Users\Matt\Desktop\FantasyData\WR_Stats\Week18\FantasyPros_Fantasy_Football_Advanced_Stats_Report_WR.csv')
wr_adv = wr_adv.iloc[:-2, :]

# Separate player name and team into two different columns
wr_adv['player'] = wr_adv.apply(lambda row: re.split(r'\((.*)\)', row['Player'])[0], axis=1)
wr_adv['team'] = wr_adv.apply(lambda row: re.split(r'\((.*)\)', row['Player'])[1], axis=1)

# Fantasy Pro Data includes a comma as the thousand separator, this forces the value to be in string form
# Convert the 'string form' columns by replacing the comma and converting to floating point
object_columns = ['YDS', 'YBC', 'AIR']
for n in object_columns:
    wr_adv[n] = wr_adv.apply(lambda row: row[n].replace(",", ""), axis=1)
    wr_adv[n] = wr_adv[n].astype(float)

# Remove percent symbol from column and convert column to a float value, also divide by 100
wr_adv['% TM'] = wr_adv.apply(lambda row: row['% TM'][:-1], axis=1)
wr_adv['% TM'] = wr_adv['% TM'].astype(float)
wr_adv['% TM'] = wr_adv.apply(lambda row: round((row['% TM']/100), 3), axis=1)

# Drop FA players from this exercise
wr_adv = wr_adv[wr_adv.team != 'FA']

# Rename columns to fix the backslash characters
wr_adv.rename(columns={'Rank': 'rank', 'G': 'games', 'REC': 'rec', 'YDS': 'yds', 'Y/R': 'yards_per_rec',
                    'YBC': 'ybc', 'YBC/R': 'ybc_per_rec', 'AIR': 'air_yards', 'AIR/R': 'air_per_rec',
                    'YAC': 'yac', 'YAC/R': 'yac_per_rec', 'YACON': 'yacon', 'YACON/R': 'yacon_per_rec',
                    'BRKTKL': 'brk_tkl', 'TGT': 'targets', '% TM': 'percent_team_targets', 'CATCHABLE': 'catchable',
                    'DROP': 'drops', 'RZ TGT': 'red_zone_targets', '10+ YDS': '10_plus', '20+ YDS': '20_plus',
                    '30+ YDS': '30_plus', '40+ YDS': '40_plus', '50+ YDS': '50_plus', 'LNG': 'long'}, inplace=True)

# Read in another CSV for the TD column because it would be nice to have in the advanced frame!
wr_tds = pd.read_csv(
    r'C:\Users\Matt\Desktop\FantasyData\WR_Stats\Week18\FantasyPros_Fantasy_Football_Statistics_WR.csv')
wr_tds = wr_tds.iloc[:-2, :]

# Separate player name and team into two different columns
wr_tds['player'] = wr_tds.apply(lambda row: re.split(r'\((.*)\)', row['Player'])[0], axis=1)
wr_tds['team'] = wr_tds.apply(lambda row: re.split(r'\((.*)\)', row['Player'])[1], axis=1)

# Rename the TD column to 'tds'
wr_tds.rename(columns={'TD': 'tds'}, inplace=True)

# Isolate only the columns needed for the join
wr_tds = wr_tds.loc[:, ['player', 'team', 'tds']]

# Add the tds column to the first dataframe with the merge command
wr_adv = pd.merge(wr_adv, wr_tds, how='left', on=['player', 'team'])

# Reorder the columns and remove the original 'Player' combined column
final = wr_adv.loc[:, ['rank', 'player', 'team', 'games', 'rec', 'yds', 'tds', 'yards_per_rec', 'ybc', 'ybc_per_rec',
                       'air_yards', 'air_per_rec', 'yac', 'yac_per_rec', 'brk_tkl', 'targets', 'percent_team_targets',
                       'catchable', 'drops', 'red_zone_targets', '10_plus', '20_plus', '30_plus', '40_plus',
                       '50_plus', 'long']]

# Create new CSV file with changed column names
final.to_csv(r'C:\Users\Matt\Desktop\FantasyData\WR_Stats\Week18\ADV_WR_Stats.csv', index=False)

"""
Next Load the final CSV and create the fantasy points scored table for SQL
"""

# Load second file to convert column names on fantasy point file
wr_points = pd.read_csv(
    r'C:\Users\Matt\Desktop\FantasyData\WR_Stats\Week18\FantasyPros_Fantasy_Football_Points_WR_HALF.csv')

# Rename columns to match the format
wr_points.rename(columns={'Rank': 'rank', 'Player': 'player', 'Team': 'team', 'Games': 'games', 'Points': 'points',
                          'Avg': 'average'}, inplace=True)

# Drop NAN values from dataframe
wr_points.dropna(how='all', inplace=True)

# Write updated file to a new CSV
wr_points.to_csv(r'C:\Users\Matt\Desktop\FantasyData\WR_Stats\Week18\Points_WR_HALF.csv', index=False)
