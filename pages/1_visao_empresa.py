import pandas as pd
import re
import plotly.express as px
import folium
from haversine import haversine
import streamlit as st
import datetime as dt
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide')

# -----------------------------------------
# Funções
# -----------------------------------------

def clean_code( df1 ):
    ''' Esta função tem a responsabilidade de limpar o dataframe

        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna dos dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica )

        Input: Dataframe
        Output: Dataframe
    '''
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
    
    return df1

def order_metric( df1 ):
    df_aux = (df1.loc[:, ['ID', 'Order_Date']]
                 .groupby( 'Order_Date' )
                 .count()
                 .reset_index()
            )

    fig = px.bar( df_aux, 
            x='Order_Date',
            y='ID',
            labels={
                'Order_Date': 'Order Date',
                'ID': 'Number of Orders',
            },
            title='Number of Orders by Date'
            )
        
    fig.update_layout(
    title={
        'text': 'Number of Orders by Date',
        'y':0.9,  
        'x':0.5,  
        'xanchor': 'center',  
        'yanchor': 'top'  
    }
    )
    return fig

def orders_traffic_type( df1 ):
    df_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
            .groupby('Road_traffic_density')
            .count()
            .reset_index())
    
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    
    fig = px.pie(df_aux, 
                values='entregas_perc', 
                names='Road_traffic_density',
                title='Orders by Traffic Type'
                )
    
    fig.update_layout(
    title={
    'text': 'Orders by Traffic Type',
    'y':0.9,  
    'x':(0.35),  
    'xanchor': 'center',  
    'yanchor': 'top'  
    }
    )  
    return fig 

def order_volume_by_city( df1 ):
    df_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                 .groupby( ['City', 'Road_traffic_density'] )
                 .count()
                 .reset_index())

    fig = px.scatter( df_aux, x='City', 
                    y='Road_traffic_density', 
                    size='ID', 
                    color='City',
                    labels={
                            'Road_traffic_density': 'Road Traffic Density',
                    },
                    title='Order Volume by City and Traffic Type'
                    )
    return fig

def orders_by_weak( df1 ):
    df1[ 'weak_of_year' ] = df1[ 'Order_Date' ].dt.strftime( '%U' )
    df_aux = df1.loc[:, ['ID', 'weak_of_year']].groupby('weak_of_year').count().reset_index()

    fig = px.line(df_aux, 
                x='weak_of_year', 
                y='ID',
                title='Orders by Weak',
                labels={
                    'weak_of_year': 'Weak of Year',
                    'ID': 'Numbers of Orders'
                }
                )
    
    fig.update_layout(
        title={
            'text': 'Orders by Weak',
            'y':0.9,  
            'x':(0.5),  
            'xanchor': 'center',  
            'yanchor': 'top'  
        }
        )
    return fig

def orders_by_deliver( df1 ):
    df_aux01 = (df1.loc[:, ['ID', 'weak_of_year']]
                .groupby('weak_of_year')
                .count()
                .reset_index())
    
    df_aux02 = (df1.loc[:, ['Delivery_person_ID', 'weak_of_year']]
                .groupby('weak_of_year')
                .nunique()
                .reset_index())

    df_aux = pd.merge( df_aux01, df_aux02, how='inner' )
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    fig = px.line( df_aux, 
                    x='weak_of_year', 
                    y='order_by_deliver',
                    title='Orders by Delivery Person by Weak',
                    labels={
                        'weak_of_year': 'Weak of Year',
                        'order_by_deliver': 'Order by Deliver'
                    }
                    )
    
    fig.update_layout(
        title={
            'text': 'Orders by Deliver by Weak',
            'y':0.9,  
            'x':(0.5),  
            'xanchor': 'center',  
            'yanchor': 'top'  
        }
        )
    return fig

def print_map( df1 ):
    df_aux = (df1
            .loc[:, ['City', 
                    'Road_traffic_density', 
                    'Delivery_location_latitude', 
                    'Delivery_location_longitude'
                    ]
                    ]
                    
            .groupby(['City', 'Road_traffic_density'])
            .median()
            .reset_index()
)

    map_ = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'], 
                        location_info['Delivery_location_longitude']],
                        popup=df_aux[['City', 'Road_traffic_density']]).add_to( map_ )

    folium_static( map_, width=1024, height=600 )

# ------------------ Início da Estrutura Lógica do Código ---------------------

df = pd.read_csv('dataset/train.csv')
df1 = clean_code( df )

# Visão Empresa
# ===========================================
# Side Bar
# ===========================================
st.header( 'Marketplace - Visão Cliente' )

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

st.sidebar.markdown( '''---''' )

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown( '''---''' )
st.sidebar.markdown( '### Powered by Comunidade DS' )

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

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

# ===========================================
# Layout
# ===========================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    with st.container():
        fig = order_metric( df1 )
        st.plotly_chart( fig, use_container_width=True )

    with st.container():
        col1, col2 = st.columns( 2 )

        with col1:
            fig = orders_traffic_type( df1 )
            st.plotly_chart( fig, use_container_width=True )

        with col2:
            fig = order_volume_by_city( df1 )
            st.plotly_chart( fig, use_container_width=True )

with tab2:
    with st.container():
        fig = orders_by_weak( df1 )
        st.plotly_chart( fig, use_container_width=True)

    with st.container():
        fig = orders_by_deliver( df1 )
        st.plotly_chart( fig, use_container_width=True )

with tab3:
    st.markdown( '# Country Maps ' )
    print_map( df1 )
