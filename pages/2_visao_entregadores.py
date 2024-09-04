import pandas as pd
import re
import plotly.express as px
import folium
from haversine import haversine
import streamlit as st
import datetime as dt
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Entregadores', page_icon='🚚', layout='wide')

df = pd.read_csv('dataset/train.csv')

df1 = df.copy()

# Removendo NaN e convertendo Delivery_person_Age de texto para int
df1 = df1.loc[df1['Delivery_person_Age'] != 'NaN ', :]
df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int) 

df1 = df1.loc[df1['Festival'] != 'NaN ', :]

# Convertendo Delivery_person_Ratings de texto para float
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

# Convertendo a coluna Order_Date de texto para data
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

# Removendo NaN e convertendo multiple_deliveries de texto para int
df1 = df1.loc[df1['multiple_deliveries'] != 'NaN ', :]
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

# Removendo os espaços dentro de strings
df1['ID'] = df1['ID'].str.strip()
df1['Road_traffic_density'] = df1['Road_traffic_density'].str.strip()
df1['Type_of_order'] = df1['Type_of_order'].str.strip()
df1['Type_of_vehicle'] = df1['Type_of_vehicle'].str.strip()
df1['City'] = df1['City'].str.strip()
df1['Festival'] = df1['Festival'].str.strip()

# Removendo NaN da coluna Weatherconditions
df1 = df1.loc[df1['Weatherconditions'] != 'conditions NaN', :]

# Removendo NaN da coluna City
df1 = df1.loc[df1['City'] != 'NaN', :]

# Removendo NaN da coluna Road_traffic_density
df1 = df1.loc[df1['Road_traffic_density'] != 'NaN', :]

# Resetando o index
df1 = df1.reset_index(drop=True)

# Removendo o texto da coluna Time_taken(min)
df1['Time_taken(min)'] = (df1['Time_taken(min)']
                          .apply(lambda x: int(''.join(re.findall(r'\d+', x))) 
                                 if pd.notna(x) else pd.NA))

# Visão Empresa
# ===========================================
# Side Bar
# ===========================================
st.header( 'Marketplace - Visão Entregadores' )

#image_path = '/home/eric/Documents/repos/projeto_01/logo.jpg'
image = Image.open( 'logo.jpg' )
st.sidebar.image( image, width=100 )

st.sidebar.markdown( '# Curry Company' )
st.sidebar.markdown( '### Fastest Delivery in Town' )
st.sidebar.markdown( '''---''' )

st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider( 
    'Até qual valor?',
    value=dt.datetime( 2022, 4, 13 ),
    min_value=dt.datetime( 2022, 2, 11 ),
    max_value=dt.datetime( 2022, 4, 6),
    format='DD-MM-YYYY'
)

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

st.sidebar.markdown( '''---''' )

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

st.sidebar.markdown( '''---''' )

weather_options = st.sidebar.multiselect(
    'Quais as condições do climáticas?',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 
    'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 
    'conditions Stormy', 'conditions Sunny', 'conditions Windy']
)

# Filtro de condições climáticas
linhas_selecionadas = df1['Weatherconditions'].isin( weather_options )
df1 = df1.loc[linhas_selecionadas, :]

st.sidebar.markdown( '''---''' )
st.sidebar.markdown( '### Powered by Comunidade DS' )

# ===========================================
# Layout
# ===========================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title( 'Overall Metrics' )

        col1, col2, col3, col4 = st.columns( 4, gap='large' )
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric( 'Maior Idade', maior_idade )

        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric( 'Menor Idade', menor_idade )

        with col3:
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric( 'Melhor condição', melhor_condicao )

        with col4:
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric( 'Pior condição', pior_condicao )

    with st.container():
        st.markdown('''---''')
        st.title( 'Avaliações' )

        col1, col2 = st.columns ( 2 )
        with col1:
            st.subheader( 'Avaliação média por entregador' )
            avg_pratings_per_deliver = (df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                        .groupby('Delivery_person_ID')
                                        .mean()
                                        .reset_index())
            st.dataframe( avg_pratings_per_deliver )

        with col2:
            st.subheader( 'Avaliação média por trânsito' )
            avg_std_per_traffic = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                    .groupby('Road_traffic_density')['Delivery_person_Ratings']
                                    .agg(['mean', 'std'])
                                    .reset_index()
                                    .rename(columns={'mean': 'mean_ratings',
                                                    'std': 'std_ratings'})
                                    )
            st.dataframe( avg_std_per_traffic )

            st.subheader( 'Avaliação média por clima' )
            avg_std_per_weather = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                            .groupby('Weatherconditions')['Delivery_person_Ratings']
                                            .agg(['mean', 'std'])
                                            .reset_index()
                                            .rename(columns={'mean': 'mean_ratings',
                                                            'std': 'std_ratings'})
                                        )
            st.dataframe( avg_std_per_weather )

    with st.container():
        st.markdown('''---''')
        st.title( 'Velocidade de Entrega' )

        col1, col2 = st.columns( 2 )

        with col1:
            st.subheader( 'Top entregadores mais rápidos' )
            deliver_fast = (df1.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']]
                    .groupby(['City', 'Delivery_person_ID'])['Time_taken(min)']
                    .min()
                    .reset_index()
                    .sort_values(['City', 'Time_taken(min)'], ascending=[True, True])
                    .groupby('City')
                    .head(10)
                    )
            st.dataframe( deliver_fast )

        with col2:
            st.subheader( 'Top entregadores mais lentos' )
            deliver_low = (df1.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']]
                    .groupby(['City', 'Delivery_person_ID'])['Time_taken(min)']
                    .max()
                    .reset_index()
                    .sort_values(['City', 'Time_taken(min)'], ascending=[True, True])
                    .groupby('City')
                    .head(10)
                    )
            st.dataframe( deliver_low )