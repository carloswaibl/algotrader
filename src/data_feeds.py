import backtrader as bt
import pandas as pd

class OptionsDataPandas(bt.feeds.PandasData):
    """
    Custom data feed for options data.
    This feed allows access to the entire options chain for a given timestamp.
    """
    lines = ('options_chain',) # Add a new 'line' to hold the options chain object

    params = (
        ('dataname', None),
        # The 'options_chain' line will be a placeholder (NaN) but we'll use
        # a custom method to retrieve the actual data.
        ('options_chain', -1), 
    )

    def __init__(self):
        super(OptionsDataPandas, self).__init__()
        # Keep the entire dataframe accessible
        self.options_df = self.p.dataname
        # Set the index to timestamp if it's not already
        if self.options_df.index.name != 'timestamp':
            self.options_df = self.options_df.set_index('timestamp')

    def get_options_chain_for_datetime(self, dt):
        """
        Returns the options chain (as a DataFrame) for the given datetime.
        """
        current_dt_utc = pd.to_datetime(dt, utc=True)
        # We find the chain for the specific timestamp.
        # In a real-world scenario with less frequent data, you might need
        # to find the most recent chain available before or at 'dt'.
        chain_at_time = self.options_df.loc[self.options_df.index == current_dt_utc]
        return chain_at_time