from json.tool import main
import time 
import requests
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from highlight_text import fig_text
from bs4 import BeautifulSoup, Comment
import sqlite3
import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import add_image, PyPizza, Radar

db_path = "football_data.db"


@st.cache_data
def createDatabase():

    # Połączenie z bazą danych
    conn = sqlite3.connect(db_path)

    # Wykonanie zapytania SQL
    query = "SELECT * FROM premier_league_stats"  # Zmień nazwę tabeli, jeśli użyłeś innej
    df = pd.read_sql_query(query, conn)



    # Zamknięcie połączenia
    conn.close()

    return df
    


@st.cache_data
def createTable():
    url = 'https://fbref.com/en/comps/9/Premier-League-Stats'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    table = soup.find("table",{"id":"results2024-202591_overall"})
    table = pd.read_html(table.prettify(),encoding='utf-8')
    table_df = pd.DataFrame(table[0])
    return table_df


def prepare():
  url = 'https://fbref.com/en/comps/9/Premier-League-Stats'
  soup = BeautifulSoup(requests.get(url).content, 'html.parser')


  gkping = soup.find( "table",{"id":"stats_squads_keeper_for"})
  shooting = soup.find( "table",{"id":"stats_squads_shooting_for"})
  passing = soup.find( "table",{"id":"stats_squads_passing_for"})
  gca = soup.find( "table",{"id":"stats_squads_gca_for"})
  defending = soup.find( "table",{"id":"stats_squads_defense_for"})
  possession = soup.find( "table",{"id":"stats_squads_possession_for"})
  main = [gkping,shooting,passing,gca,defending,possession]

  gkping = pd.read_html(gkping.prettify(),encoding='utf-8')
  gkping = pd.DataFrame(gkping[0])

  shooting = pd.read_html(shooting.prettify(),encoding='utf-8')
  shooting = pd.DataFrame(shooting[0])

  passing = pd.read_html(passing.prettify(),encoding='utf-8')
  passing = pd.DataFrame(passing[0])

  gca = pd.read_html(gca.prettify(),encoding='utf-8')
  gca = pd.DataFrame(gca[0])

  defending = pd.read_html(defending.prettify(),encoding='utf-8')
  defending = pd.DataFrame(defending[0])

  possession = pd.read_html(possession.prettify(),encoding='utf-8')
  possession = pd.DataFrame(possession[0])

  main = [gkping,shooting,passing,gca,defending,possession]
  for x in main:
      x.columns = x.columns.droplevel(0)

  possession = possession.iloc[:, :-1]

  gkping = gkping[['Squad','GA','CS']]
  shooting = shooting[['Squad', 'SoT/90','npxG']]
  passing = passing[['Squad','1/3','PrgP']]
  gca = gca[['Squad','GCA90']]
  defending = defending[['Squad','TklW','Int']]
  possession = possession[['Squad','Poss','Succ','PrgC']]

  possession = possession.rename(columns={"PrgC": "ProgCarries"})
  passing = passing.rename(columns={"PrgP":"ProgPasses"})

  main = pd.merge(gkping,shooting,on='Squad')
  main = pd.merge(main,passing,on='Squad')
  main = pd.merge(main,gca,on='Squad')
  main = pd.merge(main,defending,on='Squad')
  main = pd.merge(main,possession,on='Squad')

  main = main.rename(columns={"Succ": "Successful Dribbles","ProgCarries": "Progressive Carries","ProgPasses": "Progressive Passes","TklW": "Tackles Won","Poss": "Possesion[%]","Int": "Interceptions","1/3": "Passes into final third"})
  return main

