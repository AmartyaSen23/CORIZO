import pandas as pd
import re
import os

package_directory = os.path.dirname(os.path.abspath(__file__))

csv_folder = f'{package_directory}/../FullDataCSV'
hdf_file = f'{package_directory}/../FullData.h5'

master = None
hdf_master = None

def read_master(use_hdf=True):
    """Helper Function to Load Data Master File

    Parameter:

    use_hdf: use hdf file to load data (default True)
    """
    global master, hdf_master
    key = 'master'
    master = read_from_key(key=key, use_hdf=use_hdf)
    hdf_master = use_hdf
    return master

def filter_symbol(query=None, search=None, return_all=False, return_empty=False, use_hdf=True):
    """Helper function to filter individual stock data.

    Parameter:

    query: Similar to pandas query input except here if it doesn't contain =, < or > then query will be replaced by f'tradingsymbol == "{query}" or name == "{query}"
    
    search: It will filter all the symbols with contain '@search' in tradingsymbol or name.

    return_all: If true return all matches else it will ask user to enter row number (default False)

    return_empty: If true return empty matches else raise error (default False)

    use_hdf: use hdf file to load data (default True)
    """

    if query is None and search is None:
        raise ValueError('both query and search can not be None')

    if query is not None:
        if re.search('=|<|>', query) is None:
            query = f'tradingsymbol == "{query}" or name == "{query}"'
        query = f'({query})'
    if search is not None:
        search = f'(tradingsymbol.str.contains("{search}") or name.str.contains("{search}"))'
    final_query = [x for x in [query, search] if x is not None]
    final_query = ' and '.join(final_query)

    if hdf_master is None or hdf_master != use_hdf:
        read_master(use_hdf=use_hdf)
    
    match = master.query(final_query, engine='python').reset_index(drop=True)
    if match.shape[0] == 0:
        if return_empty:
            return match
        raise ValueError('Empty result are Fetched')
    elif match.shape[0] > 1:
        if return_all:
            return match
        display(match)
        i = 0
        while True:
            print('\n')
            row = input('Enter row index: ')
            try:
                row = row.strip()
                if row.lower() == 'exit':
                    raise ValueError('Exited by user')
                row = int(row)
                match = match.loc[row]
                print(f'\nSelected tradingsymbol: {match["tradingsymbol"]}')
                break
            except:
                print('Please Enter a Valid Input')
                i += 1    
                if i == 3:
                    raise ValueError('Max try reached')
    else:
       match = match.iloc[0]
    return match


def read_from_key(key, use_hdf=True):
    """
    It will return stock market data attached to a input key, with additional parameter to use_hdf data.
    """
    if use_hdf:
        return pd.read_hdf(hdf_file, key)
    return pd.read_csv(os.path.join(csv_folder, f'{key}.csv'))

def read_data(query=None, search=None, use_hdf=True):
    """
    Helper function to read individual stock data.

    Parameter:

    query: Similar to pandas query input except here if it doesn't contain =, < or > then query will be replaced by f'tradingsymbol == "{query}" or name == "{query}"
    
    search: It will filter all the symbols with contain '@search' in tradingsymbol or name.

    use_hdf: use hdf file to load data (default True)


    This Function will call filter_symbol with return_all=False, return_empty=False, which mean
      - it will ask user to enter row number if mutiple symbol satisfies the criteria
      - and it will raise error if no symbol satisfies the criteria.
    
    """
    match = filter_symbol(query=query, search=search, return_all=False, return_empty=False, use_hdf=use_hdf)

    key = match['key']
    return read_from_key(key, use_hdf=use_hdf)