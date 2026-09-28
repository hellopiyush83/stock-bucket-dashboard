from datetime import date
import sqlite3
import yfinance as yf

TICKERS = ["AAPL", "MSFT", "NVDA", "JNJ", "PG", "JPM", "BAC", "TSLA"]


def run_pipeline():
    conn = sqlite3.connect("stock_buckets.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS buckets (
        ticker TEXT,
        bucket TEXT,
        score REAL,
        updated_at TEXT,
        PRIMARY KEY (ticker, bucket, updated_at)
    )
    """)

    today = str(date.today())

    for symbol in TICKERS:
        try:
            info = yf.Ticker(symbol).info
            pe = info.get("forwardPE", 999)
            div = info.get("dividendYield", 0) or 0

            # Simple logic rules
            if pe < 25:
                cursor.execute(
                    "INSERT OR REPLACE INTO buckets VALUES (?, ?, ?, ?)",
                    (symbol, "Value / Core", round(pe, 2), today),
                )
            if div > 0.015:
                cursor.execute(
                    "INSERT OR REPLACE INTO buckets VALUES (?, ?, ?, ?)",
                    (symbol, "Dividend Income", round(div * 100, 2), today),
                )
        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    run_pipeline()