def radar_mosaic(radar_height, title_height, figheight):

    if title_height + radar_height > 1:
        error_msg = 'Reduce one of the radar_height or title_height so the total is ≤ 1.'
        raise ValueError(error_msg)
    endnote_height = 1 - title_height - radar_height
    figwidth = figheight * radar_height
    figure, axes = plt.subplot_mosaic([['title'], ['radar'], ['endnote']],
                                        gridspec_kw={'height_ratios': [title_height, radar_height,
                                                                        endnote_height],
                                                    # the grid takes up the whole of the figure 0-1
                                                    'bottom': 0, 'left': 0, 'top': 1,
                                                    'right': 1, 'hspace': 0},
                                        figsize=(figwidth, figheight))
    axes['title'].axis('off')
    axes['endnote'].axis('off')
    return figure, axes


def create_radar_chart(categories, low, high, pvalues1, pvalues2, player1, player2):
    """
    Creates a radar chart comparing two players.

    Parameters:
        categories (list): List of radar chart categories.
        low (list): Minimum values for each category.
        high (list): Maximum values for each category.
        pdb: Instance for creating the radar mosaic.
        pvalues1: Values for the first player.
        pvalues2: Values for the second player.
        player1 (str): Name of the first player.
        player2 (str): Name of the second player.

    Returns:
        matplotlib.figure.Figure: The generated radar chart figure.
    """
    radar = Radar(categories, low, high,
                  round_int=[False]*len(categories),
                  num_rings=4,
                  ring_width=1, center_circle_radius=1)

    fig, axs = radar_mosaic(radar_height=0.915, title_height=0.06, figheight=14)

    # Plot the radar
    radar.setup_axis(ax=axs['radar'], facecolor='None', dpi=500)
    radar.draw_circles(ax=axs['radar'], facecolor='#28252c', edgecolor='#39353f', lw=1.5)
    radar_output = radar.draw_radar_compare(
        pvalues1, pvalues2, ax=axs['radar'],
        kwargs_radar={'facecolor': '#00f2c1', 'alpha': 0.6},
        kwargs_compare={'facecolor': '#d80499', 'alpha': 0.6}
    )                                
    radar_poly, radar_poly2, vertices1, vertices2 = radar_output
    radar.draw_range_labels(ax=axs['radar'], fontsize=25, color='#fcfcfc')
    radar.draw_param_labels(ax=axs['radar'], fontsize=25, color='#fcfcfc')
    axs['radar'].scatter(
        vertices1[:, 0], vertices1[:, 1],
        c='#00f2c1', edgecolors='#6d6c6d', marker='o', s=150, zorder=2
    )
    axs['radar'].scatter(
        vertices2[:, 0], vertices2[:, 1],
        c='#d80499', edgecolors='#6d6c6d', marker='o', s=150, zorder=2
    )

    axs['title'].text(
        0.01, 0.65, '{}'.format(player1), fontsize=28, color='#01c49d', ha='left', va='center'
    )
    axs['title'].text(
        0.99, 0.65, '{}'.format(player2), fontsize=28,
        ha='right', va='center', color='#d80499'
    )

    fig.set_facecolor('#0E1117')
    
    return fig





def create_pizza_chart(params, values, team_color, selected_club, min_range, max_range):
    """
    Creates a reusable function to generate a pizza chart.

    Parameters:
        params (list): List of parameters for the chart.
        values (list): Values corresponding to the parameters.
        team_color (dict): Dictionary mapping team names to their colors.
        selected_club (str): The selected club for which the chart is generated.
        min_range (float): Minimum range for the chart.
        max_range (float): Maximum range for the chart.

    Returns:
        matplotlib.figure.Figure: The generated pizza chart figure.
    """
    baker = PyPizza(
        params=params,                  # list of parameters
        background_color='#0E1117',
        last_circle_color='#FFFFFF',
        other_circle_color='#FFFFFF',
        min_range=min_range,
        max_range=max_range,
        straight_line_color="#FFFFFF",  # color for straight lines
        straight_line_lw=1,             # linewidth for straight lines
        last_circle_lw=6,               # linewidth of last circle
        other_circle_lw=1,              # linewidth for other circles
        other_circle_ls="-."           # linestyle for other circles
    )

    fig, axs = baker.make_pizza(
        values,
        figsize=(8, 8),      # adjust figsize according to your need
        param_location=110,  # where the parameters will be added
        kwargs_slices=dict(
            facecolor=team_color[selected_club], edgecolor="#FFFFFF",
            zorder=2, linewidth=1
        ), 
        kwargs_compare=dict(
            facecolor="#BEBEBE", edgecolor="#222222", alpha=1, zorder=3, linewidth=1,
        ), # values to be used when plotting slices
        kwargs_params=dict(
            color="#FFFFFF", fontsize=12, va="center"
        ),                   # values to be used when adding parameter
        kwargs_values=dict(
            color="#FFFFFF", fontsize=12, zorder=4,
            bbox=dict(
                edgecolor="#FFFFFF", facecolor=team_color[selected_club], alpha=.8,
                boxstyle="round,pad=0.2", lw=1
            )
        ),
        kwargs_compare_values=dict(
            color="#000000", fontsize=12, zorder=3,
            bbox=dict(
                edgecolor="#000000", facecolor="#BEBEBE", alpha=0.75,
                boxstyle="round,pad=0.2", lw=1
            )
        )     # values to be used when adding parameter-values
    )

    return fig

