import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch  # para a legenda de cores
import seaborn as sns


# Declaração de constantes
COR_AZUL = "#578ac0"
COR_VERDE = "#419B9B"



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



# ==============================================================
# GRÁFICOS E ANÁLISE DELES
# ==============================================================
#
# 1. BOXPLOT: SALÁRIOS PARA VISUALIZAR OUTLIERS
# 2. PAINEL COM GRÁFICO EM BARRAS HORIZONTAL:
#    a. MEDIANA SALARIAL POR CARGO
#    b. MEDIANA SALARIAL POR DEPARTAMENTO
#    C. TOTAL SALARIAL POR CARGO
#    D. TOTAL SALARIAL POR DEPARTAMENTO
# 3. PLOTTAGEM: ADEQUAÇÃO SALARIAL: ESTIPULADO X CONTRATADO
# 4. STRIP PLOT: SALÁRIO DE CADA FUNCIONÁRIO POR REGIÃO
# 5. GRÁFICO DE BARRAS VERTICAL: SALÁRIO POR CARGO, AGRUPADO POR CIDADE


# 1. Cria a pasta 'graficos' caso ela ainda não exista
os.makedirs("graficos", exist_ok=True)

# -------------------------------------------------------------------------------------
# 1. BOXPLOT: SALÁRIOS PARA VISUALIZAR OUTLIERS
# -------------------------------------------------------------------------------------

plt.figure(num="Outliers dos Salários", figsize=(6, 4))
sns.set_style("whitegrid")
plt.boxplot(x=df_unificado["SALARIO_CONTRATADO"], vert=False)
plt.title("Outliers dos Salários", fontweight="bold")
plt.xlabel("SALÁRIO")
plt.grid(axis="x", linestyle="--", alpha=0.5)
plt.savefig("graficos/01_boxplot_salarios_outliers.png", dpi=300, bbox_inches="tight")
plt.show()

# ANÁLISE:
#   Na comparação de todos os salários, o presidente da empresa é o único outlier. 
#   Devido ao cargo, faz sentido ter uma diferença com relação aos outros cargos.


# -----------------------------------------------------------------------------------
# 2. PAINEL (2x2): MEDIANA E TOTAL SALARIAL, POR CARGO E POR DEPARTAMENTO
# -----------------------------------------------------------------------------------

# --- PREPARAÇÃO DOS DADOS ---
# Por cargo: mediana, soma e n (quantidade de funcionários do cargo)
resumo_cargo = (
    df_unificado.groupby("CARGO")["SALARIO_CONTRATADO"]
    .agg(mediana="median", soma="sum", n="count")
)

# Por departamento: mediana, soma e n (quantidade de funcionários do departamento)
resumo_dep = (
    df_unificado.groupby("DEPARTAMENTO")["SALARIO_CONTRATADO"]
    .agg(mediana="median", soma="sum", n="count")
)

# Cada tabela ordenada pela métrica do seu gráfico
mediana_cargo = resumo_cargo.sort_values("mediana", ascending=True)
mediana_dep = resumo_dep.sort_values("mediana", ascending=True)
total_cargo = resumo_cargo.sort_values("soma", ascending=True)
total_dep = resumo_dep.sort_values("soma", ascending=True)

# --- CORES POR DEPARTAMENTO ---
depto_do_cargo = df_unificado.groupby("CARGO")["DEPARTAMENTO"].first()

# Uma cor para cada departamento
lista_deptos = sorted(df_unificado["DEPARTAMENTO"].unique())
cor_depto = dict(zip(lista_deptos, sns.color_palette("tab10") + [(0.25, 0.25, 0.25)]))

# Cores na mesma ordem das barras de cada gráfico
cores_mediana_cargo = [cor_depto[depto_do_cargo[c]] for c in mediana_cargo.index]
cores_mediana_dep = [cor_depto[d] for d in mediana_dep.index]
cores_total_cargo = [cor_depto[depto_do_cargo[c]] for c in total_cargo.index]
cores_total_dep = [cor_depto[d] for d in total_dep.index]


# --- CONSTRUÇÃO DO PAINEL ---
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(
                                    2, 2, num="Painel de Salários por Cargo e por Departamento", figsize=(20, 10)
                                )

