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

# Funções
def clean_code( df1 ):
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

def top_delivers( df1, top_asc ):
    df_aux = (df1.groupby(['City', 'Delivery_person_ID'])['Time_taken(min)']
                .mean()
                .reset_index()
                .sort_values(['City', 'Time_taken(min)'], ascending=top_asc))
    df_aux01 = df_aux.loc[df_aux['City'] == 'Metropolitian'].head(10)
    df_aux02 = df_aux.loc[df_aux['City'] == 'Urban'].head(10)
    df_aux03 = df_aux.loc[df_aux['City'] == 'Semi-Urban'].head(10)
    
    df2 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index( drop=True )
    return df2

#===========================Início da Lógica do Código======================================

# Import dataset
df = pd.read_csv( 'dataset/train.csv' )

#Limpando os dados
df1 = clean_code( df )

# ==============================================================================
# Sidebar
# ==============================================================================
st.set_page_config( page_title='Visao Entregadores', page_icon='🚚', layout="wide")
st.header('Marketplace - Visão Entregadores')

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
        st.title('Overal Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = df1.loc[:, "Delivery_person_Age"].max()
            st.markdown('###### Maior idade<br>', unsafe_allow_html=True)
            st.markdown(f'# {maior_idade}')

        with col2:
            menor_idade = df1.loc[:, "Delivery_person_Age"].min()
            st.markdown('###### Menor idade<br>', unsafe_allow_html=True)
            st.markdown(f'# {menor_idade}')

        with col3:
            st.markdown('###### Melhor condição de veículo')
            melhor_condicao_veiculo = df1.loc[:, "Vehicle_condition"].max()
            st.markdown(f'# {melhor_condicao_veiculo}')

        with col4:
            pior_condicao_veiculo = df1.loc[:, "Vehicle_condition"].min()
            st.markdown('###### Pior condição de veículo')
            st.markdown(f'# {pior_condicao_veiculo}')

    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por entregador')
            df_avg_rating_per_deliver = (df1.groupby('Delivery_person_ID')['Delivery_person_Ratings']
                                            .mean()
                                            .reset_index())
            st.dataframe( df_avg_rating_per_deliver, use_container_width=True )

        with col2:
            st.markdown('##### Avaliação média por trânsito')
            df_avg_std_rating_by_traffic = (df1.groupby('Road_traffic_density')['Delivery_person_Ratings']
                                              .agg(['mean', 'std'])
                                              .reset_index())
            st.dataframe( df_avg_std_rating_by_traffic, use_container_width=True )

            st.markdown('##### Avaliação média por clima')
            df_avg_std_rating_by_condition = (df1.groupby('Weatherconditions')['Delivery_person_Ratings']
                                                 .agg(['mean', 'std'])
                                                 .reset_index())
            st.dataframe(df_avg_std_rating_by_condition, use_container_width=True)

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            df2 = top_delivers( df1, top_asc=True )
            st.dataframe(df2, use_container_width=True)

        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df2 = top_delivers( df1, top_asc=False )
            st.dataframe(df2, use_container_width=True)
