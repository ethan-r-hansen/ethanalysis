# importing necessary modules
import skrf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axes
from typing import Callable, Any, Iterable


# Function to get the specific S-data given a string input
def get_s_data(network: skrf.network.Network,
               s_to_get: str,
               scale: str = 'dB') -> np.ndarray:
    """
    Function to input a network and string of which S-paramter data to grab, '11' for example, and output the numpy
    array corresponding to that s-paramter. This is in terms of dB by default, but can also be given in linear terms via
    the scale argument.

    Parameters
    ----------
    network : skrf.network.Network
        Skrf network which has the s data that you want to access.
    s_to_get : str
        String containing the S-parameter to access, either '11', '12', '21', or '22'.
    scale : str, optional
        String denoting the scale you want the data to be in, either 'dB' or 'linear' for now, by default 'dB'

    Returns
    -------
    np.ndarray
        Numpy array corresponding to the user chosen S-parameter data

    Raises
    ------
    Exception
        Argument for scale is not in the list of valid strings. 
    Exception
        s_to_get argument is not in the list of valid strings.
    """    
    # Get s parameters in terms of the scale you want
    if scale == 'dB':
        s_params = network.s_db
    elif scale == 'linear':
        s_params = network.s
    else:
        raise Exception('Invalid scale string input! Try "dB" or "linear"')
    # go through all possible options
    if s_to_get in '11':
        return s_params[:, 0, 0]
    elif s_to_get in '21':
        return s_params[:, 1, 0]
    elif s_to_get in '12':
        return s_params[:, 0, 1]
    elif s_to_get in '22':
        return s_params[:, 1, 1]
    else:
        raise Exception('No valid string was passed through s_to_get. Try 11, 12, 21, 22')
    
    
# Function to calculate the impedance from the s parameters
def impedance_from_s(s_matrix: np.ndarray) -> np.ndarray:
    """
    This is a simple function that converts an S matrix or S vector into the corresponding impedance parameters that would be plotted
    on a smith chart. 

    Parameters
    ----------
    s_matrix : np.ndarray
        The numpy array containing either the full S matrix, or just one of the S vectors.

    Returns
    -------
    np.ndarray
        Array of the complex impedance values. 
    """    
    return (1 + s_matrix)/(1 - s_matrix)


# Plotting functions
def plot_s_parameters(network: str|skrf.network.Network,
                      name = None,
                      s_to_plot: str = '11',
                      ax = None,
                      colors: list[str] = ['#66c2a5','#fc8d62','#8da0cb','#e78ac3','#a6d854','#ffd92f','#e5c494','#b3b3b3'],
                      title:str='S-Parameters',
                      font_size = 12,
                      x_range = None,
                      y_range = None): 
    #TODO: Pick new colors based on the one chart that Nick showed in his slides
    #TODO: Change all of these plotting parameters to be kwargs! Then write, if 'title' in kwargs.keys(). Just document the possible ones well.
    #TODO: add the docstrings for this function
    #TODO: add the function to pass in different axes here. I imagine that I will make a wrapper for the grid plotting nick showed.
    #TODO: add the default to always have the upper xlim as 0
    # Define network from either filename input or skrf.Network input
    if isinstance(network, str):
        try:
            net = skrf.Network(file=network,
                               name=name)
        except: print('Issue importing network from filename.')
    else:
        net = network
        
    # Get the frequency array from the network
    try:
        freq = net.f / 1e9 # in GHz
    except: print('Issue with network. Cannot retrieve frequency array.')
    
    # Create the figure if an existing axis was not provided. I will likely just use this for testing. 
    if ax == None:
        # Define variable to show the plot at the end
        show_plot = True
        # Create the figure
        fig, ax = plt.subplots(figsize = (8,6))
        # Set the labels
        if title is not None:
            ax.set_title(title, fontsize=font_size)
        ax.set_xlabel('Frequency (GHz)', fontsize=font_size)
        ax.set_ylabel('dB', fontsize=font_size) 
        
    # Raise error if weird ax is passed through 
    elif not isinstance(matplotlib.axes._axes.Axes):
        raise Exception('user input "ax" argument that is not a true matplotlib axis...')
        
    # Now, loop through the parameters to plot.
    for i, s_to_get in enumerate(s_to_plot.split(' ')):
        # Plot the specific data, using my get_s_data function to convert '11' to the corresponding S11 data for example
        ax.plot(freq,
                get_s_data(net, s_to_get),
                label=f'S{s_to_get}', #TODO: Add the names to the labels! This will make it easier to compare different devices
                color=colors[i])
    
    # Plot the defined range
    if x_range is not None:
        try:
            plt.xlim(x_range)
        except:
            print('Issue with setting x_range, check that you input a proper list')
    if y_range is not None:
        try:
            plt.ylim(y_range)
        except:
            print('Issue with setting x_range, check that you input a proper list')
    # Plot the lengend now but to the right of the figure
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(alpha=0.5)
        
    if show_plot:
        plt.show()
        return fig, ax
    else:
        return ax

    