# --- Gráfico 1: Mediana por Cargo ---
bars1 = ax1.barh(mediana_cargo.index, mediana_cargo["mediana"], color=cores_mediana_cargo)
ax1.set_title("Mediana Salarial por Cargo", fontsize=12, fontweight="bold")
ax1.set_xlim(0, mediana_cargo["mediana"].max() * 1.3)
ax1.grid(axis="x", linestyle="--", alpha=0.5)
for bar, n in zip(bars1, mediana_cargo["n"]):
    valor = bar.get_width()
    ax1.text(valor + mediana_cargo["mediana"].max() * 0.01, bar.get_y() + bar.get_height() / 2,
             f"{valor:,.2f} (n={n})", va="center", fontsize=9, fontweight="bold")

# --- Gráfico 2: Mediana por Departamento ---
bars2 = ax2.barh(mediana_dep.index, mediana_dep["mediana"], color=cores_mediana_dep)
ax2.set_title("Mediana Salarial por Departamento", fontsize=12, fontweight="bold")
ax2.set_xlim(0, mediana_dep["mediana"].max() * 1.3)
ax2.grid(axis="x", linestyle="--", alpha=0.5)
for bar, n in zip(bars2, mediana_dep["n"]):
    valor = bar.get_width()
    ax2.text(valor + mediana_dep["mediana"].max() * 0.01, bar.get_y() + bar.get_height() / 2,
             f"{valor:,.2f} (n={n})", va="center", fontsize=9, fontweight="bold")

# --- Gráfico 3: Total por Cargo ---
bars3 = ax3.barh(total_cargo.index, total_cargo["soma"], color=cores_total_cargo)
ax3.set_title("Total Salarial por Cargo", fontsize=12, fontweight="bold")
ax3.set_xlim(0, total_cargo["soma"].max() * 1.3)
ax3.grid(axis="x", linestyle="--", alpha=0.5)
for bar, n in zip(bars3, total_cargo["n"]):
    valor = bar.get_width()
    ax3.text(valor + total_cargo["soma"].max() * 0.01, bar.get_y() + bar.get_height() / 2,
             f"{valor:,.0f} (n={n})", va="center", fontsize=9, fontweight="bold")

# --- Gráfico 4: Total por Departamento ---
bars4 = ax4.barh(total_dep.index, total_dep["soma"], color=cores_total_dep)
ax4.set_title("Total Salarial por Departamento", fontsize=12, fontweight="bold")
ax4.set_xlim(0, total_dep["soma"].max() * 1.3)
ax4.grid(axis="x", linestyle="--", alpha=0.5)
for bar, n in zip(bars4, total_dep["n"]):
    valor = bar.get_width()
    ax4.text(valor + total_dep["soma"].max() * 0.01, bar.get_y() + bar.get_height() / 2,
             f"{valor:,.0f} (n={n})", va="center", fontsize=9, fontweight="bold")

plt.savefig("graficos/02_painel_salarios_por_cargo_e_departamento.png", dpi=300, bbox_inches="tight")
plt.show()
# ANÁLISE
#   Analisando os salário, as áreas executivas e de gestão possuem são os mais bem pagos. Já os que trabalham com atendimento, 
#   como as áreas de Expedição, Compras e Estoque, possuem os menores salários e tem a maior concentração de funcionários. 
#   Tendo como exceção o departamento de vendas que, tanto os gerentes como os representantes de venda, possuem salários altos e com pouca diferença entre eles. 
#   Por exemplo, se o comparamos com o departamento de Marketing, vemos uma diferença salarial entre os cargos:
#   
#   Gerente de Marketing 	13.000 
#   Repres. de Marketing  	 6.000
#   Diferença		         7.000 (mais que o dobro do salário do Representante)
#   
#   Gerente de Vendas	12.000
#   Repres. de Vendas	 8.200 
#   Diferença		     3.200 (bem menos que a metade do salário do Representante)
#   
#   Sendo que no Marketing tem 2 funcionários. Ou seja, um gerente e um representante.
#   Se vemos o departamento de Compras, o gerente tem um salário de 4x mais que os cargos de atendente (sendo 5 funcionários a cargo).
#   O setor de TI conta com 5 programadores e não tem nenhum cargo de liderança atrelado. 
#   Segue realmente uma hierarquia horizontal ou tem uma pessoa que é procurada para responder pela área, mas não está com o cargo correspondente?
#
#   No gráfico, o departamento de VENDAS é o segundo com maior concentração de funcionários e o que tem maior custo salarial, 
#   pouco mais do dobro comparado ao departamento de EXPEDIÇÃO que tem mais funcionários. 
#   Seria interessante poder verificar se o trabalhado por esse setor está compensando para manter a quantidade de funcionários e o salário.


