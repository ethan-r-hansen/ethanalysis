import lmfit
import numpy as np
from ethanalysis.fitting.models import LorentzianConstBG
from ethanalysis.utils.main import truncate_data


# Create a function to fit the S11 resonance dip's to a lorentzian model
def fit_s11_resonance_dip(freq_data: np.ndarray,
                          s11_data: np.ndarray,
                          fit_range: list|str = 'all')-> lmfit.model.ModelResult:
    # Write the docstrings for the function
    """
    Fit the S11 resonance dip to a Lorentzian model.

    Parameters
    ----------
    freq_data : np.ndarray
        Frequency data.
    s11_data : np.ndarray

    fit_range : list|str, optional
        Range of data to fit. Default is 'all'. To choose a range, input a list of the form [min, max].
        
    Returns
    -------
    lmfit.ModelResult
        Result of the fit.
    """
    # Truncate the data to the fit range if input is not 'all'
    if isinstance(fit_range, list):
        try:
            x_fitting_data, y_fitting_data = truncate_data(freq_data, s11_data, fit_range)
        except ValueError:
            raise ValueError('The fit range is not valid. Improperly formatted list.')
    elif isinstance(fit_range, str):
        if fit_range == 'all':
            x_fitting_data, y_fitting_data = freq_data, s11_data
        else:
            raise ValueError('The fit range is not valid. The only string allowed is \'all\'.')
        #TODO: Add an option to 'guess' the fit range. This will choose the min value as a center and set a width
    else:
        raise ValueError('The fit range is not valid.')
    
    # Create a model for the S11 resonance dip
    model = LorentzianConstBG()
    
    # Create a parameters object for the model
    params = model.make_params()
    
    # Create the initial guesses for the parameters
    guess_center = x_fitting_data[np.argmin(y_fitting_data)]
    guess_background = max(y_fitting_data)
    # Set the initial guesses for the parameters
    params['l_center'].set(value=guess_center, min=x_fitting_data[0], max=x_fitting_data[-1])
    # params['l_amplitude'].set(value=-data[s11_col].min(), min=-data[s11_col].max(), max=-data[s11_col].min())
    params['l_sigma'].set(value=0.1, min=0.001, max=1)
    params['bg_c'].set(value=guess_background, min=min(y_fitting_data)/2, max=0)
    
    # Perform the fit
    result = model.fit(y_fitting_data, params, x=x_fitting_data)
    # calculate the Q factor
    q_factor = result.params['l_center'] / result.params['l_sigma']
    
    fit_plotting_data = [x_fitting_data, result.best_fit]
    
    # Return the result
    #TODO: Return the Q factor and the plot fitting data. 
    return result, q_factor, fit_plotting_data