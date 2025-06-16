# --- IMPORTANT: SET MATPLOTLIB BACKEND ---
# This must be done BEFORE importing backtrader or pyplot
import matplotlib
matplotlib.use('Agg')

import backtrader as bt
import pandas as pd
from pathlib import Path
from datetime import date

# Import the strategy that has been enhanced to accept the options dataframe
from strategies.zero_dte_spread import ZeroDTESpread

class PandasDataWithVWAP(bt.feeds.PandasData):
    # Add the vwap line to the data feed
    # lines = ('vwap',)

    # Tell backtrader which column name in the dataframe corresponds to each line
    # -1 indicates that the column name should be automatically matched to the line name
    params = (
        ('datetime', None), # Use the index for datetime
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', None),
        ('openinterest', None),
    )

if __name__ == '__main__':
    try:
        cerebro = bt.Cerebro()

        # --- CONFIGURATION ---
        # This should match the date you downloaded with the data pipeline
        TARGET_DATE_STR = "20240510"
        DATA_DIR = Path("./data/parquet")
        PLOT_DIR = Path("./plots")
        PLOT_DIR.mkdir(exist_ok=True) # Ensure the plots directory exists

        # --- Load Data ---
        # 1. Load the primary SPX data feed. This will drive the backtest.
        spx_file = DATA_DIR / f"NDX_{TARGET_DATE_STR}.parquet"
        if not spx_file.exists():
            raise FileNotFoundError(f"SPX data file not found: {spx_file}")
        
        spx_df = pd.read_parquet(spx_file)
        # Ensure data is in chronological order
        spx_df = spx_df.sort_index()
        spx_data_feed = PandasDataWithVWAP(dataname=spx_df)
        cerebro.adddata(spx_data_feed, name='SPX')
        
        # 2. Load the entire options chain data into a pandas DataFrame.
        # This will NOT be a backtrader feed, but a parameter for the strategy.
        # options_file = DATA_DIR / f"SPX_OPTIONS_{TARGET_DATE_STR}.parquet"
        # if not options_file.exists():
        #     raise FileNotFoundError(f"Options data file not found: {options_file}")

        # options_df = pd.read_parquet(options_file)
        # Convert timestamp to a datetime object for easier filtering
        # options_df['timestamp'] = pd.to_datetime(options_df['timestamp'])
        
        # --- Add Strategy ---
        # Pass the options dataframe directly to the strategy's constructor
        cerebro.addstrategy(ZeroDTESpread)

        # --- Configure Cerebro ---
        starting_cash = 100000.0
        cerebro.broker.setcash(starting_cash)
        cerebro.addsizer(bt.sizers.FixedSize, stake=10)
        cerebro.broker.setcommission(commission=0.65) 

        # --- Run Backtest ---
        print(f'Starting Portfolio Value: {starting_cash:.2f}')
        results = cerebro.run()
        final_value = cerebro.broker.getvalue()
        print(f'Final Portfolio Value: {final_value:.2f}')

        # --- Save the Plot Conditionally ---
        if final_value != starting_cash:
            print(f"Saving plot to {PLOT_DIR / 'backtest_result.png'}")
            # The plot() method returns a list of figures. We take the first one.
            # We also disable the volume plot as it can sometimes cause issues.
            figure = cerebro.plot(style='candlestick', barup='green', bardown='red', iplot=False, volume=False)[0][0]
            figure.savefig(PLOT_DIR / 'backtest_result.png', dpi=300)
        else:
            print("\nNo trades were executed or portfolio value did not change.")
            print("This is likely because the strategy's entry conditions were not met.")
            print("Skipping plot generation.")
    except Exception as e:
        print(f"Error: {e}")