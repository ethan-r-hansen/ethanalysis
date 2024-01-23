# importing necessary modules
import skrf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axes
import pandas as pd
from typing import Callable, Any, Iterable
from ethanalysis.fitting.main import fit_s11_resonance_dip
from ethanalysis.utils.colors import get_color_list, get_color
from matplotlib.lines import Line2D

#TODO: Move this to the colors library
colors = ['cyan', 'orange', 'lime', 'violet', 'pink', 'yellow', 'blue', 'grape', 'green', 'gray']
# Create colors for fitting. Eventually I will make a colors library that I can import from
fitting_colors = get_color_list(colors, 2)
plot_colors = get_color_list(colors, 4)

# Function to get parameters dictionary from a touchstone file
def get_params_dict_from_touchstone(filepath: str) -> dict:
    """
    Get simulation parameters from a touchstone file saved from a CST simulation. CST saves the design parameters in a comment
    at the top of the file, which is useful to grab if you are performing a parameter sweep!
    
    Parameters
    ----------
    filepath : str
        String containing the filepath of the touchstone file.
        
    Returns
    -------
    dict
        Dictionary containing the parameters and their values.
    """
    test_file = skrf.Touchstone(filepath)
    parameters = test_file.comments.split('\n')[3].split(' = ')[1][1:-1]
    par_dict = dict((x.strip(), y.strip())
                    for x, y in (element.split('=')
                    for element in parameters.split('; '))
                    )
    return par_dict

# Function to get an array of a chosen parameter from an array of touchstone filepaths.
def get_param_array_from_touchstones(filepaths: str|list[str]|np.ndarray,
                                     parameter: str) -> list:
    """
    Given a list of touchstone filepaths, return an array of the chosen parameter from each touchstone file. 
    This is useful for when you are performing a sweep against a parameter from a simulation.
    This has only been tested with touchstone files from CST simulations.
    
    Parameters
    ----------
    filepaths : str|list[str]|np.ndarray
        String, list of strings, or numpy array of strings containing the filepaths of the touchstone files.
    parameter : str
        String containing the parameter to grab from each touchstone file.
        
    Returns
    -------
    list
        List of the chosen parameter from each touchstone file.
    """
    if isinstance(filepaths, str):
        filepaths = [filepaths]
    print(type(filepaths))
    if not isinstance(filepaths, np.ndarray) and not isinstance(filepaths, list):
        raise TypeError('filepath must be a string, list, or numpy array')

    return [float(param[parameter]) for param in [get_params_dict_from_touchstone(file) for file in filepaths]]

