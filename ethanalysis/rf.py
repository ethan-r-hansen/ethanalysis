# importing necessary modules
import skrf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axes
from typing import Callable, Any, Iterable


# Function to get the specific S-data given a string input
#TODO: Update this to choose whether you want dB data or smith data
def get_s_data(network: skrf.network.Network,
               s_to_get: str) -> np.ndarray:
    #TODO: Add the docstrings for this!!
    # Get s parameters in dB
    s_params = network.s_db
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

# Plotting functions
def plot_s_parameters(network: str|skrf.network.Network,
                      name = None,
                      s_to_plot: str = '11',
                      ax = None,
                      colors: list[str] = ['#66c2a5','#fc8d62','#8da0cb','#e78ac3','#a6d854','#ffd92f','#e5c494','#b3b3b3'],
                      title:str='S-Parameters',
                      font_size = 12): 
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
        freq = network.f / 1e9 # in GHz
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
                get_s_data(network, s_to_get),
                label=f'S{s_to_get}', #TODO: Add the names to the labels! This will make it easier to compare different devices
                color=colors[i])
    # Plot the lengend now but to the right of the figure
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(alpha=0.5)
    
    if show_plot:
        plt.show()
        return fig, ax
    else:
        return ax

    
# TODO: Create function for plotting the smith data  
    

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