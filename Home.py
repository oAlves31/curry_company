import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🎲'
)

#image_path = '/home/eric/Documents/repos/projeto_01/logo.jpg'
image = Image.open( 'logo.jpg' )
st.sidebar.image( image, width=100 )

st.sidebar.markdown( '# Curry Company' )
st.sidebar.markdown( '### Fastest Delivery in Town' )
st.sidebar.markdown( '''---''' )

st.write( '# Curry Company Growth Dashboard' )

st.markdown(
    '''
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos
    Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimento do restaurante.
    ### Ask for help
        email: torre.eric@gmail.com
'''
)