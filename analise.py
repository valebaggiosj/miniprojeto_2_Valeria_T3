import pandas as pd


# ==============================================================
# AUTOMATIZAÇÃO DE CONSULTAS PARA ANÁLISE EXPLORATÓRIA DE DADOS 
# ==============================================================
def analise_geral_dataframe(df):

    print("--- Visão das primeiras 5 linhas ---")
    print(df.head())

    print("\n")
    print(f"--- Dimensão do dataframe unificado: {df.shape} \n")
    print("--- Tipo das colunas ---")
    print(df.info())

    print("\n")
    print("--- Estatísticas descritivas ---")
    print(df.describe(include="all").T) # transpor linhas e colunas para visualização as informações de todas as colunas do dataframe
    
    print("\n")
    print("- Mediana e Média dos campos numéricos -")
    colunas_numericas = df.select_dtypes(include="number").columns
    for col in colunas_numericas:
        print(f"-{col}")
        print(f'Mediana: {df[col].median().round(2)}')
        print(f'Média: {df[col].mean().round(2)}')

    print("\n")   
    print("--- Quantidade dados nulos ---")
    nulos = df.isnull().sum()
    porc_nulos = (df.isnull().mean() * 100).round(2)
    tabela_nulos = pd.DataFrame({
                        'Qtd Nulos': nulos,
                        '% Nulos': porc_nulos
                    })    
    print(tabela_nulos)

    print("\n")
    print("--- Contabilizar valores diferentes ---")
    colunas_texto = df.select_dtypes(include="str").columns
    for col in colunas_texto:
        qtd_registros_repetidos = df[col].value_counts()
        porc_registros_repetidos = (df[col].value_counts(normalize=True) * 100).round(2)
        tabela_registros_repetidos = pd.DataFrame({
                                        'Qtd Registros Repetidos': qtd_registros_repetidos,
                                        '% Registros Repetidos': porc_registros_repetidos
                                    })           
        print(tabela_registros_repetidos)
    print("\n")

def verificar_linhas_com_dados_nulos(df, coluna):
    if (coluna != ""):
        print(f'-- Linhas com dado nulos no campo {coluna}')
        print(df[df[coluna].isnull()])
    else:
        print(df.isnull().sum())
    print("\n")


# ==============================================================


# Carregando os arquivos para dataframes 
df_salarios_dep_cargo = pd.read_csv("query_01.csv", sep=",", encoding="utf-8")
df_funcionarios_localizacao = pd.read_csv("query_02.csv", sep=",", encoding="utf-8")


analise_geral_dataframe(df_salarios_dep_cargo)
print("\n")
analise_geral_dataframe(df_funcionarios_localizacao)
print("\n")


# ==============================================================
# TRATAMENTO DOS DADOS
# ==============================================================
#   1. Para o departamento nulo, verificar quais departamentos estão relacionado ao cargo da funcionária Kimberely Grant.
departamento_encontrado = df_salarios_dep_cargo[df_salarios_dep_cargo["CARGO"] == "Sales Representative"]["DEPARTAMENTO"].dropna().unique()
print(f"Departamento: {departamento_encontrado}")
# Para o cargo de Sales Representative só tem identificado o departamento Sales, portanto, estarei atualizando o campo com esse dado
df_salarios_dep_cargo.loc[df_salarios_dep_cargo["NOME_COMPLETO"] == "Kimberely Grant", "DEPARTAMENTO"] = "Sales"
print("\n") 
#
#   2. Para o código postal nulo, verificar se o mesmo endereço está listado para outro funcionário
#   FONTE: https://www.gov.uk/guidance/local-government-structure-and-elections#electoral-areas
codigo_encontrado = df_funcionarios_localizacao[df_funcionarios_localizacao["ENDERECO"].str.contains("Arthur St", case=False)]["CODIGO_POSTAL"].dropna().unique()
print(f"Código Postal: {codigo_encontrado}")
print(f'Linhas com registros que tenham London como CIDADE: {df_funcionarios_localizacao[df_funcionarios_localizacao["CIDADE"] == "London"]}')
# Verificado que na Inglaterra, as áreas se dividem em condados e distritos, e cada um deles tem subdivisões que variam. 
# Tem um conselho para a cidade de Londres e tem outros para cada distrito da região de Londres.  
# Como Oxford está considerando a mesma nomenclatura para a coluna ESTADO, vou seguir a mesma lógica para a cidade de Londres.
df_funcionarios_localizacao.loc[df_funcionarios_localizacao["NOME_COMPLETO"] == "Susan Jacobs", "ESTADO"] = "London"
print("\n")   
# Já para o campo do CEP, vou atualizar como "Não informado", pois não achei essa informação no site. 
df_funcionarios_localizacao.loc[df_funcionarios_localizacao["NOME_COMPLETO"] == "Susan Jacobs", "CODIGO_POSTAL"] = "Não informado"
print("\n")   
#
# 3. Constam alguns registros nulos, mas principalmente nas colunas DATA_INICIO_TRABALHO e DATA_FIM_TRABALHO.
#    A porcentagem de dados nulos nestas duas colunas é de quase 91%, portanto, fica inviável de trabalhar com eles. Vou excluir essas colunas.
#    Estes campos poderiam trazer informações muito relevantes como: quem está ativo trabalhando na empresa,
#    quantos anos cada funcionário está trabalhando na empresa, qual é o histórico de salário dele, quais cargos teve nesse tempo, etc.
# Excluir as colunas DATA_INICIO_TRABALHO e DATA_FIM_TRABALHO do dataframe.
df_salarios_dep_cargo = df_salarios_dep_cargo.drop(columns=["DATA_INICIO_TRABALHO", "DATA_FIM_TRABALHO"])
#
# 4.Transformar o campo de data para datetime
df_salarios_dep_cargo["DATA_CONTRATACAO"] = pd.to_datetime(df_salarios_dep_cargo["DATA_CONTRATACAO"] , errors="coerce").dt.tz_localize(None)
# ==============================================================


