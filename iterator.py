#! /usr/bin/env python
import os
import sys
import matplotlib.pyplot as plt

__all__ = [
    'AxesIterator'
]
# ===================================================================================================
class AxesIterator:
    '''
    Attributes:
        ax_no (int): count of Axes in one Figure (1-origin)
        pos_idx (int): 
    '''

    def __init__(self, nrows=1, ncols=1, transpose=False,
                 kw_figure={}, figsize=(8,6),
                 kw_add_subplot={},
                 kw_subplots_adjust={}, suptitle=None,
                 show=True, savefig=True, 
                 outdir='./', namefmt='{:03d}.png', start_fig_no=0, printpath=True):
        self.ax_no  = -1 # 1-origin
        self.transpose = transpose
        self.fig_no = start_fig_no - 1
        self.fig_no_start = start_fig_no

        # subplot
        self.nrows = nrows
        self.ncols = ncols
        self.kw_figure = kw_figure
        self.kw_figure.update({'figsize': figsize})
        self.kw_add_subplot = kw_add_subplot
        self.kw_subplots_adjust = kw_subplots_adjust
        self.suptitle = suptitle

        # finalize
        self.show = show
        self.savefig = savefig
        self.outdir = outdir
        self.namefmt = namefmt
        self.printpath = printpath
        if savefig: os.makedirs(outdir, exist_ok=True)

    # -----------------------------------------------------------------------------------------------
    def __iter__(self):
        return self

    
    def __next__(self):
        if self.__is_first_figure():
            self.__refresh_figure()
            return self.__add_subplot()

        elif self.is_last:
            self.finalize()
            self.__refresh_figure()
            return self.__add_subplot()

        else:
            return self.__add_subplot()


    def next(self):
        return self.__next__()


    def finalize(self):
        self.__subplots_adjust()
        self.__set_suptitle()
        if self.savefig: self.__save_fig()
        if self.show: plt.show()
        plt.close()

    # -----------------------------------------------------------------------------------------------
    @property
    def is_first(self):
        return self.ax_no == 1

    @property
    def is_last(self):
        return self.ax_no == self.nrows * self.ncols

    # -----------------------------------------------------------------------------------------------
    @property
    def is_top(self):
        return self.position_index <= self.ncols

    @property
    def is_bottom(self):
        return self.position_index >= self.ncols * (self.nrows - 1) + 1

    @property
    def is_left(self):
        return self.position_index % self.ncols == 1

    @property
    def is_right(self):
        return self.position_index % self.ncols == 0

    # -----------------------------------------------------------------------------------------------
    def __refresh_figure(self):
        self.fig_no += 1
        self.ax_no = 0
        self.figure = plt.figure(**self.kw_figure)
        #self.__subplots_adjust()


    def __add_subplot(self):
        self.ax_no += 1
        ax = self.figure.add_subplot(self.nrows, self.ncols, self.position_index,
            **self.kw_add_subplot)
        return ax


    def __is_first_figure(self):
        return self.fig_no < self.fig_no_start

    # -----------------------------------------------------------------------------------------------
    def __subplots_adjust( self ):
        if not self.kw_subplots_adjust is None:
            self.figure.subplots_adjust( **self.kw_subplots_adjust )
            #plt.subplots_adjust( **self.kw_subplots_adjust )
        else:
            self.figure.tight_layout()

    def __save_fig(self):
        outpath = os.path.join(self.outdir, self.namefmt.format(self.fig_no))
        plt.savefig(outpath, bbox_inches='tight', pad_inches=0.05)
        if self.printpath:
            print( ' ', outpath )

    def __set_suptitle(self):
        '''
        TODO: array-like suptitle
        '''
        if self.suptitle is None:
            return
        title = self.suptitle if isinstance(self.suptitle, str) else None
        top = 0.9
        self.figure.suptitle(title)
        self.figure.subplots_adjust(top=top)

    @property
    def position_index(self):
        '''
        convert row-major index to column-major index
        https://stackoverflow.com/questions/49054631/fill-matplotlib-subplots-by-column-not-row
        '''
        if self.transpose:
            return ((self.ax_no - 1) % self.nrows) * self.ncols + (self.ax_no - 1) // self.nrows + 1
        else:
            return self.ax_no

    # -----------------------------------------------------------------------------------------------
    def add_axes(self, rect, **kwargs):
        '''
        Args:
            rect ((float, float, float, float)): (left, bottom, width, height)
            kwargs: for plt.Figure.add_axes()
        Returns:
            plt.Axes
        '''
        return self.figure.add_axes(rect, **kwargs)
