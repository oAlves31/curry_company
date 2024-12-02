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

def order_metrics( df1 ):
    df_aux = (df1.loc[:, ['ID', 'Order_Date']]
                 .groupby( 'Order_Date' )
                 .count()
                 .reset_index())
    df_aux.columns = ['order_date', 'qtde_entregas']
    
    fig = px.bar( df_aux, x='order_date', y='qtde_entregas' )
    return fig

def traffic_order_share( df1 ):
    columns = ['ID', 'Road_traffic_density']
    df_aux = (df1.loc[:, columns]
                 .groupby( 'Road_traffic_density' )
                 .count()
                 .reset_index())
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum())
    
    fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )
    return fig

def traffic_order_city( df1 ):
    columns = ['ID', 'City', 'Road_traffic_density']
    df_aux = (df1.loc[:, columns]
                 .groupby( ['City', 'Road_traffic_density'] )
                 .count()
                 .reset_index())
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum())
    
    fig = px.bar( df_aux, x='City', y='ID', color='Road_traffic_density', barmode='group')
    return fig

def order_by_week( df1 ):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )
    df_aux = (df1.loc[:, ['ID', 'week_of_year']]
                 .groupby( 'week_of_year' )
                 .count()
                 .reset_index())
    
    fig = px.line( df_aux, x='week_of_year', y='ID' )
    return fig
    
def order_share_by_week( df1 ):
    df_aux1 = (df1.loc[:, ['ID', 'week_of_year']]
                  .groupby( 'week_of_year' )
                  .count()
                  .reset_index())
    df_aux2 = (df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
                  .groupby( 'week_of_year')
                  .nunique()
                  .reset_index())
    
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
    return fig

def country_maps( df1 ):
    columns = [
    'City',
    'Road_traffic_density',
    'Delivery_location_latitude',
    'Delivery_location_longitude'
    ]
    columns_groupby = ['City', 'Road_traffic_density']
    data_plot = df1.loc[:, columns].groupby( columns_groupby ).median().reset_index()
    data_plot = data_plot[data_plot['City'] != 'NaN']
    data_plot = data_plot[data_plot['Road_traffic_density'] != 'NaN']
    # Desenhar o mapa
    map_ = folium.Map( zoom_start=11 )
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )
    return map_

#===========================Início da Lógica do Código======================================

# Import dataset
df = pd.read_csv( '../dataset/train.csv' )

#Limpando os dados
df1 = clean_code( df )

# ==============================================================================
# Sidebar
# ==============================================================================
st.set_page_config( page_title='Visao Empresa', page_icon='📈', layout="wide")
st.header('Marketplace - Visão Cliente')

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

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered By Comunidade DS')

# Filtro data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro traffic
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# ==============================================================================
# Layout streamlit
# ==============================================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geogáfica'])

with tab1:
    with st.container():
        # Order metrics
        st.markdown('# Order by Day')
        fig = order_metrics( df1 )
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.header('Traffic Order Share')
            fig = traffic_order_share( df1 )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city( df1 )
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week( df1 )
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('# Order Share by Week')
        fig = order_share_by_week( df1 )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown('# Country Maps')
    map_ = country_maps( df1 )
    folium_static(map_, width=1024, height=600)