import streamlit as st
import pandas as pd
import mysql.connector

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="Análise de Vendas", layout="wide")
st.title("📊 App de Análise de Vendas")

# -------------------------------
# CONEXÃO
# -------------------------------
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1237',
    database='vendas_db'
)

# -------------------------------
# FORMATADORES
# -------------------------------
def formatar_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_percentual(valor):
    return f"{valor*100:.1f}%"

# -------------------------------
# MENU
# -------------------------------
opcao = st.selectbox("Escolha uma análise:", [
    "Receita por categoria",
    "Lucro por categoria",
    "Produtos com prejuízo",
    "Desconto vs lucro",
    "Top clientes",
    "Clientes com prejuízo",
    "Vendas por região",
    "Produtos mais vendidos",
    "Ticket médio por cliente"
])

# -------------------------------
# CONTROLE TOP N (dinâmico)
# -------------------------------
usar_top = opcao in ["Top clientes", "Produtos mais vendidos", "Produtos com prejuízo"]

if usar_top:
    top_n = st.slider("Quantidade de resultados (Top N)", 5, 50, 10)

# -------------------------------
# QUERIES BASE
# -------------------------------
queries = {
    "Receita por categoria": """
        SELECT category AS Categoria, SUM(sales) AS Receita
        FROM vendas GROUP BY category ORDER BY Receita DESC
    """,
    "Lucro por categoria": """
        SELECT category AS Categoria, SUM(profit) AS Lucro
        FROM vendas GROUP BY category ORDER BY Lucro DESC
    """,
    "Produtos com prejuízo": f"""
        SELECT product_name AS Produto, SUM(profit) AS Lucro
        FROM vendas GROUP BY product_name ORDER BY Lucro ASC
        {"LIMIT " + str(top_n) if usar_top else ""}
    """,
    "Desconto vs lucro": """
        SELECT discount AS Desconto, COUNT(*) AS Quantidade, AVG(profit) AS Lucro_Medio
        FROM vendas GROUP BY discount ORDER BY discount
    """,
    "Top clientes": f"""
        SELECT customer_name AS Cliente, SUM(sales) AS Receita
        FROM vendas GROUP BY customer_name ORDER BY Receita DESC
        {"LIMIT " + str(top_n) if usar_top else ""}
    """,
    "Clientes com prejuízo": """
        SELECT customer_name AS Cliente, SUM(profit) AS Lucro
        FROM vendas GROUP BY customer_name HAVING Lucro < 0 ORDER BY Lucro
    """,
    "Vendas por região": """
        SELECT region AS Região, SUM(sales) AS Receita, SUM(profit) AS Lucro
        FROM vendas GROUP BY region ORDER BY Receita DESC
    """,
    "Produtos mais vendidos": f"""
        SELECT product_name AS Produto, SUM(quantity) AS Quantidade
        FROM vendas GROUP BY product_name ORDER BY Quantidade DESC
        {"LIMIT " + str(top_n) if usar_top else ""}
    """,
    "Ticket médio por cliente": """
        SELECT customer_name AS Cliente, AVG(sales) AS Ticket_Médio
        FROM vendas GROUP BY customer_name ORDER BY Ticket_Médio DESC
    """
}

# -------------------------------
# EXECUTAR QUERY
# -------------------------------
df = pd.read_sql(queries[opcao], conn)

# -------------------------------
# KPI
# -------------------------------
if "Receita" in df.columns:
    st.metric("💰 Receita Total", formatar_real(df["Receita"].sum()))

elif "Lucro" in df.columns:
    st.metric("📈 Lucro Total", formatar_real(df["Lucro"].sum()))

elif "Ticket_Médio" in df.columns:
    st.metric("🧾 Ticket Médio", formatar_real(df["Ticket_Médio"].mean()))

# -------------------------------
# FORMATAÇÃO
# -------------------------------
df_display = df.copy()

for col in df_display.columns:
    if col in ["Receita", "Lucro", "Ticket_Médio"]:
        df_display[col] = df_display[col].apply(formatar_real)
    elif col == "Desconto":
        df_display[col] = df_display[col].apply(formatar_percentual)

# -------------------------------
# TABELA
# -------------------------------
st.subheader("📋 Dados")
st.dataframe(df_display, use_container_width=True)

# -------------------------------
# GRÁFICOS
# -------------------------------
st.subheader("📊 Visualização")

df_chart = df.set_index(df.columns[0])

if opcao == "Desconto vs lucro":
    st.line_chart(df_chart)

else:
    st.bar_chart(df_chart)