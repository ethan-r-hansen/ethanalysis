# importing necessary modules
import skrf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axes
import pandas as pd
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

# define function for getting list  of networks out from an input of either, single network or string to filepath
# or list of networks or strings to filepaths
def get_networks(network: str|skrf.network.Network|list[str|skrf.network.Network])->list[skrf.network.Network]:
    """
    Function to input a network or list of networks and return a list of skrf.Network objects. This is useful for
    when you want to input a single network, or a list of networks, and return a list of skrf.Network objects that
    can be used for plotting or other analysis.

    Parameters
    ----------
    network : str|skrf.network.Network|list[str|skrf.network.Network]
        Either a single network, a list of networks, a single string to a filepath, or a list of strings to filepaths.

    Returns
    -------
    list[skrf.network.Network]
        List of skrf.Network objects that can be used for plotting or other analysis.
    """    
    # Check if the input is a list of networks or a single network that isn't a list (single list of one network is fine)
    if isinstance(network, str):
        #TODO: Add the ability to get the frequency array to and return it as well as freqs
        try:
            nets = [skrf.Network(file=network)]
        except: print('Issue importing network from filename.')
    elif isinstance(network, skrf.network.Network):
        nets = [network]
    elif isinstance(network, list):
        nets = []
        for net in network:
            if isinstance(net, str):
                try:
                    nets.append(skrf.Network(file=net))
                except: print('Issue importing network from filename.')
            elif isinstance(net, skrf.network.Network):
                nets.append(net)
            else:
                print('Issue with input list. Check that all entries are either strings to filepaths or skrf.Network objects.')
    else:
        print('Issue with input. Check that input is either a string to a filepath, a skrf.Network object, or a list of either.')
    return nets

# Creating a function to get the frequency array in provided units (Hz, kHz, MHz, GHz) from a network
def get_freq(network: skrf.network.Network,
             units: str='GHz')->np.ndarray: 
    """
    Function to input a network and return the frequency array in the desired units.
    
    Parameters
    ----------
    network : skrf.network.Network
        A single network
    units : str, optional
        String denoting the units you want the frequency array to be in, either 'Hz', 'kHz', 'MHz', or 'GHz' for now, by default 'GHz'
        
    Returns
    -------
    np.ndarray
        Numpy array containing the frequency array in the desired units.
    """
    # Get the frequency array from the network
    try:
        freq = network.f
    except: print('Issue with network. Cannot retrieve frequency array.')
    # Convert the frequency array to the desired units
    if units == 'Hz':
        return freq
    elif units == 'kHz':
        return freq / 1e3
    elif units == 'MHz':
        return freq / 1e6
    elif units == 'GHz':
        return freq / 1e9
    else:
        raise Exception('Invalid units string input! Try "Hz", "kHz", "MHz", or "GHz"')


# Plotting functions
def plot_s_parameters(network: str|skrf.network.Network|list[str|skrf.network.Network],
                      names = None,
                      datasets_to_plot = None,
                      s_to_plot: str = '11',
                      ax = None,
                      colors: list[str] = ['#66c2a5','#fc8d62','#8da0cb','#e78ac3','#a6d854','#ffd92f','#e5c494','#b3b3b3'],
                      linestyles: list[str] = ['-','--',':','-.'],
                      title:str='S-Parameters',
                      font_size = 12,
                      x_range = None,
                      y_range = None): 
    #TODO: Figure out a better way to deal with displaying the different datasets and how we color and display them. 
    #TODO: Pick new colors based on the one chart that Nick showed in his slides
    #TODO: Change all of these plotting parameters to be kwargs! Then write, if 'title' in kwargs.keys(). Just document the possible ones well.
    #TODO: add the docstrings for this function
    #TODO: add the default to always have the upper xlim as 0
    #TODO: Pass through the desired plotting units for the frequency axis (Hz, kHz, MHz, GHz) to pass to the get_freq function
    # Get the network(s) from the input
    nets = get_networks(network)
    # Create the names array if one doesn't exist
    if names is None:
        names = [i for i in range(len(nets))]
    # # Create a dictionary from the network(s) to easily access the data if different sets denoted by dataset_to_plot, with names as keys
    # if datasets_to_plot is not None and names is not None:
    #     # Create a temp array to store all of the networks in it
    #     temp_nets = []
    #     # Loop through the networks and names to create the dictionary
    
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
    elif not isinstance(ax, matplotlib.axes._axes.Axes):
        raise Exception('user input "ax" argument that is not a true matplotlib axis...')
    # Set show plot to false if an axis was passed through
    else:
        show_plot = False
        
    # Now, loop through the parameters to plot, and then plot for each dataset
    for i, net in enumerate(nets):
        for j, s_to_get in enumerate(s_to_plot.split(' ')):
            # Plot the specific data, using my get_s_data function to convert '11' to the corresponding S11 data for example
            ax.plot(get_freq(net, units='GHz'),
                    get_s_data(net, s_to_get),
                    label=f'{names[i]}: S{s_to_get}',
                    color=colors[i],
                    ls=linestyles[j])
    
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
#TODO: Add the ability to pass a networks class object that already has the preset names, networks, and even range to plot, can be overriden though
#TODO: Add the option to choose the units for the frequency axis (Hz, kHz, MHz, GHz)
# # Function to plot the smith chart data from a given s-parameter
def plot_impedance(network: str|skrf.network.Network,
                   names = None,
                   s_to_plot: str = '11',
                   ax = None,
                   colors: list[str] = ['#66c2a5','#fc8d62','#8da0cb','#e78ac3','#a6d854','#ffd92f','#e5c494','#b3b3b3'],
                   linestyles: list[str] = ['-','--',':','-.'],
                   title:str='Impedance (Normalized to 50 Ohm)',
                   font_size = 12,
                   x_range = None,
                   y_range = None):
    
    # Get the network(s) from the input
    nets = get_networks(network)
    # Create the names array if one doesn't exist
    if names is None:
        names = [i for i in range(len(nets))]
    
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
    elif not isinstance(ax, matplotlib.axes._axes.Axes):
        raise Exception('user input "ax" argument that is not a true matplotlib axis...')
    # Set show plot to false if an axis was passed through
    else:
        show_plot = False

    # Now, loop through the parameters to plot, and then plot for each dataset
    for i, net in enumerate(nets):
    # Now calculate the impedance values and loop over each parameter defined by 
        for j, s_to_get in enumerate(s_to_plot.split(" ")):
            # get the s_data and convert it to impedance data
            s_data = get_s_data(net, s_to_get, scale='linear')
            imp_data = impedance_from_s(s_data)
            # Plot the real
            ax.plot(get_freq(net, units='GHz'),
                    imp_data.real,
                    label=f'{names[i]}: Re(z) from S{s_to_get}', 
                    color=colors[2*i],
                    ls=linestyles[j])
            # Plot the imaginary
            ax.plot(get_freq(net, units='GHz'),
                    imp_data.imag,
                    label=f'{names[i]}: Im(z) from S{s_to_get}',
                    color=colors[2*i+1],
                    ls=linestyles[j]) #TODO: Fix this so that the real is distringuisable from the imaginary (work with line styles, or just do two plots!)
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
#TODO: Have one of the inputs be a data, and one of the inputs be a simulation network
# since that is mostly what I will be working with. 