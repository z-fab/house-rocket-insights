import pandas as pd
import streamlit as st
import plotly.express as px
import locale

#config Streamlit
#st.set_page_config(layout='wide')
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def get_data(path):
    df = pd.read_csv(path)
    return df

@st.cache(allow_output_mutation=True)
def set_feature(df):

    #Removendo colunas sem descrição no dicionário do dataset
    df.drop(columns=['grade', 'sqft_living15', 'sqft_lot15'], inplace=True)
    
    #Convertendo coluna date para o tipo date
    df['date'] = pd.to_datetime(df['date']) 
    
    #convertendo sqft_living, sqft_lot, sqft_above, sqft_basement de Pés Quadrados para Metros Quadrados
    df['sqft_living'] = round(df['sqft_living']*0.0929,2)
    df['sqft_lot'] = round(df['sqft_lot']*0.0929,2)
    df['sqft_above'] = round(df['sqft_above']*0.0929,2)
    df['sqft_basement'] = round(df['sqft_basement']*0.0929,2)
    
    #Renomeando colunas sqft_living, sqft_lot, sqft_above, sqft_basement para m2_living, m2_lot, m2_above, m2_basement
    new_columns = {
        'sqft_living' : 'm2_living',
        'sqft_lot' : 'm2_lot',
        'sqft_above' : 'm2_above',
        'sqft_basement' : 'm2_basement'
    }
    df.rename(columns=new_columns, inplace=True)
    
    #Alterando variável bathrooms de float para int
    df['bathrooms'] = df['bathrooms'].astype('int64')

    #convertendo Waterfront para Categorical
    df['waterfront'] = pd.Categorical(df['waterfront'])
    df['waterfront'] = df['waterfront'].cat.rename_categories({0: 'no', 1: 'yes'})

    #convertendo view para Categorical
    df['view'] = pd.Categorical(df['view'])
    df['view'] = df['view'].cat.rename_categories({0: 'no view', 1: 'fair', 2: 'average', 3: 'good', 4: 'excelent'})
    

    #convertendo condition para Categorical
    df['condition'] = pd.Categorical(df['condition'])
    df['condition'] = df['condition'].cat.rename_categories({1: 'poor', 2: 'fair', 3: 'average', 4: 'good', 5: 'very good'})

    #Removendo registros com ids duplicados e mantendo o registro mais recente
    df = df.sort_values(by='date').drop_duplicates(subset=['id'], keep='last')

    #Alterando registro com 33 quartos para 3
    df.loc[df['bedrooms'] == 33, 'bedrooms'] = 3

    return df


def set_home(df, tab):
    with tab:
        st.title('House Rocket Guide')
        st.markdown("A House Rocket (H.R.) é uma empresa de compra e venda de imóvel que atua principalmente no condado de King, no estado de Washington, EUA. Ela é uma empresa fictícia e usada aqui para ilustrar o **processo de geração de insights** através da análise e manipulação de dados para auxiliar na **tomada de decisões de negócio**.")
        st.info('Veja o repositório desse projeto no [Github](https://github.com/z-fab/project-house-rocket-insights)', icon="ℹ️")
        st.markdown("""
            ## **1. Contexto de Negócio**
            A área estratégica da House Rocket deseja encontrar as melhores oportunidades de compra e venda de imóveis para maximizar os lucros da empresa. 

            O time de negócio não consegue tomar boas decisões sem analisar os dados. O portfólio é muito grande e levaria muito tempo para realizar essa análise manualmente.

            ### **1.1 Questões**

            Foi apresentado as seguintes questões a serem respondidas com base nos dados dos imóveis encontrados no portfólio da H.R.:

            1. Quais são os imóveis que a House Rocket deveria comprar e por qual preço?

            2. Uma vez a casa comprada, qual o melhor momento para vendê-las e por qual preço?
        """)

        st.markdown("""
            ### **1.2 Dados**
            Os dados foram retirados do Kaggle e podem ser visto [aqui](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction)
        """)
        show_df = st.checkbox('Mostrar Dataframe')
        if(show_df):
            st.dataframe(df)

        with st.expander("Ver dicionário de Dados"):
            st.markdown("""
                #### **1.2.1 Dicionário de Dados**
                | Variável | Significado |
                | --- | --- |
                |id| Identificação única de cada imóvel|
                |date| Data em que o imóvel ficou disponível para venda
                |price| Valor de venda
                |bedrooms| Número de quartos
                |bathrooms| Número de banheiros, onde .5 refere-se a lavabos (i.e. sem chuveiro)
                |sqft_living| Tamanho construído do imóvel em pés quadrados
                |sqft_lot| Tamanho total do terreno em pés quadrados
                |floors| Número de andares
                |waterfront| Indica se a propriedade tem vista para a água ou não 
                |view| Um índice de 0 a 4 para a qualidade da vista da propriedade, em que:  0 = sem vista, 1 = regular 2 = média, 3 = boa, 4 = excelente
                |condition| Um índice de 1 a 5 para a integridade física da propriedade, em que: 1 = muito ruim, 2 = ruim, 3 = média, 4 = boa, 5= excelente
                |sqft_above| O tamanho do sotão do imóvel em pés quadrados
                |sqft_basement| O tamanho do porão do imóvel em pés quadrados
                |yr_built| O ano em que a propriedade foi construída 
                |yr_renovated| O ano em que o imóvel foi reformado pela última vez
                |zipcode| O zipcode do imóvel
                |lat| Latitude do imóvel
                |long| Longitude do imóvel
                |sqft_living15| O tamanho construido dos imóveis dos 15 vizinhos mais próximos (em pés quadrados)
                |sqft_lot15| O tamanho do terreno dos imóveis dos 15 vizinhos mais próximos (em pés quadrados)
            """)
            st.write(" ")
        st.markdown("""
            ### **1.3 Premissas**
            * Podem haver erros de digitação em alguns registros que devem ser tratados/removidos durante a limpeza dos dados.

            * As variáveis `sqft_living15`, `grade` e `sqft_lot15` foram desconsideradas e removidas

            * A variável `date` se refere a data em que o imóvel foi disponibilizado para venda

            * Imóveis em que a variável `yr_renovated` for igual a 0, considera-se que não passou por reformas   
        """)


    return None

