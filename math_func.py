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

__all__ = ['generic_interpolate','find_quant','cal_pdf']
__author__="Dexter S.-H. Hon"

def generic_interpolate():
    # generic interpolate method Cubic spline and what not
    return None

def find_quant(curve, quant, price):
    """
    This is an inverse Spline interpolation treating the cdf as the x-axis.
    This is meant to find the corresponding quantile with a given price.
    
    This function assumes a range of probability distribution function in
    between 0.0025 and 0.9975 qantiles that has a 0.0025 interval

    Parameters
    ----------
    curve : 1D pandas dataframe
        A 1D array that contains a discrete number of cdf points.
    price : float
        The given price.

    Returns
    -------
    quant : float
        The corresponding quantile.

    """

    spline_apc = CubicSpline(curve, quant)
    quant = spline_apc(price)
    return quant
    

def cal_pdf(x,cdf):
    #cdf
    even_spaced_prices = np.arange(np.min(cdf), np.max(cdf), 0.005)
    
    print(len(even_spaced_prices))
    
    spline_apc_rev = UnivariateSpline(cdf, np.arange(0.0025, 0.9975, 0.0025), s = 0)
    quantiles_even_prices = spline_apc_rev(even_spaced_prices)

    dq = even_spaced_prices[1]-even_spaced_prices[0]
    deriv = fd.FinDiff(0, dq, 1)
    pdf = deriv(quantiles_even_prices)
    
    print(len(pdf))
    
    spline_pdf = UnivariateSpline(even_spaced_prices, pdf,  s = 0.0015)
    pdf = spline_pdf(even_spaced_prices)
    
    print(len(pdf))
    return even_spaced_prices, pdf