# -----------------------------------------------------------------------------------
# 3. PLOTTAGEM: ADEQUAÇÃO SALARIAL: ESTIPULADO X CONTRATADO
# -----------------------------------------------------------------------------------

# Agrupa os valores de Salário Mínimo, Máximo e Contratado (mediana) por Cargo
faixa_salarial = df_unificado.groupby("CARGO").agg(
                    sal_min=("SALARIO_MIN", "min"),
                    sal_max=("SALARIO_MAX", "max"),
                    sal_mediano=("SALARIO_CONTRATADO", "median")
                ).sort_values(by="sal_mediano", ascending=True)

plt.figure(num="Adequação Salarial: Faixa Estipulada vs. Salário Contratado", figsize=(10, 6))

# Plota a linha da faixa salarial
plt.hlines(
    y=faixa_salarial.index, 
    xmin=faixa_salarial["sal_min"], 
    xmax=faixa_salarial["sal_max"], 
    color="gray", 
    alpha=0.6, 
    linewidth=4, 
    label="Faixa Salarial Estipulada (Min - Max)"
)

# Plota o ponto com a mediana do Salário Contratado
plt.scatter(
    faixa_salarial["sal_mediano"], 
    faixa_salarial.index, 
    color=COR_VERDE, 
    s=100, 
    zorder=3, 
    label="Mediana Salarial"
)

