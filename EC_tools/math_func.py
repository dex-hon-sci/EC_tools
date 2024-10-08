#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 03:05:10 2024

@author: dexter

This is a utility library for mathematical operations.

"""
import numpy as np
from scipy.interpolate import CubicSpline, UnivariateSpline
import findiff as fd 

__all__ = ['generic_spline','find_quant','cal_pdf']
__author__="Dexter S.-H. Hon"

def generic_spline(x,y, method="cubic", s = 0):
    """
    A generic method to interpolate data.

    Parameters
    ----------
    x : numpy array
        x-axis.
    y : numpy array
        y-axis.
    method : str, optional
        The method of interpolation. The default is "cubic".

    Returns
    -------
    func : TYPE
        A callable function.

    """
    # generic interpolate method Cubic spline and what not
    method_dict = {'cubic': CubicSpline,
                   'univariate': UnivariateSpline}
    
    func = method_dict[method]
# =============================================================================
#     if method == "cubic":
#         func = CubicSpline(x, y) 
#     elif method =="univariate":
#         func = UnivariateSpline(x, y, s=s) 
# =============================================================================
    return func(x,y)

def find_quant(cdf, quant_list, val):
    """
    This is an inverse Spline interpolation treating the cdf as the x-axis.
    This is meant to find the corresponding quantile with a given price.
    
    This function assumes a range of probability distribution function in
    between 0.0025 and 0.9975 qantiles that has a 0.0025 interval

    Parameters
    ----------
    cdf : 1D pandas dataframe
        A 1D array that contains a discrete number of cdf points.
    val : float
        The given value (e.g. price).

    Returns
    -------
    quant : float
        The corresponding quantile.

    """
    spline = CubicSpline(cdf, quant_list)
    quant = spline(val)
    return float(quant)
    

def cal_pdf(quant, cdf):
    """
    Calcualte the probability distribution function (pdf) from a cumulative 
    probability distribution function (cdf).

    Parameters
    ----------
    quant : 1D list
        The distribution of the events.
    cdf : 1D list
        The value of the cdf.

    Returns
    -------
    spaced_events : 1D list
        The value of the events.
    pdf : 1D list
        The probability of the events.

    """
    # Define the evenly spaced events for the cdf
    spaced_events = np.arange(np.min(cdf), np.max(cdf), 0.005)
    #print(len(spaced_events))
    
    # interpolate the qunatile given the cdf
    spline_apc_rev = UnivariateSpline(cdf, quant, s = 0)
    quant_even_prices = spline_apc_rev(spaced_events) # get the corresponding quantile

    # make the differential dq using the 1st and 2nd elements
    dq = spaced_events[1]-spaced_events[0]
    deriv = fd.FinDiff(0, dq, 1) 
    pdf = deriv(quant_even_prices) # perform the differentiation on cdf, outcome the pdf
    
    #print(len(pdf))
    
    # interpolate the pdf with the spaced events
    spline_pdf = UnivariateSpline(spaced_events, pdf,  s = 0.0015)
    pdf = spline_pdf(spaced_events)
    
    #print(len(pdf))
    return spaced_events, pdf

def find_pdf_val(pdf_val, pdf, func= max):
    """
    A generic method to extract the price of a particular centile given
    a function operation over the pdf. For example, func can be max(),
    median(), average(), lambda functions, etc.
    
    Parameters
    ----------
    pdf_val : 
        
    pdf :
    
    func
    
    Returns
    ------_
    Price for that centile        
    """
    centile_index = list(pdf).index(func(pdf))

    return float(pdf_val[centile_index])

    
def find_pdf_quant(pdf_val, pdf, func= max):
    """
    A generic method to extract the price of a particular centile given
    a function operation over the pdf. For example, func can be max(),
    median(), average(), lambda functions, etc.
    
    Parameters
    ----------
    pdf_val : 
        
    pdf :
    
    func
    
    Returns
    ------_
    Price for that centile        
    """
    centile_index = list(pdf).index(func(pdf))

    return float(pdf[centile_index])


def get_2nd_moment(pdf: np.ndarray):
    mean = np.average(pdf)
    x = np.arange(start = None, stop = None, step = None)
    
    return