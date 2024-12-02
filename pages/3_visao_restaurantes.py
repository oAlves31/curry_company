#Libraries
import pandas as pd
import re
import plotly.express as px
import folium
from haversine import haversine
import streamlit as st
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static
import plotly.graph_objects as go
import numpy as np

# =====================================================================
# Funções 
# =====================================================================
def clean_code( df1 ):
    """Esta função tem a responsabilidade de limpar o dataframe
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. REmoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica )

        Input: Dataframe
        Output: Dataframe
    """

    # Excluir as linhas 'NaN '
    df1 = df1[df1['Delivery_person_Age'] != 'NaN ']
    df1 = df1[df1['multiple_deliveries'] != 'NaN ']
    df1 = df1[df1['Road_traffic_density'] != 'NaN ']
    df1 = df1[df1['Festival'] != 'NaN ']
    df1 = df1[df1['City'] != 'NaN ']

    # Remover espaços nas colunas
    df1['ID'] = df1['ID'].str.strip()
    df1['Delivery_person_ID'] = df1['Delivery_person_ID'].str.strip()
    df1['Road_traffic_density'] = df1['Road_traffic_density'].str.strip()
    df1['Type_of_order'] = df1['Type_of_order'].str.strip()
    df1['Type_of_vehicle'] = df1['Type_of_vehicle'].str.strip()
    df1['City'] = df1['City'].str.strip()
    df1['Festival'] = df1['Festival'].str.strip()

    # Converter a coluna 'Delivery_person_Age' para inteiro
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    # Converter a coluna 'Delivery_person_Ratings' para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # Converter a coluna 'Order_Date' para o formato de data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # Converter a coluna 'multiple_deliveries' para inteiro
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # Extrair apenas os números da coluna 'Time_taken(min)'
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: int(re.findall(r'\d+', x)[0]))
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    # Resetar o índice
    df1 = df1.reset_index(drop=True)

    return df1