plt.title("Adequação Salarial: Faixa Estipulada vs. Salário Contratado", fontsize=12, fontweight="bold")
plt.xlabel("SALÁRIO")
plt.ylabel("CARGO")
plt.legend(loc="lower right")
plt.grid(axis="x", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig("graficos/03_adequacao_salarial.png", dpi=300, bbox_inches="tight")
plt.show()
# ANÁLISE
#   No gráfico de adequação salarial, também podemos verificar, com análise prévia de indicadores, se os salários estão adequados. 
#   Alguns cargos estão perto do salário mínimo estipulado, principalmente dos funcionários com menos salário (4 dos 7 cargos). 
#   Outros 5 cargos estão perto ou chegando no máximo do range salarial estipulado, são eles: Contabilidade, Contabilidade Pública, Gerente de estoque, Gerente de Marketing e Relações públicas.
#   Os outros cargos estão na media da faixa salarial. 
#   Revisar se as faixas salariais estão dentro da competitividade salarial do mercado e se os salários, próximos no mínimo e no máximo da faixa, precisam de algum reajuste.


# -----------------------------------------------------------------------------------
# 4. STRIP PLOT: SALÁRIO DE CADA FUNCIONÁRIO POR REGIÃO 
# -----------------------------------------------------------------------------------

# Mesma cor de cada departamento usada no gráfico de barras por cargo/departamento
lista_deptos = sorted(df_unificado["DEPARTAMENTO"].unique())
cor_depto = dict(zip(lista_deptos, sns.color_palette("tab10") + [(0.25, 0.25, 0.25)]))
cor_regiao = {"Americas": COR_AZUL, "Europe": COR_VERDE}

# Quantidade de funcionários por região (da maior para a menor)
qtd_regiao = df_unificado["REGIAO"].value_counts()
ordem_regiao = qtd_regiao.index.tolist()

plt.figure(num="Salário de cada Funcionário por Região", figsize=(11, 6))

# Cada ponto = 1 funcionário (jitter --> espalha os pontos para não ficarem em cima uns dos outros)
ax = sns.stripplot(
    data=df_unificado, x="REGIAO", y="SALARIO_CONTRATADO", hue="DEPARTAMENTO",
    order=ordem_regiao, palette=cor_depto,
    size=8, jitter=0.25, alpha=0.85, edgecolor="white", linewidth=0.5
)

# Linha tracejada preta = mediana salarial da região
for i, regiao in enumerate(ordem_regiao):
    mediana = df_unificado.loc[df_unificado["REGIAO"] == regiao, "SALARIO_CONTRATADO"].median()
    ax.hlines(mediana, i - 0.4, i + 0.4, color="black", linestyles="--", linewidth=2, zorder=3)
    ax.text(i + 0.42, mediana, f"mediana\n{mediana:,.0f}", va="center", fontsize=9, fontweight="bold")

# Nome da região indicando a quantidade de funcionários (n) 
ax.set_xticks(range(len(ordem_regiao)))
ax.set_xticklabels([f"{r}\n(n={qtd_regiao[r]})" for r in ordem_regiao])
ax.set_xlim(-0.5, len(ordem_regiao) - 0.5 + 0.35)

plt.title("Salário de cada Funcionário por Região", fontsize=12, fontweight="bold")
plt.ylabel("SALÁRIO")
plt.legend(title="DEPARTAMENTO", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
plt.grid(axis="y", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig("graficos/04_salario_por_regiao.png", dpi=300, bbox_inches="tight")
plt.show()
# ANÁLISE
#   São 70 funcionários na América e 37 na Europa.
#   Na Europa, encontramos 3 departamentos da empresa: Vendas, Recursos Humanos e Relações Públicas (acabou ficando escondido atrás de outro ponto e não ficou muito visível - confirmado no gráfico seguinte).
#   Os salários estão mais próximos, se comparado com os salários na América
#   Já na América, notamos maior diferencia de salários devido à concentração de ter mais departamentos e contar com mais cargos de gerentes e executivos. 
#       Mesmo assim, por ter mais quantidade de funcionários, a mediana do salário ficou abaixo da mediana de Europa.
#   Devido à concentração de cargos executivos na América, aqui parece ser a central da empresa.


# -----------------------------------------------------------------------------------
# 5. GRÁFICO DE BARRAS VERTICAL: SALÁRIO POR CARGO, AGRUPADO POR CIDADE
# -----------------------------------------------------------------------------------

# --- PREPARAÇÃO DOS DADOS ---
# Mediana salarial, maior salário e n (quantidade de funcionários) de cada cargo em cada cidade
resumo_cc = (
    df_unificado.groupby(["REGIAO", "CIDADE", "CARGO"])["SALARIO_CONTRATADO"]
    .agg(mediana="median", maximo="max", n="count")
    .reset_index()
)

# Ordem das cidades: por região e, dentro da região, da que tem mais funcionários para a que tem menos
total_cidade = (
    df_unificado.groupby(["REGIAO", "CIDADE"]).size().reset_index(name="total")
    .sort_values(["REGIAO", "total"], ascending=[True, False])
)

# Posição de cada barra no eixo X: cargos de uma mesma cidade ficam juntos, com um espaço entre as cidades
resumo_cc["POS"] = np.nan
centros_cidade = {}
pos = 0
for _, linha in total_cidade.iterrows():
    cargos_da_cidade = resumo_cc[resumo_cc["CIDADE"] == linha["CIDADE"]].sort_values("mediana", ascending=False)
    primeira = pos
    for idx in cargos_da_cidade.index:
        resumo_cc.loc[idx, "POS"] = pos
        pos += 1
    centros_cidade[linha["CIDADE"]] = (primeira, pos - 1)
    pos += 1  # espaço entre as cidades
resumo_cc = resumo_cc.sort_values("POS")

# Salário de cada funcionário (para os pontinhos): leva junto a posição da barra do seu cargo
pontos = df_unificado.merge(resumo_cc[["CIDADE", "CARGO", "POS"]], on=["CIDADE", "CARGO"])
rng = np.random.default_rng(42)
pontos["POS_JITTER"] = pontos["POS"] + rng.uniform(-0.25, 0.25, len(pontos))


# --- CONSTRUÇÃO DO GRÁFICO ---
fig, ax = plt.subplots(num="Salário por Cargo, agrupado por Cidade", figsize=(16, 8))

# Barras = mediana salarial do cargo; cor = região
ax.bar(
    resumo_cc["POS"], resumo_cc["mediana"],
    color=[cor_regiao[r] for r in resumo_cc["REGIAO"]], width=0.8, alpha=0.85,
)

# Rótulo: mediana e n, acima do maior salário do cargo (para não ficar embaixo dos pontinhos)
for _, linha in resumo_cc.iterrows():
    ax.text(linha["POS"], linha["maximo"] + 300, f"{linha['mediana']:,.0f}\n(n={linha['n']})",
            ha="center", va="bottom", fontsize=8, fontweight="bold")

# Nome dos cargos embaixo de cada barra
ax.set_xticks(resumo_cc["POS"])
ax.set_xticklabels(resumo_cc["CARGO"], rotation=60, ha="right", fontsize=9)

# Nome da cidade no topo de cada grupo, com uma linha na cor da região
limite_y = df_unificado["SALARIO_CONTRATADO"].max() * 1.22
ax.set_ylim(0, limite_y)
for _, linha in total_cidade.iterrows():
    primeira, ultima = centros_cidade[linha["CIDADE"]]
    cor = cor_regiao[linha["REGIAO"]]
    ax.hlines(limite_y * 0.96, primeira - 0.4, ultima + 0.4, color=cor, linewidth=4)
    ax.text((primeira + ultima) / 2, limite_y * 0.975, f"{linha['CIDADE']} ({linha['total']})",
            ha="center", va="bottom", fontsize=10, fontweight="bold")

ax.set_title("Salário por Cargo, agrupado por Cidade", fontsize=12, fontweight="bold", pad=25)
ax.set_xlabel("CARGO (agrupado por cidade; número entre parênteses = funcionários em cada cidade)")
ax.set_ylabel("SALÁRIO CONTRATADO (barra = mediana)")
ax.grid(axis="x", visible=False)  # tira as linhas verticais que cortam as barras
ax.grid(axis="y", linestyle="--", alpha=0.5)
ax.set_axisbelow(True)
ax.legend(handles=[Patch(color=c, label=r) for r, c in cor_regiao.items()], title="Região", loc="upper right",
          bbox_to_anchor=(1.0, 0.9))

plt.tight_layout()
plt.savefig("graficos/05_salario_por_cargo_e_cidade.png", dpi=300, bbox_inches="tight")
plt.show()
# ANÁLISE
#   O departamento executivo se localiza em Seattle junto com outros cargos gerenciais, enquanto que outros funcionários se espalham por algumas cidades. 
#   Mas a cidade com maior quantidade de funcionários é San Francisco na América, seguida por Oxford na Europa, onde se encontra todo o departamento de Vendas.
#   No dataframe não tinha informação de quantas filias tem a empresa, mas como em alguns casos poucas pessoas estão localizadas em determinada cidade, 
#       estou deduzindo que elas poderiam em situação de trabalho remoto. Tomando como exemplo o departamento de Marketing que é o que tem um maior valor no total de salários, 
#       podemos nos perguntar se eles estão em trabalho remoto e porquê todos estão localizados em Oxford. Isso está relacionado com o alto valor de salários, comparado com outros departamentos?
#       Mudaria considerando a contratação remota em diversas partes do mundo? Essa mudança afetaria os indicadores atuais da área? 
#       Essas são algumas perguntas que não encontro nesse dataframe, mas que podem ajudar o RH a analisar os dados do departamento.
# 
# 
# 
# ==============================================================
# CONCLUSÃO GERAL:
# ==============================================================
#   Tem informações que estão faltando e seriam muito importantes para continuar uma análise mais profunda. Algum dos dados faltantes são as datas de inicio de fim de contrato, pois, 
#       com base nos dados do sistema, não sabemos se os funcionários estão ativos ou não. As data de inicio e fim de trabalho estavam vazias quase na sua totalidade, 
#       e as poucas informações pareciam estar com datas sem relação sequencial.
#   Poderia ser montado um gráfico para comparar as lideranças dos diferentes departamentos, mas procurar pelo nome para fazer essa separação ficaria mais moroso do que adicionar uma nova coluna
#       no BD identificando o tipo de cargo de cada funcionário.
#   Seria interessante podem analisar os indicadores de cada departamento para entender essas diferenças entre os gerentes e seus funcionários, 
#       confirmar se os salários correspondentes às responsabilidades e se acompanham os retornos financeiros que a empresa estipula para cada departamento e cargo. 
#   A empresa tem funcionários em várias regiões, e tem que levar em consideração os impostos/taxas, o custo de vida e outras influências que cada região trás e interfere nos contratos de trabalho.
#        Analisar se é vantajoso contratar na modalidade home office em diversas cidades, mesmo para cargos em um mesmo departamento, 
#       ou se a contratação híbrida ou presencial numa filial já existente, compensa.


