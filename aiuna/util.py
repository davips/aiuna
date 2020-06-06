"""This module keep util function used in pjdata."""
import importlib
import warnings
from typing import List, Dict, Union, Any

# importing the module that contains the global variables.
from numpy import ndarray

GLOBAL_VARS_MODULE = importlib.import_module("pjdata.glconfig")


def gl_config(**kwargs):
    """Handle global variables values.

    Parameters
    ----------
    **kwargs
        Global variables and their respective new values.

    Notes
    -----
    Use 'ls_gl_config()' to see all global variables available.
    For more information see `global_configuration_handler`.
    """
    global_configuration_handler(module=GLOBAL_VARS_MODULE, **kwargs)


def ls_gl_config(show_values: bool = False) -> Union[List[str], Dict[str, Any]]:
    """List global variables from `glconfig` module.

    Notes
    -----
    See `ls_global_configuration_handler` for more information.
    """
    return ls_global_configuration_handler(GLOBAL_VARS_MODULE, show_values)


def ls_global_configuration_handler(
        module: str,
        show_values: bool = False) -> Union[List[str], Dict[str, Any]]:
    """List global variables from a givem module.

    Parameters
    ----------
    module
        A python module.

    show_values : bool
        If True return a dictionary with the global variables names and values.
        If False return a list with only the global variable names.

    Returns
    -------
    list, dict
        When `show_values=False`, a list with the global variable names.
        When `show_values=True`, a dict with global variable names and values.

    Notes
    -----
    Global variables should follow PEP8 format.
    """
    if show_values:
        return {key: value
                for key, value in module.__dict__.items() if key.isupper()}
    return [item for item in module.__dict__.keys() if item.isupper()]


def global_configuration_handler(module: str, **kwargs):
    """Handle global variables values.

    Parameters
    ----------
    module : module
        A python module.
    **kwargs
        Global variables and their respective new values.

    Examples
    --------
    >>> from pjdata.util import gl_config
    >>> gl_config(pretty_printing=True, does_nothing=False)

    Notes
    -----
    Use 'ls_global_configuration_handler()' to see all global variables
    available from a given python module.
    """
    gl_var = ls_global_configuration_handler(module)
    for key, value in kwargs.items():
        key = key.upper()
        if key in gl_var:
            module.__dict__[key] = value
        else:
            warnings.warn(f'Variable {key} not found.'
                          f'This configuration was ignored!')
