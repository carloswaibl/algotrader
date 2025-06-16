# In file: src/data-pipeline/download_data.py

import os
import pandas as pd
from datetime import date, timedelta
from pathlib import Path
from polygon import RESTClient

# --- CONFIGURATION ---
# IMPORTANT: Store your API key in an environment variable, not in your code.
# You can set this in your terminal: export POLYGON_API_KEY="YOUR_KEY"
API_KEY = os.environ.get("POLYGON_API_KEY")
OUTPUT_DIR = Path("./data/parquet")
UNDERLYING_SYMBOL = "I:NDX"
TARGET_DATE = date(2024, 5, 10) # A sample date


def download_and_save_spx_data(client, target_date):
    """Downloads 1-minute bar data for the underlying (SPX) for a given date."""
    print(f"Downloading 1-minute SPX data for {target_date}...")
    try:
        # Fetching 1-minute aggregates for the entire day
        aggs = client.get_aggs(
            ticker=UNDERLYING_SYMBOL,
            multiplier=1,
            timespan="minute",
            from_=target_date,
            to=target_date,
            limit=50000, # Set a high limit to get all bars for the day
        )
        spx_df = pd.DataFrame(aggs)
        spx_df['timestamp'] = pd.to_datetime(spx_df['timestamp'], unit='ms')
        spx_df = spx_df.set_index('timestamp')
        
        file_path = OUTPUT_DIR / f"{UNDERLYING_SYMBOL.replace('I:', '')}_{target_date.strftime('%Y%m%d')}.parquet"
        spx_df.to_parquet(file_path)
        print(f"Successfully saved SPX data to {file_path}")
        return True
    except Exception as e:
        print(f"Error downloading SPX data: {e}")
        return False

def download_and_save_options_data(client, target_date):
    """
    Downloads the entire options chain and their 1-minute bars for a given date.
    NOTE: This can be a very large download. For testing, you might limit the strike range.
    """
    print(f"Downloading options chain for {UNDERLYING_SYMBOL} on {target_date}...")
    all_options_data = []
    
    try:
        # Get all contracts for the 0DTE expiration
        contracts = client.list_options_contracts(
            underlying_ticker=UNDERLYING_SYMBOL,
            expiration_date=target_date,
            limit=1000
        )
        
        for contract in contracts:
            # You can add filtering here, e.g., by strike price, to reduce data size
            # if abs(contract.strike_price - current_spx_price) > 200:
            #     continue

            aggs = client.get_aggs(
                ticker=contract.ticker,
                multiplier=1,
                timespan="minute",
                from_=target_date,
                to=target_date,
                limit=50000,
            )
            
            if aggs:
                df = pd.DataFrame(aggs)
                df['contract_ticker'] = contract.ticker
                df['strike'] = contract.strike_price
                df['type'] = contract.contract_type
                all_options_data.append(df)

        if not all_options_data:
            print("No options data found for the given date.")
            return False

        # Combine all data and save
        full_options_df = pd.concat(all_options_data, ignore_index=True)
        full_options_df['timestamp'] = pd.to_datetime(full_options_df['timestamp'], unit='ms')

        file_path = OUTPUT_DIR / f"SPX_OPTIONS_{target_date.strftime('%Y%m%d')}.parquet"
        full_options_df.to_parquet(file_path)
        print(f"Successfully saved options data to {file_path}")
        return True

    except Exception as e:
        print(f"Error downloading options data: {e}")
        return False


if __name__ == '__main__':
    if not API_KEY:
        print("Error: POLYGON_API_KEY environment variable not set.")
    else:
        client = RESTClient(api_key=API_KEY)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Download both datasets
        download_and_save_spx_data(client, TARGET_DATE)
        # download_and_save_options_data(client, TARGET_DATE)