def create_bar_chart(categories, pvalues1, pvalues2, player1, player2):
    """
    Creates a bar chart comparing two players.

    Parameters:
        categories (list): List of categories for the bar chart.
        pvalues1 (list): Values for the first player.
        pvalues2 (list): Values for the second player.
        player1 (str): Name of the first player.
        player2 (str): Name of the second player.

    Returns:
        matplotlib.figure.Figure: The generated bar chart figure.
    """
    import matplotlib.pyplot as plt
    import numpy as np

    x = np.arange(len(categories))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(10, 6))

    # bars1 = ax.bar(x - width/2, pvalues1, width, label=player1, color='#00f2c1', edgecolor='#6d6c6d')
    # bars2 = ax.bar(x + width/2, pvalues2, width, label=player2, color='#d80499', edgecolor='#6d6c6d')

    # Add some text for labels, title, and custom x-axis tick labels, etc.
    ax.set_xlabel('Categories', fontsize=14, color='#fcfcfc')
    ax.set_ylabel('Values', fontsize=14, color='#fcfcfc')
    ax.set_title('Comparison of Players', fontsize=16, color='#fcfcfc')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=12, color='#fcfcfc')
    ax.legend()

    # Customize the plot's appearance
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#fcfcfc')
    ax.spines['bottom'].set_color('#fcfcfc')
    ax.tick_params(colors='#fcfcfc')
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#28252c')

    return fig

def create_vertical_bar_chart(categories, pvalues1, pvalues2, player1, player2):
    """
    Creates a vertical bar chart comparing two players using Plotly.

    Parameters:
        categories (list): List of categories for the bar chart.
        pvalues1 (list): Values for the first player.
        pvalues2 (list): Values for the second player.
        player1 (str): Name of the first player.
        player2 (str): Name of the second player.

    Returns:
        plotly.graph_objects.Figure: The generated bar chart figure.
    """


    fig = go.Figure()

    # Add bars for the first player
    fig.add_trace(go.Bar(
        x=categories,
        y=pvalues1,
        name=player1,
        marker=dict(color='#00f2c1', line=dict(color='#6d6c6d', width=1))
    ))

    # Add bars for the second player
    fig.add_trace(go.Bar(
        x=categories,
        y=pvalues2,
        name=player2,
        marker=dict(color='#d80499', line=dict(color='#6d6c6d', width=1))
    ))

    # Update layout
    fig.update_layout(
        title='Comparison of Players',
        xaxis=dict(title='Categories', titlefont=dict(size=14), tickfont=dict(size=12)),
        yaxis=dict(title='Values', titlefont=dict(size=14), tickfont=dict(size=12)),
        barmode='group',
        plot_bgcolor='#28252c',
        paper_bgcolor='#0E1117',
        font=dict(color='#fcfcfc')
    )

    return fig

