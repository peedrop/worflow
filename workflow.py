import os
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from prefect import flow, task
from prefect.blocks.system import Secret
from prefect.artifacts import create_table_artifact, create_markdown_artifact
from prefect.variables import Variable

# 🔒 Carregar a API Key armazenada no Prefect Block
api_key_block = Secret.load("prefect-api-key")
PREFECT_API_KEY = api_key_block.get()
os.environ["PREFECT_API_KEY"] = PREFECT_API_KEY

# 📌 Obter a lista de tickers da variável JSON no Prefect
tickers_json = Variable.get("tickers")  
TICKERS = tickers_json["tickers"]

BASE_DIR = "dados_mercado"
os.makedirs(BASE_DIR, exist_ok=True)

@task(retries=3, retry_delay_seconds=5, log_prints=True)
def fetch_stock_data(tickers, days=7):
    """Baixa os últimos `days` dias de dados das ações."""
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)

    print(f"📥 Baixando dados de {start_date.date()} até {end_date.date()}...")

    try:
        df = yf.download(tickers, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        if "Close" not in df:
            print("❌ Nenhum dado de fechamento disponível.")
            return None
        
        df = df["Close"].dropna(axis=1, how="all")  # Remove tickers sem dados
        print(f"✅ Dados baixados com sucesso! ({len(df.columns)} tickers válidos)")
        return df
    except Exception as e:
        print(f"❌ Erro ao baixar dados: {e}")
        return None

@task(retries=3, retry_delay_seconds=5, log_prints=True)
def calculate_indicators(df):
    """Calcula indicadores financeiros: médias móveis e volatilidade."""
    if df is None or df.empty:
        print("❌ Sem dados para calcular indicadores.")
        return None

    indicators = pd.DataFrame()
    
    for ticker in df.columns:
        indicators[f"{ticker}_ma7"] = df[ticker].rolling(window=7).mean()  # Média Móvel de 7 dias
        indicators[f"{ticker}_volatility"] = df[ticker].pct_change().rolling(window=7).std()  # Volatilidade

    print("📊 Indicadores calculados com sucesso!")
    return indicators

@task(retries=3, retry_delay_seconds=5, log_prints=True)
def save_partitioned_data(df):
    """Salva os dados particionados por mês e dia em CSV."""
    if df is None or df.empty:
        print("❌ Nenhum dado para salvar.")
        return

    for date, data in df.iterrows():
        month_folder = os.path.join(BASE_DIR, date.strftime('%Y-%m'))
        os.makedirs(month_folder, exist_ok=True) 

        file_path = os.path.join(month_folder, f"{date.date()}.csv")
        data.to_frame().transpose().to_csv(file_path, mode='w', header=True, index=True)
        
        print(f"📁 Dados do dia {date.date()} salvos em {file_path}")

@task(retries=3, retry_delay_seconds=5, log_prints=True)
def analyze_stock_movement(df):
    """Identifica as 3 ações que mais subiram e mais caíram e salva no Prefect Artifacts."""
    if df is None or df.empty:
        print("❌ Sem dados para análise.")
        return

    last_date = df.index[-1] if not df.empty else None

    if last_date is None:
        print("❌ Nenhum dado disponível para análise.")
        return

    last_day_data = df.loc[last_date].pct_change().dropna()

    if last_day_data.empty:
        print("❌ Nenhuma variação encontrada no último dia.")
        return

    top_gainers = last_day_data.nlargest(3)
    top_losers = last_day_data.nsmallest(3)

    print("\n📈 Top 3 maiores altas:")
    print(top_gainers)

    print("\n📉 Top 3 maiores quedas:")
    print(top_losers)

    table_data = {
        "Ticker": list(top_gainers.index) + list(top_losers.index),
        "Variação (%)": list(top_gainers.values) + list(top_losers.values),
        "Tipo": ["Alta"] * 3 + ["Queda"] * 3
    }
    
    create_table_artifact(
        key="top-stock-movements",
        table=table_data,
        description="Top 3 altas e baixas do último dia."
    )

@task(retries=3, retry_delay_seconds=5, log_prints=True)
def generate_report(df):
    """Gera um relatório de análise com gráfico."""
    if df is None or df.empty:
        print("❌ Sem dados para relatório.")
        return

    plt.figure(figsize=(10, 5))
    df.iloc[-30:].plot(title="Últimos 30 dias de Preços", figsize=(10, 5))
    plt.xlabel("Data")
    plt.ylabel("Preço")
    
    report_path = os.path.join(BASE_DIR, "relatorio.png")
    plt.savefig(report_path)
    
    markdown_report = f"""
    ## 📊 Relatório Diário das Ações
    
    - **Data do relatório:** {datetime.today().strftime('%Y-%m-%d')}
    - **Top 3 Altas e Quedas disponíveis no Prefect**
    
    ![Relatório](attachment://{report_path})
    """

    create_markdown_artifact(
        key="daily-stock-report",
        markdown=markdown_report,
        description="Relatório de análise das ações com gráfico."
    )

@flow
def stock_analysis_flow():
    """Fluxo principal do Prefect para coletar, processar e gerar relatórios das ações."""
    df = fetch_stock_data(TICKERS)
    indicators = calculate_indicators(df)
    save_partitioned_data(df)
    analyze_stock_movement(df)
    generate_report(df)

if __name__ == "__main__":
    stock_analysis_flow()