# Unificando os dataframes para facilitar a análise dos dados.
# Junção dos dataframes através do campo NOME_COMPLETO e DEPARTAMENTO
#   escolhendo o dataframe com maior quantidade de registros para não perder informações
df_unificado = pd.merge(
        df_salarios_dep_cargo,
        df_funcionarios_localizacao,
        on=["NOME_COMPLETO", "DEPARTAMENTO"],
        how="left"
)
df_unificado = df_unificado.sort_values(by=["DEPARTAMENTO", "CARGO", "NOME_COMPLETO"])
print(df_unificado.head().T)

# Excluir linhas duplicadas
df_unificado = df_unificado.drop_duplicates(keep="first")

analise_geral_dataframe(df_unificado)

# ===============================
# OBSERVAÇÕES DA EDA
# ===============================
# - Alguns dados ficaram nulos com a junção das tabelas. Verificar se é possível preencher com dados existentes ou com "Não informado"
# - Análise dos dados:
#   CARGO
#       Os cargos com maior quantidade (quase 65%) de funcionários são: Sales Representative, Shipping Clerk e Stock Clerk.
#   DEPARTAMENTO
#       Os departamentos com maior quantidade (quase 74%) de funcionários são: Shipping e Sales. 
#   DATA_CONTRATACAO
#       O registro de contratações vai de 2011 a 2018.
#   ENDERECO, CODIGO_POSTAL, CIDADE, ESTADO
#       Identificado que 3 locais são os que tem maior quantidade (aprox. 91%) de funcionários trabalhando neles.
#   REGIAO
#       Mais da metade dos funcionários estão localizados na América


# Verificar quais registros ainda estão nulos
verificar_linhas_com_dados_nulos(df_unificado, "ENDERECO")
verificar_linhas_com_dados_nulos(df_unificado, "CIDADE")
verificar_linhas_com_dados_nulos(df_unificado, "ESTADO")
verificar_linhas_com_dados_nulos(df_unificado, "PAIS")
verificar_linhas_com_dados_nulos(df_unificado, "REGIAO")

# A funcionária "Kimberely Grant" está com os campos de localização sem preencher. Verificar se alguns deles poderiam ser preenchidos, caso contrário, popular como "Não informado"
# Verificar se o departamento Sales, está localizado em uma única CIDADE, ESTADO, PAIS e REGIAO
print(f'Linhas com registros que tenham Sales como DEPARTAMENTO: {df_unificado.loc[
                                                                        df_unificado["DEPARTAMENTO"] == "Sales", 
                                                                        ["ENDERECO", "CODIGO_POSTAL", "CIDADE", "ESTADO", "PAIS", "REGIAO"]
                                                                    ].drop_duplicates(keep="first").T
                                                                }')
print("\n")
# O DEPARTAMENTO = Sales, tem uma única localização, portanto vou atualizar os campos de "Kimberely Grant" seguindo esses dados.
df_unificado.loc[df_unificado["NOME_COMPLETO"] == "Kimberely Grant", "ENDERECO"] = "Magdalen Centre, The Oxford Science Park"
df_unificado.loc[df_unificado["NOME_COMPLETO"] == "Kimberely Grant", "CODIGO_POSTAL"] = "OX9 9ZB"
df_unificado.loc[df_unificado["NOME_COMPLETO"] == "Kimberely Grant", "CIDADE"] = "Oxford"
df_unificado.loc[df_unificado["NOME_COMPLETO"] == "Kimberely Grant", "ESTADO"] = "Oxford"
df_unificado.loc[df_unificado["NOME_COMPLETO"] == "Kimberely Grant", "PAIS"] = "United Kingdom of Great Britain and Northern Ireland"
df_unificado.loc[df_unificado["NOME_COMPLETO"] == "Kimberely Grant", "REGIAO"] = "Europe"


# Mostrar novamente as informações do dataframe
# Confirmado que todos os dados estão preenchidos
print(df_unificado.info())
print("\n")


# Verificar a DATA_CONTRATACAO mais antiga e mais recente
data_mais_antiga = df_unificado["DATA_CONTRATACAO"].min()
data_mais_recente = df_unificado["DATA_CONTRATACAO"].max()

print(f'A data mais antiga de contratação é {data_mais_antiga.strftime("%d/%m/%Y")}')
print(f'A data mais recente de contratação é {data_mais_recente.strftime("%d/%m/%Y")}')
print("\n")

# -- Verificar se tem outliers no campo SALARIO
# Calcular os quartis e o iqr
q1 = df_unificado["SALARIO_CONTRATADO"].quantile(0.25)
q3 = df_unificado["SALARIO_CONTRATADO"].quantile(0.75)
iqr = q3 - q1

# Definir os limites de corte
limite_inferior = q1 - 1.5 * iqr
limite_superior = q3 + 1.5 * iqr

# Filtrar os registros fora dos limites (outliers)
outliers_iqr = df_unificado[(df_unificado["SALARIO_CONTRATADO"] < limite_inferior) | (df_unificado["SALARIO_CONTRATADO"] > limite_superior)]

print(f"Total de outliers identificados por IQR: {len(outliers_iqr)}")
print(outliers_iqr.T)