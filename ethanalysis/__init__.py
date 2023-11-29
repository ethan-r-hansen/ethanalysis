__version__ = '0.1.dev'

import numpy as np

# For relative imports to work in Python 3.6
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))


def hello_world(): # temporary just for testing as of now
    print("Hello world")
    
# Create function to truncate the data to a specific x_range
def truncate_data(x_data: np.ndarray,
                  y_data: np.ndarray,
                  x_range: list)->(np.ndarray, np.ndarray):
    """
    Truncate the data to a specific x_range
    
    Parameters
    ----------
    x_data : array
        x-axis data
    y_data : array
        y-axis data
    x_range : array
        x-axis range to truncate data to
        
    Returns
    -------
    x_data_trunc : array
        truncated x-axis data
    y_data_trunc : array
        truncated y-axis data
    """
    # Find the indices of the x_range
    x_min_idx = np.argmin(np.abs(x_data - x_range[0]))
    x_max_idx = np.argmin(np.abs(x_data - x_range[1]))
    
    # Truncate the data
    x_data_trunc = x_data[x_min_idx:x_max_idx]
    y_data_trunc = y_data[x_min_idx:x_max_idx]
    
    return x_data_trunc, y_data_trunc

# create a function to find the x value where an extremum occurs in the y data
def find_where_extremum(x_data: np.ndarray, 
                        y_data: np.ndarray,
                        extremum: str='min') -> (float, float, float):
    """
    Finds the x value where the desired extremum occurs (min or max for now).
    The output is a tuple of the extremum x value, the extremum y value, and the index of the extremum value.
    
    Parameters
    ----------
    x_data : np.ndarray
        x data for the set
    y_data : np.ndarray
        y data to be searched for a minimum value
    extremum : str
        string to determine what extremum to search for. 'min' or 'max' for now. 
        
    Returns
    -------
    float
        extremum y value
    float
        x value where y value is the extremum
    float
        index of the extremum value
    """
    # for the minimum case
    if extremum == 'min':
        # find the index of the minimum value
        min_index = np.argmin(y_data)
        # get the x value at the minimum index
        min_x = x_data[min_index]
        # get the y value at the minimum index
        min_y = y_data[min_index]
        return min_x, min_y, min_index
    elif extremum == 'max':
        # find the index of the minimum value
        max_index = np.argmax(y_data)
        # get the x value at the minimum index
        max_x = x_data[max_index]
        # get the y value at the minimum index
        max_y = y_data[max_index]
        return max_x, max_y, max_index
    else:
        raise ValueError('extremum must be either "min" or "max"')