def calculate_values(main, selected_club, mode):
    if mode == 'Stats':
        values = [
            main[main["Squad"] == selected_club].iloc[0][x]
            for x in main.columns[1:]
        ]
        
    else:
       values = [
            int(main["GA"].rank(ascending=False, pct=True)[main["Squad"] == selected_club].iloc[0] * 100)
        ] + [
            int(main[x].rank(ascending=True, pct=True)[main["Squad"] == selected_club].iloc[0] * 100)
            for x in main.columns[2:]
        ]
    return values

def calculate_ranges(main, playerdb, categories, mode):
    if mode == 'Stats':
        max_range = [main[x].max() for x in main.columns[1:]]
        min_range = [main[x].min() for x in main.columns[1:]]
        low = [
            min(playerdb[playerdb['Minutes Played'] > 300][x])
            for x in categories
        ]
        high = [
            max(playerdb[playerdb['Minutes Played'] > 300][x])
            for x in categories
        ]
    else:
        max_range = [100] * len(main.columns[1:])
        min_range = [0] * len(main.columns[1:])
        low = [0] * len(categories)
        high = [100] * len(categories)

    return min_range, max_range, low, high

def calculate_player_percentiles(playerdb, player1, player2, categories, mode):
    if mode == 'Percentile vs whole league':
        pvalues1 = [
            playerdb[x].rank(pct=True).iloc[
                playerdb[playerdb['Player'].str.contains(player1)].index
            ].reset_index(drop=True)[0] * 100
            for x in categories
        ]
        
        pvalues2 = [
            playerdb[x].rank(pct=True).iloc[
                playerdb[playerdb['Player'].str.contains(player2)].index
            ].reset_index(drop=True)[0] * 100
            for x in categories
        ]
    elif mode == 'Percentile vs position':
        # Pobieranie pozycji zawodników
        position1 = playerdb.loc[
            playerdb[playerdb['Player'].str.contains(player1)].index[0], 'Position'
        ]
        position2 = playerdb.loc[
            playerdb[playerdb['Player'].str.contains(player2)].index[0], 'Position'
        ]
        # Filtracja graczy według pozycji
        position_filter1 = playerdb[playerdb['Position'] == position1].reset_index(drop=True)
        position_filter2 = playerdb[playerdb['Position'] == position2].reset_index(drop=True)

        pvalues1 = [
            position_filter1[x].rank(pct=True).iloc[
                position_filter1[position_filter1['Player'].str.contains(player1)].index
            ].reset_index(drop=True)[0] * 100
            for x in categories
        ]
        

        pvalues2 = [
            position_filter2[x].rank(pct=True).iloc[
                position_filter2[position_filter2['Player'].str.contains(player2)].index
            ].reset_index(drop=True)[0] * 100
            for x in categories
        ]
    else:
        pvalues1 = playerdb.loc[
            playerdb[playerdb['Player'].str.contains(player1)].index[0], categories
        ].tolist()

        pvalues2 = playerdb.loc[
            playerdb[playerdb['Player'].str.contains(player2)].index[0], categories
        ].tolist()


    return pvalues1, pvalues2



