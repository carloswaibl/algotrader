import backtrader as bt
import pandas as pd
from strategies.zero_dte_spread import ZeroDTESpread

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # --- Add Strategy ---
    cerebro.addstrategy(ZeroDTESpread)
    
    # --- Load Data ---
    # In a real scenario, you need a custom data feed for your options data.
    # For now, let's create some dummy data to make the script runnable.
    
    # Dummy SPX data
    spx_dummy_data = pd.read_csv(
        'https://raw.githubusercontent.com/backtrader/backtrader/master/datas/2006-day-001.txt',
        parse_dates=True, index_col=0
    )
    spx_data_feed = bt.feeds.PandasData(dataname=spx_dummy_data)
    cerebro.adddata(spx_data_feed, name='SPX')
    
    # Dummy Options Data - THIS IS A CRITICAL PART YOU WILL BUILD
    # You would load your Parquet file here and create a custom feed
    # that Backtrader can understand.
    options_dummy_data = spx_dummy_data.copy() # Just to have a second data feed
    options_data_feed = bt.feeds.PandasData(dataname=options_dummy_data)
    cerebro.adddata(options_data_feed, name='Options')

    # --- Configure Cerebro ---
    cerebro.broker.setcash(100000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10) # Trade 10 contracts
    cerebro.broker.setcommission(commission=0.65, mult=100) # Per contract commission

    # --- Run Backtest ---
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # --- Plot Results ---
    cerebro.plot(style='candlestick', barup='green', bardown='red')