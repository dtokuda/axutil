import os 
import sys
import numpy as np
import matplotlib.pyplot as plt

from .util import merge_axes

__all__ = [
    'GridSpecFig',
]

# ===================================================================================================
class GridSpecFig:
    '''
    Attributes:
        gs (matplotlib.gridspec.GridSpec)
        axs (np.ndarray (dtype = object)): -> plt.Axes
        data (np.ndarray (dtype = object))
    '''

    def __init__(self, figsize=None, axsize=None, nrows=1, ncols=1, direction='row', **kwargs):
        if not figsize is None:
            _figsize = figsize
            if not axsize is None:
                assert(figsize[0] == axsize[0] * ncols)
                assert(figsize[1] == axsize[1] * nrows)
        else:
            if not axsize is None:
                _figsize = (axsize[0] * ncols, axsize[1] * nrows)
            else:
                _figsize = (5, 3)
        self.figure = plt.figure(figsize=_figsize)
        self.gs = self.figure.add_gridspec(nrows=nrows, ncols=ncols, **kwargs)
        #self.axs = FlattenObjectArray((nrows, ncols))
        #self.data = FlattenObjectArray((nrows, ncols))
        self.axs = np.ndarray((nrows, ncols), dtype=object)
        for irow in range(nrows):
            for icol in range(ncols):
                self.axs[irow, icol] = self.figure.add_subplot(self.gs[irow, icol])
        self.data = np.ndarray((nrows, ncols), dtype=object)
    
        self.direction = direction

    # ===============================================================================================
    @property
    def nrows(self): return self.gs.nrows

    @property
    def ncols(self): return self.gs.ncols

    def __getitem__(self, ind):
        return self.axs[ind]

    def __setitem__(self, ind, ax):
        self.axs[ind] = ax

    # ===============================================================================================
    def is_left(self, icol):
        return icol == 0

    def is_right(self, icol):
        return icol == self.gs.ncols - 1

    def is_top(self, irow):
        return irow == 0

    def is_bottom(self, irow):
        return irow == self.gs.nrows - 1

    # ===============================================================================================
    def set_direction(self, direction):
        if isinstance(direction, int):
            direction = {0: 'row', 1: 'col'}[direction]
        self.direction = direction
        
    def __iter__(self):
        self.row_index = 0
        self.col_index = 0
        return self

    def __next__(self):
        if self.direction == 'row':
            if self.row_index < self.nrows:
                ax = self[self.row_index, self.col_index]
                self.col_index += 1
                if self.col_index == self.ncols:
                    self.col_index = 0
                    self.row_index += 1
                return ax
            else:
                raise StopIteration
        elif self.direction == 'col':
            if self.col_index < self.ncols:
                val = self[self.row_index, self.col_index]
                self.row_index += 1
                if self.row_index == self.nrows:
                    self.row_index = 0
                    self.col_index += 1
                return val
            else:
                raise StopIteration
        else:
            raise ValueError("Invalid direction. Please select 'row' or 'col'.")

    # ===============================================================================================
    def get_merged_axes(self, irow=None, icol=None, **kwargs):
        '''
        Args:
            irow (int or None)
            icol (int or None)
            kwargs: for plt.figure.add_axes()
        '''
        if irow is None:
            ax0, ax1 = self[0, icol], self[-1, icol]
        elif icol is None:
            ax0, ax1 = self[irow, 0], self[irow, -1]
        else:
            ax0, ax1 = self[0, 0], self[-1, -1]
        return merge_axes(ax0, ax1, **kwargs)