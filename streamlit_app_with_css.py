#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import mysql.connector

db_host = st.secrets["DB_HOST"]
db_port = st.secrets["DB_PORT"]
db_name =  st.secrets["DB_NAME"]
db_user =  st.secrets["DB_USER"]
db_password =  st.secrets["DB_PASSWORD"]

# Crea una conexión con la base de datos
conn = mysql.connector.connect(host=db_host, port=db_port, database=db_name, user=db_user,password=db_password)

# Crea un cursor para ejecutar comandos SQL
cur = conn.cursor()

# Ejecuta una consulta SQL
sql = "SELECT idc, pregunta, resposta, data, curso FROM teclaPREGUNTES WHERE tema = '10000'"

cur.execute(sql)

# Obtiene los resultados de la consulta
results_database = cur.fetchall()
count_interactions = len(results_database)
# Student List

all_idc = []
all_pregunta = []
all_resposta = []
all_data = []
all_curso = []

for idc,pregunta,resposta,data,curso in results_database:
    all_idc.append(idc)
    all_pregunta.append(pregunta)
    all_resposta.append(resposta)
    all_data.append(data)
    all_curso.append(curso)

all_idc.pop(count_interactions-2)
all_pregunta.pop(count_interactions-2)
all_resposta.pop(count_interactions-2)
all_data.pop(count_interactions-2)
all_curso.pop(count_interactions-2)
all_idc.append('totxs')
all_pregunta.append('totes les preguntes')
all_resposta.append('totes les respostes')
all_data.append('històric')
all_curso.append('totes les etapes')

#we need to store this data to CSV
dic = {'idc': all_idc , 'pregunta':all_pregunta, 'resposta':all_resposta, 'data':all_data, 'curso':all_curso}
df = pd.DataFrame (dic)
df_csv = df.to_csv('random.csv')

conn.commit()

# Cierra la conexión con la base de datos
cur.close()
conn.close()

#######################
# Page configuration
st.set_page_config(
    page_title="STEAMBuilder - Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)


#######################
# Load data
df_reshaped = pd.read_csv('random.csv')


#######################
# Sidebar
with st.sidebar:
    st.title('🏂 STEAMBuilder - Dashboard')
    
    student_list = list(df_reshaped.idc.unique())[::-1]
    
    selected_student = st.selectbox('Selecciona un/a alumne', student_list)
    df_selected_student = df_reshaped[df_reshaped.idc == selected_student]
    df_selected_student_sorted = df_selected_student.sort_values(by="data", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


#######################
# Plots

# Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap

# Choropleth map
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(df_selected_year.population)),
                               scope="usa",
                               labels={'population':'Population'}
                              )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth


# Donut chart
def make_donut(input_response, input_text, input_color):
  if input_color == 'blue':
      chart_color = ['#29b5e8', '#155F7A']
  if input_color == 'green':
      chart_color = ['#27AE60', '#12783D']
  if input_color == 'orange':
      chart_color = ['#F39C12', '#875A12']
  if input_color == 'red':
      chart_color = ['#E74C3C', '#781F16']
    
  source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
  source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
  })
    
  plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
  ).properties(width=130, height=130)
    
  text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
  ).properties(width=130, height=130)
  return plot_bg + plot + text

# Convert population to text 
def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

# Calculation year-over-year population migrations
def calculate_population_difference(input_df, input_year):
  selected_year_data = input_df[input_df['year'] == input_year].reset_index()
  previous_year_data = input_df[input_df['year'] == input_year - 1].reset_index()
  selected_year_data['population_difference'] = selected_year_data.population.sub(previous_year_data.population, fill_value=0)
  return pd.concat([selected_year_data.states, selected_year_data.id, selected_year_data.population, selected_year_data.population_difference], axis=1).sort_values(by="population_difference", ascending=False)


#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown('#### Dades Generals')

    df_num_interactions = count_interactions

    st.metric(label='#Interaccions', value=df_num_interactions, delta='total alumnes')


    st.markdown('#### States Migration')



with col[1]:
    st.markdown('#### Total Population')
    



with col[2]:

    st.markdown('#### Top States')
    with st.expander('Sobre...', expanded=True):
        st.write('''
            - Dades generals de STEAMBuilder
            ''')