def create_single_player_bar_chart(categories, pvalues, player):
    """
    Creates a vertical bar chart for a single player's statistics using Plotly.

    Parameters:
        categories (list): List of categories for the bar chart.
        pvalues (list): Values for the player.
        player (str): Name of the player.

    Returns:
        plotly.graph_objects.Figure: The generated bar chart figure.
    """

        # Round values to 2 decimal places
    pvalues = [round(value, 2) for value in pvalues]

    fig = go.Figure()

    # Add bars for the player
    fig.add_trace(go.Bar(
        x=categories,
        y=pvalues,
        name=player,
        marker=dict(color='#1f77b4', line=dict(color='#6d6c6d', width=1))
    ))

    # Update layout
    fig.update_layout(
        title=f'Statistics for {player}',
        xaxis=dict(title='Categories', titlefont=dict(size=14), tickfont=dict(size=12)),
        yaxis=dict(title='Values', titlefont=dict(size=14), tickfont=dict(size=12)),
        plot_bgcolor='#28252c',
        paper_bgcolor='#0E1117',
        font=dict(color='#fcfcfc'),
        legend=dict(title='Legend', font=dict(size=12))
    )

    # Add value annotations
    for i, value in enumerate(pvalues):
        fig.add_annotation(
            x=categories[i],
            y=value,
            text=f'{value:.2f}',
            showarrow=False,
            font=dict(size=12, color="white"),
            bgcolor="#444444",
            opacity=0.8
        )

    # Add explanation
    fig.add_annotation(
        x=0.5, y=-0.3, xref='paper', yref='paper',
        text='Values represent the player\'s performance in each category vs Premier League.',
        showarrow=False,
        font=dict(size=12, color="white"),
        align="center"
    )

    return fig

def create_single_player_pizza_chart(params, values, player_color, player_name, min_range, max_range):
    """
    Creates a pizza chart for a single player.

    Parameters:
        params (list): List of parameters for the chart.
        values (list): Values corresponding to the parameters.
        player_color (str): Color for the player's slices.
        player_name (str): The name of the player.
        min_range (float): Minimum range for the chart.
        max_range (float): Maximum range for the chart.

    Returns:
        matplotlib.figure.Figure: The generated pizza chart figure.
    """
    

    values = [round(value, 2) for value in values]
    baker = PyPizza(
        params=params,                  # list of parameters
        background_color='#0E1117',
        last_circle_color='#FFFFFF',
        other_circle_color='#FFFFFF',
        min_range=min_range,
        max_range=max_range,
        straight_line_color="#FFFFFF",  # color for straight lines
        straight_line_lw=1,             # linewidth for straight lines
        last_circle_lw=6,               # linewidth of last circle
        other_circle_lw=1,              # linewidth for other circles
        other_circle_ls="-."           # linestyle for other circles
    )

    fig, axs = baker.make_pizza(
        values,
        figsize=(8, 8),      # adjust figsize according to your need
        param_location=110,  # where the parameters will be added
        kwargs_slices=dict(
            facecolor=player_color, edgecolor="#FFFFFF",
            zorder=2, linewidth=1
        ),
        kwargs_params=dict(
            color="#FFFFFF", fontsize=12, va="center"
        ),                   # values to be used when adding parameter
        kwargs_values=dict(
            color="#FFFFFF", fontsize=12, zorder=4,
            bbox=dict(
                edgecolor="#FFFFFF", facecolor=player_color, alpha=.8,
                boxstyle="round,pad=0.2", lw=1
            )
        )
    )

    fig.text(
        0.5, 0.02, f'Statistics for {player_name}', size=14, color="white",
        ha="center", va="center"
    )

    return fig

def create_plotly_radar_chart(categories, low, high, pvalues1, pvalues2, player1, player2):
    """
    Creates a radar chart comparing two players using Plotly.

    Parameters:
        categories (list): List of radar chart categories.
        low (list): Minimum values for each category.
        high (list): Maximum values for each category.
        pvalues1 (list): Values for the first player.
        pvalues2 (list): Values for the second player.
        player1 (str): Name of the first player.
        player2 (str): Name of the second player.

    Returns:
        plotly.graph_objects.Figure: The generated radar chart figure.
    """
    # Normalize the player values to the range [0, 1]
    normalized_values1 = [(p - l) / (h - l) for p, l, h in zip(pvalues1, low, high)]
    normalized_values2 = [(p - l) / (h - l) for p, l, h in zip(pvalues2, low, high)]

    # Create a DataFrame for Plotly Express
    data = {
        "Category": categories,
        player1: normalized_values1,
        player2: normalized_values2
    }

    df = pd.DataFrame(data)

    # Use Plotly Express to create a radar chart
    fig = px.line_polar(
        df.melt(id_vars=["Category"], var_name="Player", value_name="Value"),
        r="Value",
        theta="Category",
        color="Player",
        line_close=True,
        template="plotly_dark",
    )

    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                showline=False,
                color='#0E1117'
            ),
        ),
        showlegend=True,
        title=dict(
            text=f"{player1} vs {player2} - Radar Chart",
            x=0.5,
            xanchor='center',
            font=dict(size=18, color='white')
        ),
        paper_bgcolor='#0E1117',
        font=dict(color='white')
    )

    return fig


