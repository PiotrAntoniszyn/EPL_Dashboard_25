import numpy as np
from PIL import Image
import playerdb as pdb
import plotly.express as px
import plotly.graph_objects as go
from highlight_text import fig_text
import streamlit as st
st.set_page_config(
 page_title="EPL 24/25 Team Dashboard",
 page_icon=":trophy:",
 layout="wide",
 initial_sidebar_state="auto",
)

edge_team_colors = {'Arsenal':'#063672', 'Aston Villa':'#670E36', 'Bournemouth':'#000000','Brentford':'#FFFFFF', 'Brighton':'#FFFFFF',
               'Burnley':'#99D6EA', 'Chelsea':'#D1D3D4', 'Crystal Palace':'#C4122E', 'Everton':'#FFFFFF', "Fulham": "#FFFFFF",'Ipswich Town':'#DE2C37',
               'Leicester City': '#FDBE11', "Leeds United": "#FFCD00", 'Liverpool':'#00B2A9', 'Manchester City':'#1C2C5B', 'Manchester Utd':'#FBE122',
               'Newcastle':'#F1BE48', 'Norwich':'#00A650','Nott\'ham Forest':'#FFFFFF', 'Sheffield Utd':'#0D171A', 
               'Southampton':'#130C0E', 'Tottenham':'#FFFFFF', 'Watford':'#ED2127', "West Brom": '#FFFFFF', 'West Ham':'#1BB1E7',
               'Wolves':'#231F20'}

team_colors = {'Arsenal':'#ef0107', 'Aston Villa':'#95bfe5', 'Bournemouth':'#da291c','Brentford':'#D20000', 'Brighton':'#0057b8',
               'Burnley':'#6c1d45', 'Chelsea':'#034694', 'Crystal Palace':'#1b458f', 'Everton':'#003399', "Fulham": "#000000",'Ipswich Town':'#3A64A3',
               'Leicester City':'#003090', "Leeds United": "#1D428A", 'Liverpool':'#c8102e', 'Manchester City':'#6cabdd', 'Manchester Utd':'#da291c',
               'Newcastle Utd':'#241f20', 'Norwich':'#fff200','Nott\'ham Forest':'#E53233', 'Sheffield Utd':'#ee2737', 
               'Southampton':'#d71920', 'Tottenham':'#132257', 'Watford':'#fbee23', "West Brom": '#122F67', 'West Ham':'#7a263a',
               'Wolves':'#fdb913'}

#######################

st.title("Premier League Team Dashboard | Season 24/25 ")

#######################

col1, col2= st.columns([2,2])

playerdb = pdb.createDatabase()

leaguetable = pdb.createTable()

main = pdb.prepare()

#######################

st.sidebar.header("Dashboard Settings")

with st.sidebar.expander("Club",expanded=True):
  selected_club = st.selectbox("",options=list(main['Squad'].sort_values(ascending=True)))

with st.sidebar.expander("View Mode",expanded=True):
  mode = st.radio("", ("Percentile vs whole league","Percentile vs position","Stats"))

st.sidebar.header("Player Comparison Settings")

with st.sidebar.expander("Metrics",expanded=True):
  categories = st.multiselect('',list(playerdb.columns[10:]),["Expected Goals","Expected Assists","Progressive Carries","Key Passes", "Goal-Creating Actions", "Shots on Target"])

with st.sidebar.expander("Players",expanded=True):
  player1 = st.selectbox("Player 1:",options=list(playerdb[playerdb['Team']==selected_club]['Player'].sort_values(ascending=True)),index=0)
  player2 = st.selectbox("Player 2:",options=list(playerdb[playerdb['Team']==selected_club]['Player'].sort_values(ascending=True)),index=1)

image = Image.open('PL_Logos/{}.png'.format(selected_club))



with col1:
  with st.container():
    st.image(image, width=80)
    st.subheader("Rank: {} - {} pts".format(leaguetable[leaguetable['Squad']==selected_club]['Rk'].reset_index(drop=True)[0],leaguetable[leaguetable['Squad']==selected_club]['Pts'].reset_index(drop=True)[0]))
    st.subheader(" Wins: {} Draws: {} Losses: {}".format(leaguetable[leaguetable['Squad']==selected_club]['W'].reset_index(drop=True)[0],leaguetable[leaguetable['Squad']==selected_club]['D'].reset_index(drop=True)[0],leaguetable[leaguetable['Squad']==selected_club]['L'].reset_index(drop=True)[0]))
    st.subheader("Last 5 matches: {}".format(leaguetable[leaguetable['Squad']==selected_club]['Last 5'].reset_index(drop=True)[0]))
    st.subheader("Top scorer(s): {}".format(leaguetable[leaguetable['Squad']==selected_club]['Top Team Scorer'].reset_index(drop=True)[0]))

#######################

values = pdb.calculate_values(main,selected_club,mode)

min_range, max_range, low, high = pdb.calculate_ranges(main,playerdb,categories,mode)

pvalues1, pvalues2 = pdb.calculate_player_percentiles(playerdb,player1,player2,categories,mode)

#######################

with col2:
  params = main.columns[1:]

  fig = pdb.create_pizza_chart(params,values,team_colors,selected_club,min_range,max_range)

  with st.spinner("Loading..."):
    st.subheader("Team Performance")
    if mode == 'Stats':
      st.markdown("Stats | Season 2024-25")
    else:
      st.markdown("Percentile vs PL clubs | Season 2024-25")
    st.pyplot(fig)



#######################






with st.expander("Scatter plot",expanded=True):  
  colcat1,colcat2 = st.columns(2)

  with colcat1:
    cat1 = st.selectbox('X',options=list(playerdb.columns[10:]),index=9)
  with colcat2:  
    cat2 = st.selectbox('Y',options=list(playerdb.columns[10:]),index=11)
  fig2 = px.scatter(playerdb, x=playerdb[cat1], y=playerdb[cat2],title='Scatter Plot -  {} / {}'.format(cat1,cat2), template="simple_white", hover_data=['Player'],labels={
                      "x": cat1,
                      "y": cat2 
                  })

  marker_color = np.where(playerdb['Team'] == selected_club , '#FF4B4B' , '#262730')
  fig2.update_traces(
                  marker = dict(color=marker_color),
                  opacity = .8,
                  )
  st.plotly_chart(fig2, use_container_width=True)



with st.expander("Player Comparison",expanded=True):
  with st.spinner("Loading..."):


    team1all = selected_club
    player1all = player1

    team2all =  selected_club
    player2all = player2
    pvalues1all, pvalues2all = pdb.calculate_player_percentiles(playerdb,player1all,player2all,categories,mode)
    #rfig4 = pdb.create_radar_chart(categories,low,high,pvalues1all,pvalues2all,player1all,player2all)
    fig4 = pdb.create_vertical_bar_chart(categories,pvalues1all,pvalues2all,player1all,player2all)

    st.plotly_chart(fig4)
    fig1 = pdb.create_radar_chart(categories,low,high,pvalues1,pvalues2,player1,player2)

    fig7 = pdb.create_player_comparison_pizza_chart(categories,player1all,player2all,pvalues1all,pvalues2all,team_colors,team1all,team2all,low,high,mode)
    st.pyplot(fig7)


    st.pyplot(fig1,use_container_width=True)


with st.expander("Browse squad data",expanded=True):
  st.dataframe(playerdb[playerdb['Team']==selected_club].reset_index(drop=True))

