import pandas as pd
import glob
import os

def load_latest_data(data_dir='../data'):
    """
    Finds the latest CSV file in the data directory and loads it into a DataFrame.
    """
    # Adjust path if running from utilites or root
    if not os.path.exists(data_dir):
        # Try relative to current file if data_dir is relative
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, data_dir)
    
    list_of_files = glob.glob(os.path.join(data_dir, '*.csv'))
    
    if not list_of_files:
        print(f"No CSV files found in {data_dir}")
        return None

    # Find the latest file based on creation time
    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"Loading data from: {latest_file}")
    
    try:
        df = pd.read_csv(latest_file)
        return df
    except Exception as e:
        print(f"Error reading {latest_file}: {e}")
        return None
