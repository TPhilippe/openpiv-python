#!/usr/bin/env python
"""The openpiv.tools module is a collection of utilities and tools.
"""

__licence__ = """
Copyright (C) 2011  www.openpiv.net

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import glob
import sys
import os.path
import multiprocessing

import numpy as np
import scipy.misc
import matplotlib.pyplot as pl



def display_vector_field( filename,**kw):
    """ Displays quiver plot of the data stored in the file 
    
    
    Parameters
    ----------
    filename :  string
        the absolute path of the text file
    
    Key arguments   : (additional parameters, optional)
        *scale*: [None | float]
        *width*: [None | float]
    
    
    See also:
    ---------
    matplotlib.pyplot.quiver
    
        
    Examples
    --------
    
    >>> openpiv.tools.display_vector_field('./exp1_0000.txt',scale=100, width=0.0025) 

    
    """
    
    a = np.loadtxt(filename)
    pl.figure()
    pl.hold(True)
    invalid = a[:,4].astype('bool')
    
    valid = ~invalid
    pl.quiver(a[invalid,0],a[invalid,1],a[invalid,2],a[invalid,3],color='r',**kw)
    pl.quiver(a[valid,0],a[valid,1],a[valid,2],a[valid,3],color='b',**kw)
    pl.draw()
    pl.show()

def imread( filename, flatten=0 ):
    """Read an image file into a numpy array
    using scipy.misc.imread
    
    Parameters
    ----------
    filename :  string
        the absolute path of the image file
    flatten :   bool
        True if the image is RGB color or False (default) if greyscale
        
    Returns
    -------
    frame : np.ndarray
        a numpy array with grey levels
        
        
    Examples
    --------
    
    >>> image = openpiv.tools.imread( 'image.bmp' )
    >>> print image.shape 
        (1280, 1024)
    
    
    """
    
    return scipy.misc.imread( filename, flatten=flatten).astype(np.int32)

def save( x, y, u, v, mask, filename, fmt='%8.4f', delimiter='\t' ):
    """Save flow field to an ascii file.
    
    Parameters
    ----------
    x : 2d np.ndarray
        a two dimensional array containing the x coordinates of the 
        interrogation window centers, in pixels.
        
    y : 2d np.ndarray
        a two dimensional array containing the y coordinates of the 
        interrogation window centers, in pixels.
        
    u : 2d np.ndarray
        a two dimensional array containing the u velocity components,
        in pixels/seconds.
        
    v : 2d np.ndarray
        a two dimensional array containing the v velocity components,
        in pixels/seconds.
        
    mask : 2d np.ndarray
        a two dimensional boolen array where elements corresponding to
        invalid vectors are True.
        
    filename : string
        the path of the file where to save the flow field
        
    fmt : string
        a format string. See documentation of numpy.savetxt
        for more details.
    
    delimiter : string
        character separating columns
        
    Examples
    --------
    
    >>> openpiv.tools.save( x, y, u, v, 'field_001.txt', fmt='%6.3f', delimiter='\t')
    
    """
    # build output array
    out = np.vstack( [m.ravel() for m in [x, y, u, v, mask] ] )
            
    # save data to file.
    np.savetxt( filename, out.T, fmt=fmt, delimiter=delimiter )

def display( message ):
    """Display a message to standard output.
    
    Parameters
    ----------
    message : string
        a message to be printed
    
    """
    sys.stdout.write(message)
    sys.stdout.write('\n')
    sys.stdout.flush()

class Multiprocesser():
    def __init__ ( self, data_dir, pattern_a, pattern_b  ):
        """A class to handle and process large sets of images.

        This class is responsible of loading image datasets
        and processing them. It has parallelization facilities
        to speed up the computation on multicore machines.
        
        It currently support only image pair obtained from 
        conventional double pulse piv acquisition. Support 
        for continuos time resolved piv acquistion is in the 
        future.
        
        
        Parameters
        ----------
        data_dir : str
            the path where image files are located 
            
        pattern_a : str
            a shell glob patter to match the first 
            frames.
            
        pattern_b : str
            a shell glob patter to match the second
            frames.

        Examples
        --------
        >>> multi = openpiv.tools.Multiprocesser( '/home/user/images', 'image_*_a.bmp', 'image_*_b.bmp')
    
        """
        # load lists of images 
        self.files_a = sorted( glob.glob( os.path.join( os.path.abspath(data_dir), pattern_a ) ) )
        self.files_b = sorted( glob.glob( os.path.join( os.path.abspath(data_dir), pattern_b ) ) )
        
        # number of images
        self.n_files = len(self.files_a)
        
        # check if everything was fine
        if not len(self.files_a) == len(self.files_b):
            raise ValueError('Something failed loading the image file. There should be an equal number of "a" and "b" files.')
            
        if not len(self.files_a):
            raise ValueError('Something failed loading the image file. No images were found. Please check directory and image template name.')

    def run( self, func, n_cpus=1 ):
        """Start to process images.
        
        Parameters
        ----------
        
        func : python function which will be executed for each 
            image pair. See tutorial for more details.
        
        n_cpus : int
            the number of processes to launch in parallel.
            For debugging purposes use n_cpus=1
        
        """

        # create a list of tasks to be executed.
        image_pairs = [ (file_a, file_b, i) for file_a, file_b, i in zip( self.files_a, self.files_b, xrange(self.n_files) ) ]
        
        # for debugging purposes always use n_cpus = 1,
        # since it is difficult to debug multiprocessing stuff.
        if n_cpus > 1:
            pool = multiprocessing.Pool( processes = n_cpus )
            res = pool.map( func, image_pairs )
        else:
            for image_pair in image_pairs:
                func( image_pair )
                
                
