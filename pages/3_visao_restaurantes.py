import pandas as pd
import re
import plotly.express as px
from haversine import haversine
import streamlit as st
import datetime as dt
from PIL import Image
import numpy as np
import plotly.graph_objects as go

st.set_page_config( page_title='Visão Empresa', page_icon='🍲', layout='wide')

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
st.header( 'Marketplace - Visão Restaurantes' )

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

        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        with col1:
            entregadores_unicos = df1['Delivery_person_ID'].nunique()
            col1.metric( 'Entregadores Únicos', entregadores_unicos )

        with col2:
            df1['Distance_km'] = (df1.loc[:, ['Restaurant_latitude', 'Restaurant_longitude', 
                                            'Delivery_location_latitude', 'Delivery_location_longitude']]
                        .apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
)
            distancia_media = np.round(df1.loc[:, 'Distance_km'].mean(), 2)
            
            col2.metric( 'Distância Média', distancia_media )

        with col3:
            df_aux = (df1.loc[:, ['Festival', 'Time_taken(min)']]
                        .groupby('Festival')
                        .agg( {'Time_taken(min)': ['mean', 'std']} )
                        )
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            linhas_selecionadas = df_aux['Festival'] == 'Yes'
            df_aux = np.round(df_aux.loc[linhas_selecionadas, 'avg_time'], 2)
            col3.metric( 'Tempo Médio Festival', df_aux )
            
        with col4:
            df_aux = (df1.loc[:, ['Festival', 'Time_taken(min)']]
                        .groupby('Festival')
                        .agg( {'Time_taken(min)': ['mean', 'std']} )
                        )
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            linhas_selecionadas = df_aux['Festival'] == 'Yes'
            df_aux = np.round(df_aux.loc[linhas_selecionadas, 'std_time'], 2)
            col4.metric( 'Desvio Padrão Festival', df_aux )

        with col5:
            df_aux = (df1.loc[:, ['Festival', 'Time_taken(min)']]
                        .groupby('Festival')
                        .agg( {'Time_taken(min)': ['mean', 'std']} )
                        )
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            linhas_selecionadas = df_aux['Festival'] == 'No'
            df_aux = np.round(df_aux.loc[linhas_selecionadas, 'avg_time'], 2)
            col5.metric( 'Tempo Médio Festival', df_aux )

        with col6:
            df_aux = (df1.loc[:, ['Festival', 'Time_taken(min)']]
                        .groupby('Festival')
                        .agg( {'Time_taken(min)': ['mean', 'std']} )
                        )
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            linhas_selecionadas = df_aux['Festival'] == 'No'
            df_aux = np.round(df_aux.loc[linhas_selecionadas, 'std_time'], 2)
            col6.metric( 'Desvio Padrão Festival', df_aux )

    with st.container():
        col1, col2 = st.columns( 2 )

        with col1:
            st.title( 'Tempo Médio de Entrega por Cidade' )
            
            df_aux = df1.loc[:, ['Time_taken(min)', 'City']].groupby('City').agg(['mean', 'std']).reset_index()
            df_aux.columns = ['City', 'Time_mean', 'Time_std']

            fig = go.Figure()
            fig.add_trace( go.Bar( name='Control',
                                    x=df_aux['City'],
                                    y=df_aux['Time_mean'],
                                    error_y=dict( type='data', array=df_aux['Time_std'] ) ) )

            fig.update_layout(barmode='group')
            st.plotly_chart( fig ) 

        with col2:
            st.title( 'Distribuição da Distância' )

            df_aux = (df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']]
                        .groupby(['City', 'Type_of_order'])
                        .agg(['mean', 'std'])
                        .reset_index())
            
            df_aux.columns = ['City', 'Type_of_order', 'Time_mean', 'Time_std']

            st.dataframe( df_aux )

    with st.container():
        st.title( 'Distribuição do Tempo' )

        col1, col2 = st.columns( 2 )
        with col1:
            avg_distance = df1.loc[:, ['City', 'Distance_km']].groupby('City').mean().reset_index()

            fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['Distance_km'], pull=[0, 0.1, 0])])
            st.plotly_chart( fig )

        with col2:
            df_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg(['mean', 'std']).reset_index()
            df_aux.columns = ['City', 'Road_traffic_density', 'Time_mean', 'Time_std']

            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='Time_mean',
                            color='Time_std', color_continuous_scale='RdBu',
                            color_continuous_midpoint=np.average(df_aux['Time_std'] ) )

            st.plotly_chart( fig )
