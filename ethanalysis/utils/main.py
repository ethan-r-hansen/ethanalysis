import numpy as np

# TODO: Move this to a utils files or something like that
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
                        extremum: str='min',
                        range: str|list = 'all') -> (float, float, float):
    """
    Finds the x value where the desired extremum occurs (min or max for now) for a given range.
    The output is a tuple of the extremum x value, the extremum y value, and the index of the extremum value.
    
    Parameters
    ----------
    x_data : np.ndarray
        x data for the set
    y_data : np.ndarray
        y data to be searched for a minimum value
    extremum : str
        string to determine what extremum to search for. 'min' or 'max' for now. 
    range : str|list
        range of data to search for the extremum. 'all' or a list of the form [min, max].
        
    Returns
    -------
    float
        extremum y value
    float
        x value where y value is the extremum
    float
        index of the extremum value
    """
    # format the data for if there is a range
    if isinstance(range, list):
        # truncate the data to the range
        try:
            x_data_trunc, y_data_trunc = truncate_data(x_data, y_data, range)
        except ValueError:
            raise ValueError('The range is not valid. Improperly formatted list.')
    elif isinstance(range, str):
        if range == 'all':
            x_data_trunc, y_data_trunc = x_data, y_data
        else:
            raise ValueError('The range is not valid. The only string allowed is \'all\'.')
    else:
        raise ValueError('The range is not valid.')
    
    # for the mimimum case
    if extremum == 'min':
        # find the index of the minimum value
        min_index = np.argmin(y_data_trunc)
        # get the x value at the minimum index
        min_x = x_data_trunc[min_index]
        # get the y value at the minimum index
        min_y = y_data_trunc[min_index]
        # get the x index for the orignal data where the minimum value occurs in the truncated data
        min_index = np.where(x_data == min_x)[0][0]
        return min_x, min_y, min_index
    elif extremum == 'max':
        # find the index of the minimum value
        max_index = np.argmax(y_data_trunc)
        # get the x value at the minimum index
        max_x = x_data_trunc[max_index]
        # get the y value at the minimum index
        max_y = y_data_trunc[max_index]
        # get the x index for the orignal data where the maximum value occurs in the truncated data
        max_index = np.where(x_data == max_x)[0][0]
        return max_x, max_y, max_index