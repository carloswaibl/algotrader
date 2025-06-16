import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

def generate_mock_spx_and_options_data():
    """Generates a realistic-looking mock dataset for SPX and its options."""
    print("Generating mock data...")
    DATA_DIR = Path("./data/parquet")
    PLOTS_DIR = Path("./plots")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # --- Generate Mock SPX Data ---
    start_date = datetime(2025, 6, 13, 9, 30)
    minutes = 6.5 * 60 # 9:30 AM to 4:00 PM
    timestamps = [start_date + timedelta(minutes=i) for i in range(int(minutes))]
    price = 5200 + np.random.randn(len(timestamps)).cumsum() * 0.5
    spx_df = pd.DataFrame({'open': price, 'high': price, 'low': price, 'close': price, 'volume': np.random.randint(1000, 5000, size=len(timestamps))}, index=pd.to_datetime(timestamps))
    spx_df.index.name = 'timestamp'
    
    # --- Generate Mock Options Data ---
    # A simplified structure. A real file would be much larger.
    options_data = []
    for ts in timestamps[::5]: # Sample every 5 minutes
        underlying_price = spx_df.loc[ts, 'close']
        for strike_offset in [-20, -10, 0, 10, 20]:
            strike = int(round(underlying_price / 10) * 10) + strike_offset
            # Mock some greeks and prices
            options_data.append({
                'timestamp': ts,
                'underlying_price': underlying_price,
                'contract_type': 'put',
                'expiration': datetime(2025, 6, 13).date(),
                'strike': strike,
                'bid': 1.5 + strike_offset * 0.1 + np.random.rand() * 0.1,
                'ask': 1.6 + strike_offset * 0.1 + np.random.rand() * 0.1,
                'delta': 0.1 + strike_offset * 0.01
            })
    options_df = pd.DataFrame(options_data).set_index('timestamp')
    
    # Save to Parquet
    spx_file = DATA_DIR / "SPX_20250613.parquet"
    options_file = DATA_DIR / "SPX_OPTIONS_20250613.parquet"
    spx_df.to_parquet(spx_file)
    options_df.to_parquet(options_file)
    print(f"Saved mock SPX data to {spx_file}")
    print(f"Saved mock options data to {options_file}")


def generate_mock_backtest_results():
    """Generates a mock backtest output CSV file."""
    print("\nGenerating mock backtest results...")
    DATA_DIR = Path("./data")
    DATA_DIR.mkdir(exist_ok=True)
    
    dates = pd.date_range(start="2025-05-01", end="2025-06-13")
    equity = 100000 * (1 + np.random.randn(len(dates)).cumsum() * 0.001)
    results_df = pd.DataFrame({'equity': equity}, index=dates)
    results_df.index.name = 'date'
    
    results_file = DATA_DIR / "backtest_results_log.csv"
    results_df.to_csv(results_file)
    print(f"Saved mock backtest results to {results_file}")

if __name__ == "__main__":
    generate_mock_spx_and_options_data()
    generate_mock_backtest_results()