def create_player_comparison_pizza_chart(categories, player1, player2, values1, values2, colors, selected_club1, selected_club2, min_range, max_range, mode):
    """
    Creates a reusable function to generate a pizza chart.

    Parameters:
        params (list): List of parameters for the chart.
        values (list): Values corresponding to the parameters.
        team_color (dict): Dictionary mapping team names to their colors.
        selected_club (str): The selected club for which the chart is generated.
        min_range (float): Minimum range for the chart.
        max_range (float): Maximum range for the chart.

    Returns:
        matplotlib.figure.Figure: The generated pizza chart figure.
    """
    values1 = [round(value, 2) for value in values1]
    values2 = [round(value, 2) for value in values2]

    params_offset  = [abs(a - b) < 10 for a, b in zip(values1, values2)]

    baker = PyPizza(
        params=categories,                  # list of parameters
        background_color='#0E1117',
        last_circle_color='#FFFFFF',
        other_circle_color='#FFFFFF',
        min_range=min_range,
        max_range=max_range,
        straight_line_color="#FFFFFF",  # color for straight lines
        straight_line_lw=1,             # linewidth for straight lines
        last_circle_lw=6,               # linewidth of last circle
        other_circle_lw=1,              # linewidth for other circles
        other_circle_ls="-."           # linestyle for other circles
    )

    fig, axs = baker.make_pizza(
        values1,
        compare_values=values2,
        figsize=(8, 8),      # adjust figsize according to your need
        param_location=110,  # where the parameters will be added
        kwargs_slices=dict(
            facecolor="#00f2c1", edgecolor="#FFFFFF",
            zorder=2, linewidth=1
        ), 
        kwargs_compare=dict(
            facecolor="#d80499", edgecolor="#222222", alpha=1, zorder=3, linewidth=1,
        ), # values to be used when plotting slices
        kwargs_params=dict(
            color="#FFFFFF", fontsize=12, va="center"
        ),                   # values to be used when adding parameter
        kwargs_values=dict(
            color="#000000", fontsize=12, zorder=4,
            bbox=dict(
                edgecolor="#FFFFFF", facecolor="#00f2c1", alpha=1,
                boxstyle="round,pad=0.2", lw=1
            )
        ),
        kwargs_compare_values=dict(
            color="#d80499", fontsize=12, zorder=3,
            bbox=dict(
                edgecolor="#000000", facecolor="#FFFFFF", alpha=1,
                boxstyle="round,pad=0.2", lw=1
            )
        )     # values to be used when adding parameter-values
    )
    baker.adjust_texts(params_offset, offset=-0.25, adj_comp_values=True)

    fig_text(
        0.515, 0.99, f"<{player1}> vs <{player2}>", size=17, fig=fig,
        highlight_textprops=[{"color": "#00f2c1"}, {"color": "#d80499"}],
        ha="center",  color="#FFFFFF"
    )
    if mode == "Percentile vs position":

        fig.text(
        0.515, 0.942,
        "Percentile Rank vs Premier League (player's position-specific) | Season 2024-25",
        size=10,
        ha="center",  color="#FFFFFF"
        )
    elif mode == "Percentile vs whole league":

        fig.text(
        0.515, 0.942,
        "Percentile Rank vs Premier League | Season 2024-25",
        size=10,
        ha="center",  color="#FFFFFF"
        )
    else:

        fig.text(
        0.515, 0.942,
        "Stats | Season 2024-25",
        size=10,
        ha="center",  color="#FFFFFF"
        )
    return fig