def set_buy_suggest(df, df_total, tab):
    with tab:
        st.title('Sugestão de compra')

        col1, col2, col3 = st.columns(3)
        col1.metric(label="Total de Imóveis", value=df_total.shape[0])
        col2.metric(label="Imóveis para Compra", value=df.shape[0])
        percent_buy = round((df.shape[0]/df_total.shape[0])*100,2)
        col3.metric(label="% Imóveis para compra", value=str(percent_buy)+"%")
        st.write(" ")
        st.markdown("No Dataframe abaixo estão as casas recomendadas a serem compradas")
        st.dataframe(df, use_container_width=True)

        fig = px.scatter_mapbox(df, 
                                lat="lat", 
                                lon="long", 
                                color='offer_suggest',
                                zoom=10)

        fig.update_layout(mapbox_style="open-street-map")
        fig.update_traces(marker={'size': 10})
        fig.update_layout(height=800, margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig)





    return None

def set_sell_suggest(df, df_total, tab):
    with tab:
        st.title('Sugestão de Venda')

        col1, col2, col3 = st.columns(3)
        col1.metric(label="Imóveis para Venda", value=df.shape[0])

        sell_suggest_total = df['sell_suggest'].sum()/1000000
        sell_suggest_total = '$ '+str(locale.currency(sell_suggest_total, grouping=True, symbol=False)+"M")
        col2.metric(label="Valor total", value=sell_suggest_total)
        
        profit_total = df['profit'].sum()/1000000
        profit_total = '$ '+str(locale.currency(profit_total, grouping=True, symbol=False)+"M")
        col3.metric(label="Lucro total", value=profit_total)

        st.write(" ")
        st.markdown("No Dataframe abaixo estão as casas recomendadas a serem vendidas")
        st.dataframe(df, use_container_width=True)

        st.write(" ")
        st.markdown("No Dataframe abaixo estão os lucros esperados por estação do Ano")
        st.dataframe(df.groupby('season').median()['profit'].reset_index(), use_container_width=True)

        fig = px.scatter_mapbox(df, 
                                lat="lat", 
                                lon="long", 
                                color='profit',
                                zoom=10)

        fig.update_layout(mapbox_style="open-street-map")
        fig.update_traces(marker={'size': 10})
        fig.update_layout(height=800, margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig)


    return None




if __name__ == "__main__":

    df = get_data('data/kc_house_data.csv')
    df_buy = get_data('output/buy_suggest.csv')
    df_sell = get_data('output/sell_suggest.csv')
    df = set_feature(df)
    


    tabs = st.tabs(["🏠 Home", "📥 Sugestão de Compra", "📤 Sugestão de Venda"])
    set_home(df, tabs[0])
    set_buy_suggest(df_buy, df, tabs[1])
    set_sell_suggest(df_sell, df, tabs[2])

