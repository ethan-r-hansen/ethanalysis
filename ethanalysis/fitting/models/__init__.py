# Module that contains the models used for fitting data. Add the docstrings here to make 
# These will be functions that output the desired models if I have to make additional ones not provided by lmfit. 
# sure that they are included in the documentation and are easy to understand. 
from lmfit.models import LorentzianModel, ConstantModel
import lmfit

# Lorentzian on constant background
def LorentzianConstBG(lorentzian_prefix: str='l_',
                      bg_prefix: str='bg_')-> lmfit.Model:
    """
    Lorentzian model on constant background.
    The Lorentzian model has three paramters: center, amplitude, and sigma.
    The constant background has one parameter: c.
    
    Parameters
    ----------
    lorentzian_prefix : str
        Prefix for the Lorentzian model parameters. Default is 'v_'.
    bg_prefix : str
        Prefix for the constant background parameters. Default is 'bg_'.
        
    Returns
    -------
    lmfit.Model
        Lorentzian model on constant background.
    """
    return LorentzianModel(prefix=lorentzian_prefix) + ConstantModel(prefix=bg_prefix)