# TODO: Create function for plotting the smith data  
# # Function to plot the smith chart data from a given s-parameter
def plot_impedance(network: str|skrf.network.Network,
                   name = None,
                   s_to_plot: str = '11',
                   ax = None,
                   colors: list[str] = ['#66c2a5','#fc8d62','#8da0cb','#e78ac3','#a6d854','#ffd92f','#e5c494','#b3b3b3'],
                   title:str='Impedance (Normalized to 50 Ohm)',
                   font_size = 12,
                   x_range = None,
                   y_range = None):
    
    if isinstance(network, str):
        try:
            net = skrf.Network(file=network,
                               name=name)
        except: print('Issue importing network from filename.')
    else:
        net = network
        
    # Get the frequency array from the network
    try:
        freq = net.f / 1e9 # in GHz
    except: print('Issue with network. Cannot retrieve frequency array.')
    
    # Create the figure if an existing axis was not provided. I will likely just use this for testing. 
    if ax == None:
        # Define variable to show the plot at the end
        show_plot = True
        # Create the figure
        fig, ax = plt.subplots(figsize = (8,6))
        # Set the labels
        if title is not None:
            ax.set_title(title, fontsize=font_size)
        ax.set_xlabel('Frequency (GHz)', fontsize=font_size)
        ax.set_ylabel('Impedance (Norm. to 50 Ohm)', fontsize=font_size) 
        
    # Raise error if weird ax is passed through 
    elif not isinstance(matplotlib.axes._axes.Axes):
        raise Exception('user input "ax" argument that is not a true matplotlib axis...')

    # Now calculate the impedance values and loop over each parameter defined by 
    for i, s_to_get in enumerate(s_to_plot.split(" ")):
        # get the s_data and convert it to impedance data
        s_data = get_s_data(net, s_to_get, scale='linear')
        imp_data = impedance_from_s(s_data)
        # Plot the real
        ax.plot(freq,
                imp_data.real,
                label=f'Re(z) from S{s_to_get}', #TODO: Add the names to the labels! This will make it easier to compare different devices
                color=colors[i])
        # Plot the imaginary
        ax.plot(freq,
                imp_data.imag,
                label=f'Im(z) from S{s_to_get}', #TODO: Add the names to the labels! This will make it easier to compare different devices
                color=colors[i],
                ls='--')
    # Plot horizontal lines at zero and 1 to make viewing the plots much easier
    plt.axhline(y=0, color='k', alpha=0.5)
    plt.axhline(y=1, color='k', alpha=0.5)
    
    # Plot the defined range
    if x_range is not None:
        try:
            plt.xlim(x_range)
        except:
            print('Issue with setting x_range, check that you input a proper list')
    if y_range is not None:
        try:
            plt.ylim(y_range)
        except:
            print('Issue with setting x_range, check that you input a proper list')
    # Plot the lengend now but to the right of the figure
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(alpha=0.5)
        
    if show_plot:
        plt.show()
        return fig, ax
    else:
        return ax
# Create a class for dealing with multiple Networks, can either pass in a list of networks or a list of filenames
# class RFNetworks():
#     """
#     Class representing RF Network data from either a VNA or Simulation software. Currently only accepts touchstone files
    
#     Attributes:
#         file (str|list[str]): path to the file/files you want to load. Currently only accepts .sNp files. Can be array of one file.
#         name (str|list[str]): user defined name/names corresponding to the files imported. 
#             These can be used to call back the specific data set. 
#             If no name is provided, it will default to [0, 1, 2, etc..]
#     """    
#     def __init__(self, 
#                  files: str|list[str],
#                  names: str|list[str]):
#         #TODO: Add option to pass through the design parameters.
#         #TODO: This will accept an array of 'files' and a string of names so that you can label them easily
#         # And then you will be able to call the names if you want to. That is the hope? Make this easy to use.
#         # I am imagining that this will be used when comparing device parameters
#         # Then you will use the name to access the data? Make this less complex
#         # Initialize files, turn them into an array if single str input
#         if isinstance(files, str):
#             self.filenames = [files]
#             self.names = [names]
        
#         # Initialize the RF network
#         self.networks = skrf.Network(file=files,
#                                      name=names)
        
#TODO: Create a class called RFNetworks for working with and plotting multiple files