# Function to get the specific S-data given a string input
def get_s_data(network: skrf.network.Network,
               s_to_get: str = '11',
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
def plot_s_parameters(networks: str|skrf.network.Network|list[str|skrf.network.Network],
                      names = None,
                      nets_to_plot = 'all',
                      s_to_plot: str = '11',
                      nets_to_fit_S11 = None,
                      fit_range: list|str = 'all',
                      ax = None,
                      colors = None,
                      fit_colors = None,
                      linestyles: list[str] = ['-','--',':','-.'],
                      title = 'S-Parameters',
                      font_size = 12,
                      x_range = None,
                      y_range = None,
                      show_plot: bool = False,
                      show_legend: bool = True,
                      x_label: str = 'Frequency (GHz)',
                      y_label: str = 'dB',
                      label_S_in_legend: bool = False): 
    #TODO: Figure out a better way to deal with displaying the different datasets and how we color and display them. 
    #TODO: Pick new colors based on the one chart that Nick showed in his slides
    #TODO: Change all of these plotting parameters to be kwargs! Then write, if 'title' in kwargs.keys(). Just document the possible ones well.
    #TODO: add the docstrings for this function
    #TODO: add the default to always have the upper xlim as 0
    #TODO: Pass through the desired plotting units for the frequency axis (Hz, kHz, MHz, GHz) to pass to the get_freq function
    # Get the network(s) from the input
    nets = get_networks(networks)
    # Create the names array if one doesn't exist
    if names is None:
        names = [i for i in range(len(nets))]
    elif len(names) != len(nets):
        raise Exception('The length of the names array does not match the length of the networks array!')
    # Create the nets dictionary so that I can easily access and choose from the data
    # If no names array is passed through, then it will simply be the index, as shown above
    nets_dict = dict(zip(names, nets))
    # If plotting all, set the nets_to_plot to the names of all of the networks
    if nets_to_plot == 'all':
        nets_to_plot = names
    
    # Create the figure if an existing axis was not provided. I will likely just use this for testing. 
    if ax == None:
        # Define variable to show the plot at the end
        show_plot = True
        # Create the figure
        fig, ax = plt.subplots(figsize = (8,6), dpi=150)
    # Raise error if weird ax is passed through 
    elif not isinstance(ax, matplotlib.axes._axes.Axes):
        raise Exception('user input "ax" argument that is not a true matplotlib axis...')
    # Set show plot to false if an axis was passed through
    else:
        show_plot = False
    # Now format the plot with the title and labels
    if title is not None:
        ax.set_title(title, fontsize=font_size)
        
    # Set the axis labels
    if x_label is not None:
        ax.set_xlabel(x_label, fontsize=font_size)
    if y_label is not None:
        ax.set_ylabel(y_label, fontsize=font_size)
    
    # Set the colors for plotting
    if fit_colors is None:
        fit_colors = fitting_colors
    elif not isinstance(fit_colors, list):
        raise Exception('The fit_colors argument must be a list of strings!')
    if colors is None:
        colors = plot_colors
    elif not isinstance(colors, list):
        raise Exception('The colors argument must be a list of strings!')
        
    # Create array for the custom legend elements
    legend_elements = []    
    
    #TODO: Fix so that I can easilly call the frequency and s11 data from the dictionary
    # Now, loop through the parameters to plot, and then plot for each dataset
    for i, name in enumerate(nets_to_plot):
        for j, s_to_get in enumerate(s_to_plot.split(' ')):
            # Plot the specific data, using my get_s_data function to convert '11' to the corresponding S11 data for example
            ax.plot(get_freq(nets_dict[name], units='GHz'),
                    get_s_data(nets_dict[name], s_to_get),
                    label=f'{name} S{s_to_get}',
                    color=colors[i],
                    ls=linestyles[j],
                    lw=1.5)
            # Add to the legend elements
            if label_S_in_legend:
                legend_elements.append(Line2D([0], [0], color=colors[i], lw=2, label=f'{name} S{s_to_get}'))
            else:
                legend_elements.append(Line2D([0], [0], color=colors[i], lw=2, label=name))
                
    # Now to fit the S11 data if desired
    if nets_to_fit_S11 is not None:
        # Create dicts for the centers and Q factors to pass through
        centers_dict = {}
        q_factors_dict = {}
        for i, name in enumerate(nets_to_fit_S11):
            # Make sure that each entry is in the names array
            if name not in names:
                raise Exception(f'Network {name} is not in the names array!')
            # run the fit
            fit_result, q_fact, fit_plotting_data = fit_s11_resonance_dip(freq_data=get_freq(nets_dict[name], units='GHz'),
                                                                          s11_data=get_s_data(nets_dict[name], s_to_get='11'),
                                                                          fit_range=fit_range)
            # add the center and Q factor to the dictionaries
            centers_dict[name] = fit_result.params['l_center'].value
            q_factors_dict[name] = q_fact
            # Plot the fit
            ax.plot(fit_plotting_data[0],
                    fit_plotting_data[1],
                    label=f'Fit {name} S11 \n (Q: {round(q_fact, 2)})\n (Center: {round(centers_dict[name], 2)} GHz)',
                    color=fit_colors[i],
                    ls='--',
                    lw=1.5)
            
            # Add to the legend elements
            legend_elements.append(Line2D([0], [0], color=fit_colors[i], ls='--', lw=2, label=f'(Fit {name} S11 \nQ={round(q_fact, 0)})\nCenter={round(centers_dict[name], 2)} GHz)'))
            
    
    # Plot the defined range
    if x_range is not None:
        try:
            ax.set_xlim(x_range)
        except:
            print('Issue with setting x_range, check that you input a proper list')
    if y_range is not None:
        try:
            ax.set_ylim(y_range)
        except:
            print('Issue with setting x_range, check that you input a proper list')
    # Plot the lengend now but to the right of the figure
    # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    if show_legend:
        ax.legend(handles=legend_elements, 
                  loc='center left', 
                  bbox_to_anchor=(1, 0.5), 
                  fontsize=10, 
                  frameon=False)
    ax.grid(alpha=0.5)
        
    #TODO: Fix this later so that I am outputing the results in a nicer way
    if show_plot:
        plt.show()
        if nets_to_fit_S11 is not None:
            return fig, ax, centers_dict, q_factors_dict
        else:
            return fig, ax
    else:
        if nets_to_fit_S11 is not None:
            return ax, centers_dict, q_factors_dict
        else:
            return ax

    
# TODO: Create function for plotting the smith data  
#TODO: Add the ability to pass a networks class object that already has the preset names, networks, and even range to plot, can be overriden though
#TODO: Add the option to choose the units for the frequency axis (Hz, kHz, MHz, GHz)
# # Function to plot the smith chart data from a given s-parameter
def plot_impedance(networks: str|skrf.network.Network|list[str|skrf.network.Network],
                   names = None,
                   s_to_plot: str = '11',
                   imp_to_plot: str = 'real',
                   ax = None,
                   colors: list[str] = ['#66c2a5','#fc8d62','#8da0cb','#e78ac3','#a6d854','#ffd92f','#e5c494','#b3b3b3'],
                   linestyles: list[str] = ['-','--',':','-.'],
                   title = 'Impedance (Normalized to 50 Ohm)',
                   font_size = 12,
                   x_range = None,
                   y_range = None,
                   show_legend: bool = True,
                   show_plot: bool = False,
                   x_label: str = 'Frequency (GHz)'):
    #TODO: Fix this imag_ax thing. I don't think that I want to use it anymore.
    # Get the network(s) from the input
    nets = get_networks(networks)
    # Create the names array if one doesn't exist
    if names is None:
        names = [i for i in range(len(nets))]
    
    # Create the figure if an existing axis was not provided. I will likely just use this for testing. 
    if ax == None:
        # Define variable to show the plot at the end
        show_plot = True
        # Create the figure
        fig, ax = plt.subplots(figsize = (8,6))
        
    # Raise error if weird ax is passed through 
    elif not isinstance(ax, matplotlib.axes._axes.Axes):
        raise Exception('user input "ax" argument that is not a true matplotlib axis...')
    # Set show plot to false if an axis was passed through
    else:
        show_plot = False

    # Now format the plot with the title and labels
    if title is not None:
        ax.set_title(title, fontsize=font_size)
    # Set the x label
    if x_label is not None:
        ax.set_xlabel('Frequency (GHz)', fontsize = font_size)

    # Set dict to store the impedance data
    imp_dict = {}
    # Now, loop through the parameters to plot, and then plot for each dataset
    for i, net in enumerate(nets):
    # Now calculate the impedance values and loop over each parameter defined by 
        for j, s_to_get in enumerate(s_to_plot.split(" ")):
            # get the s_data and convert it to impedance data
            s_data = get_s_data(net, s_to_get, scale='linear')
            imp_data = impedance_from_s(s_data)
            # add the impedance data to the dictionary
            imp_dict[names[i]] = imp_data
            # Plot the real
            if imp_to_plot == 'real':
                ax.axhline(y=1, color=get_color('gray', 6), alpha=0.5, ls='-', lw=1.5)
                ax.axhline(y=0, color=get_color('gray', 6), alpha=0.5, ls='-', lw=1.5)
                ax.plot(get_freq(net, units='GHz'),
                        imp_data.real,
                        label=f'{names[i]}: Re(z) from S{s_to_get}', 
                        color=colors[i],
                        ls=linestyles[j],
                        lw=2)
                
                ax.set_ylabel('Re(Z) / (50 $\Omega$)', fontsize=font_size) 
            # Plot the imaginary
            elif imp_to_plot == 'imag':
                ax.axhline(y=0, color=get_color('gray', 6), alpha=0.5, ls='-', lw=1.5)
                ax.axhline(y=1, color=get_color('gray', 6), alpha=0.5, ls='-', lw=1.5)
                ax.plot(get_freq(net, units='GHz'),
                        imp_data.imag,
                        label=f'{names[i]}: Im(z) from S{s_to_get}',
                        color=colors[i],
                        ls=linestyles[j],
                        lw=2)
                
                ax.set_ylabel('Im(Z) / (50 $\Omega$)', fontsize=font_size) 
            # Plot both
            elif imp_to_plot == 'both':
                ax.plot(get_freq(net, units='GHz'),
                        imp_data.real,
                        label=f'{names[i]}: Re(z) from S{s_to_get}', 
                        color=colors[2*i],
                        ls=linestyles[j],
                        lw=2)
                ax.plot(get_freq(net, units='GHz'),
                        imp_data.imag,
                        label=f'{names[i]}: Im(z) from S{s_to_get}',
                        color=colors[2*i+1],
                        ls=linestyles[j],
                        lw=2)
                ax.set_ylabel('Z / (50 $\Omega$)', fontsize=font_size) 
            else:
                raise Exception('Invalid imp_to_plot string input! Try "real", "imag", or "both"')
    

    
    # Plot the defined range
    if x_range is not None:
        try:
            ax.set_xlim(x_range)
        except:
            print('Issue with setting x_range, check that you input a proper list')
    if y_range is not None:
        try:
            ax.set_ylim(y_range)
        except:
            print('Issue with setting _range, check that you input a proper list')
    # Plot the lengend now but to the right of the figure
    if show_legend:
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.grid(alpha=0.5)
        
    if show_plot:
        plt.show()
        return fig, ax, imp_dict
    else:
        return ax, imp_dict

        
#TODO: Create a class called RFNetworks for working with and plotting multiple files
#TODO: Have one of the inputs be a data, and one of the inputs be a simulation network
# since that is mostly what I will be working with. 

# Function to plot the s data in one subplot and the impedance data in another
def plot_s11_and_impedance(networks: str|skrf.network.Network|list[str|skrf.network.Network],
                           names = None,
                           nets_to_plot = 'all',
                           nets_to_fit = None,
                           imps_to_plot = 'all', #TODO: Add the ability to plot the impedance data to plot
                           fit_range: str|list = 'all',
                           fig_size: tuple = (8, 10),
                           dpi: int = 150,
                           x_range = None,
                           s_y_range = None,
                           re_y_range = [-1, 3],
                           im_y_range = [-2, 2],
                           main_colors = ['cyan', 'orange', 'violet', 'pink', 'yellow']):
    #TODO: Add docstrings
    #TODO: Add the ability to change the title in the future, figure out how I want to format this.
    # Get the colors 
    s_colors = get_color_list(main_colors, 7)
    fit_colors = get_color_list(main_colors, 3)
    re_colors = get_color_list(main_colors, 5)
    imag_colors = get_color_list(main_colors, 3)
    
    # if no names are passed through, then set the names to be the index of the networks
    if names is None:
        names = [i for i in range(len(nets))]
    # Get the networks
    nets = get_networks(networks)
    # Create the nets dictionary so that I can easily access and choose from the data
    nets_dict = dict(zip(names, nets))
    # if the nets_to_plot is set to all, then set it to the names
    if nets_to_plot == 'all':
        nets_to_plot = names
    if nets_to_fit is not None:
        if isinstance(nets_to_fit, str):
            if nets_to_fit == 'all':
                nets_to_fit = names
            else:
                raise Exception('The nets_to_fit argument must be either a list of strings or the string \'all\'')

    # Create the figure and axes to plot the data
    fig, ax = plt.subplots(3, 1, 
                        sharex=True,
                        gridspec_kw={'height_ratios': [2, 1, 1], 'hspace': 0.05}, 
                        figsize=(8, 10), dpi=150)
    
    # Now plot the S11 data on the first panel, but check if the fit is desired
    if nets_to_fit is not None:
        _, cents_dict, qs_dict = plot_s_parameters(networks=networks,
                                                    names=names,
                                                    nets_to_plot=nets_to_plot,
                                                    s_to_plot='11',
                                                    nets_to_fit_S11=nets_to_fit,
                                                    fit_range=[7.1, 10],
                                                    ax=ax[0],
                                                    colors=s_colors,
                                                    fit_colors=fit_colors,
                                                    title=None,
                                                    x_range=x_range,
                                                    y_range=s_y_range,
                                                    show_legend=False,
                                                    show_plot=False,
                                                    x_label=None)
        
        # Create a custom legend for the s11 plot
        s_legend_elements = [Line2D([0], [0], color=s_colors[i], lw=2, label=name) for i, name in enumerate(nets_to_plot)] + \
                            [Line2D([0], [0], color=fit_colors[i], ls='--', lw=2, label=f'(Fit {name}\nCenter={cents_dict[name]:.2f} GHz \n Q={qs_dict[name]:.0f})') for i, name in enumerate(nets_to_fit)]
        ax[0].legend(handles=s_legend_elements, 
                     loc='center left', 
                     bbox_to_anchor=(1, 0.5), 
                     fontsize=10, 
                     frameon=False, 
                     title=r'$\bf{S11}$')
        
        # Now for the impedance data
        # For the real data
        _ , imp_dict = plot_impedance(networks=networks,
                                       names=names,
                                       imp_to_plot='real',
                                       x_range=x_range,
                                       y_range=re_y_range,
                                       ax=ax[1],
                                       title=None,
                                       colors=re_colors,
                                       show_legend=False,
                                       x_label=None)
        
        # For the imaginary data
        plot_impedance(networks=networks,
                       names=names,
                       imp_to_plot='imag',
                       x_range=x_range,
                       y_range=im_y_range,
                       ax=ax[2],
                       title=None,
                       colors=imag_colors,
                       show_legend=False)
        
        # Now calculate the impedances at the center frequencies
        imp_cents_dict = {}
        for i, name in enumerate(nets_to_fit):
            imp_cents_dict[name] = imp_dict[name][np.argmin(np.abs(get_freq(nets_dict[name], units='GHz') - cents_dict[name]))]
            
        # Now plot the center frequencies on the impedance plots
        for i, ax_ in enumerate(ax[1:]):
            for i, name in enumerate(names):
                ax_.axvline(cents_dict[name], color=s_colors[i], linestyle='--', linewidth=2, alpha=0.5)
        
        # Now add the legends for the impedance plots
        re_legend_elements = [Line2D([0], [0], color=re_colors[i], lw=2, label=name) for i, name in enumerate(nets_to_plot)] + \
                             [Line2D([0], [0], color=s_colors[i], ls='--', lw=2, alpha=0.5, label=f'{cents_dict[name]:.2f} GHz \nZ={imp_cents_dict[name]*50:.2f} $\Omega$') for i, name in enumerate(nets_to_fit)]
        # Now for the imaginary
        im_legend_elements = [Line2D([0], [0], color=imag_colors[i], lw=2, label=name) for i, name in enumerate(nets_to_plot)] + \
                             [Line2D([0], [0], color=s_colors[i], ls='--', lw=2, alpha=0.5, label=f'{cents_dict[name]:.2f} GHz \nZ={imp_cents_dict[name]*50:.2f} $\Omega$') for i, name in enumerate(nets_to_fit)]
        # Now plot the legends
        ax[1].legend(handles=re_legend_elements, 
                     loc='center left', 
                     bbox_to_anchor=(1, 0.5), 
                     fontsize=10, 
                     frameon=False, 
                     title=r'$\bf{Re(Z)}$')
        ax[2].legend(handles=im_legend_elements, 
                     loc='center left', 
                     bbox_to_anchor=(1, 0.5), 
                     fontsize=10, 
                     frameon=False, 
                     title=r'$\bf{Im(Z)}$')

    # Now if no fit is desired, then just plot all of the data
    else:
        plot_s_parameters(networks=networks,
                          names=names,
                          nets_to_plot=nets_to_plot,
                          s_to_plot='11',
                          nets_to_fit_S11=nets_to_fit,
                          fit_range=[7.1, 10],
                          ax=ax[0],
                          colors=s_colors,
                          fit_colors=fit_colors,
                          title=None,
                          x_range=x_range,
                          y_range=s_y_range,
                          show_legend=False,
                          show_plot=False,
                          x_label=None)
        
        re_legend_elements = [Line2D([0], [0], color=re_colors[i], lw=2, label=name) for i, name in enumerate(nets_to_plot)]
        im_legend_elements = [Line2D([0], [0], color=imag_colors[i], lw=2, label=name) for i, name in enumerate(nets_to_plot)]
        # Create a custom legend for the s11 plot
        s_legend_elements = [Line2D([0], [0], color=s_colors[i], lw=2, label=name) for i, name in enumerate(nets_to_plot)]
        ax[0].legend(handles=s_legend_elements, 
                     loc='center left', 
                     bbox_to_anchor=(1, 0.5), 
                     fontsize=10, 
                     frameon=False, 
                     title=r'$\bf{S11}$')
        
        # Now plot the impedance data on the second and third panels
        # For the real data
        _ , imp_dict = plot_impedance(networks=networks,
                                       names=names,
                                       imp_to_plot='real',
                                       x_range=x_range,
                                       y_range=re_y_range,
                                       ax=ax[1],
                                       title=None,
                                       colors=re_colors,
                                       show_legend=False,
                                       x_label=None)
        
        # For the imaginary data
        plot_impedance(networks=networks,
                       names=names,
                       imp_to_plot='imag',
                       x_range=x_range,
                       y_range=im_y_range,
                       ax=ax[2],
                       title=None,
                       colors=imag_colors,
                       show_legend=False)
        
        # Get the legend info
        re_legend_elements = [Line2D([0], [0], color=re_colors[i], lw=2, label=name) for i, name in enumerate(nets_to_plot)]
        im_legend_elements = [Line2D([0], [0], color=imag_colors[i], lw=2, label=name) for i, name in enumerate(nets_to_plot)]
        # Create the legends
        # Real
        ax[1].legend(handles=re_legend_elements, 
                     loc='center left', 
                     bbox_to_anchor=(1, 0.5), 
                     fontsize=10, 
                     frameon=False, 
                     title=r'$\bf{Re(Z)}$')
        ax[2].legend(handles=im_legend_elements, 
                     loc='center left', 
                     bbox_to_anchor=(1, 0.5), 
                     fontsize=10, 
                     frameon=False, 
                     title=r'$\bf{Im(Z)}$')
    