def avg_distance_by_city( df1 ):
    col = ['Restaurant_latitude', 
        'Restaurant_longitude', 
        'Delivery_location_latitude', 
        'Delivery_location_longitude']
    df1['distance'] = (df1.loc[ :, col]
                         .apply( lambda x: haversine(
                        (x['Restaurant_latitude'], x['Restaurant_longitude']),
                        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
    
    avg_distance = df1['distance'].mean()
    return avg_distance

def avg_time_deliver_by_city( df1 ):
    col = ['Restaurant_latitude', 
            'Restaurant_longitude', 
            'Delivery_location_latitude', 
            'Delivery_location_longitude']
    df1['distance'] = df1.loc[ :, col].apply( lambda x: haversine(
                                    (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
    avg_distance_graph = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    fig = go.Figure(data=[go.Pie(labels=avg_distance_graph['City'], values=avg_distance_graph['distance'], pull=[0, 0.1, 0])])
   
    fig.update_layout(width=1200, height=700)
    return fig

def avg_std_deliver_by_city( df1 ):
    df_aux = df1.groupby('City')['Time_taken(min)'].agg(['mean', 'std']).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                        x=df_aux['City'],
                        y=df_aux['mean'],
                        error_y=dict(type='data', array=df_aux['std'])))
    
    fig.update_layout(barmode='group', width=650, height=500)
    return fig

def avg_std_deliver_by_city_traffic( df1 ):
    df_aux = (df1.groupby(['City', 'Road_traffic_density'])['Time_taken(min)']
                 .agg(['mean', 'std'])
                 .reset_index())
    
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='mean',
                    color='std', color_continuous_scale='RdBu',
                    color_continuous_midpoint=np.average(df_aux['std']))
    fig.update_layout(width=800, height=500)
    return fig

#===========================Início da Lógica do Código======================================

# Import dataset
df = pd.read_csv( '../dataset/train.csv' )

#Limpando os dados
df1 = clean_code( df )

# ==============================================================================
# Sidebar
# ==============================================================================
st.set_page_config( page_title='Visao Restaurantes', page_icon='🍽️', layout="wide")

st.header('Marketplace - Visão Restaurantes')

#image_path = '/home/eric/Documents/comunidade_ds/ftc_programacao_python/repos/logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width=180)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY'
)

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

conditions = st.sidebar.multiselect(
    'Quais as condições climáticas?',
    ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
    'conditions Cloudy', 'conditions Fog', 'conditions Windy'],
    default=['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
    'conditions Cloudy', 'conditions Fog', 'conditions Windy']
)

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered By Comunidade DS')

# Filtro data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro traffic
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# Filtro condition
linhas_selecionadas = df1['Weatherconditions'].isin(conditions)
df1 = df1.loc[linhas_selecionadas, :]

# ==============================================================================
# Layout streamlit
# ==============================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.markdown('###### Entregadores únicos<br>', unsafe_allow_html=True)
            df_aux = df1['Delivery_person_ID'].nunique()
            st.markdown(f'## {df_aux}')
            
        with col2:
            avg_distance = avg_distance_by_city( df1 )
            st.markdown('###### Distância Média<br>', unsafe_allow_html=True)
            st.markdown(f'## {avg_distance:.2f}')

        with col3:
            st.markdown('###### Tempo Médio de Entrega c/ Festival')
            df_aux = df1.groupby('Festival')['Time_taken(min)'].agg(['mean', 'std']).reset_index()
            avg_delivery_festival = df_aux.loc[df_aux['Festival'] == 'Yes', 'mean']
            st.markdown(f'## {avg_delivery_festival.iloc[0]:.2f}')

        with col4:
            st.markdown('###### Desvio Padão de Entrega c/ Festival')
            df_aux = df1.groupby('Festival')['Time_taken(min)'].agg(['mean', 'std']).reset_index()
            avg_delivery_festival = df_aux.loc[df_aux['Festival'] == 'Yes', 'std']
            st.markdown(f'## {avg_delivery_festival.iloc[0]:.2f}')
            
        with col5:
            st.markdown('###### Tempo Médio de Entrega s/ Festival')
            df_aux = df1.groupby('Festival')['Time_taken(min)'].agg(['mean', 'std']).reset_index()
            avg_delivery_festival = df_aux.loc[df_aux['Festival'] == 'No', 'mean']
            st.markdown(f'## {avg_delivery_festival.iloc[0]:.2f}')

        with col6:
            st.markdown('###### Desvio Padão de Entrega s/ Festival')
            df_aux = df1.groupby('Festival')['Time_taken(min)'].agg(['mean', 'std']).reset_index()
            avg_delivery_festival = df_aux.loc[df_aux['Festival'] == 'No', 'std']
            st.markdown(f'## {avg_delivery_festival.iloc[0]:.2f}')

    with st.container():
        st.markdown("""---""")
        st.markdown(
                """
                <h1 style="text-align: center;">Tempo Médio de Entrega por Cidade</h1>
                """, 
                unsafe_allow_html=True
            )
        fig = avg_time_deliver_by_city( df1 )
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("""---""")
        st.markdown(
                """
                <h1 style="text-align: center;">Distribuição do Tempo</h1>
                """, 
                unsafe_allow_html=True
            )
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Tempo médio e desvio padrão de entrega por cidade.')
            fig = avg_std_deliver_by_city( df1 )
            st.plotly_chart(fig)

        with col2:
            st.markdown('##### Tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego.')
            fig = avg_std_deliver_by_city_traffic( df1 )
            st.plotly_chart(fig)

        
    with st.container():
        st.markdown("""---""")
        st.markdown(
                """
                <h1 style="text-align: center;">Distribuição da Distância</h1>
                """, 
                unsafe_allow_html=True
            )
        df_aux = (df1.groupby(['City', 'Type_of_order'])['Time_taken(min)']
                    .agg(['mean', 'std'])
                    .reset_index())
        st.dataframe(df_aux, use_container_width=True)

        