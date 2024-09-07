import os
import sys
import matplotlib.pyplot as plt

__all__ = [
    'get_rect', 'get_size_inches',
    'replace_axes', 'add_axes',
    'merge_axes',
    'vsplit', 'hsplit',
]

# ===================================================================================================
def get_rect(ax):
    '''
    Args:
        ax (plt.Axes
    Returns:
        (left, bottom, width, height)
    '''
    bbox = ax.get_position()
    left = bbox.xmin
    right  = bbox.xmax
    bottom = bbox.ymin
    top    = bbox.ymax
    return left, bottom, right - left, top - bottom


def get_size_inches(ax):
    '''
    Args:
        ax (plt.Axes)
    Returns:
        width (scalar)
        height (scalar)
    '''
    fig_width, fig_height = ax.get_figure().get_size_inches()
    _, _, frac_width, frac_height = get_rect(ax)
    return fig_width * frac_width, fig_height * frac_height

# ===================================================================================================
def replace_axes(ax, *args, **kwargs):
    '''
    Args:
        ax (plt.Axes)
        args, kwargs: for fig.add_axes()
    Returns:
        ret (plt.Axes)
    '''
    fig = ax.get_figure()
    ret = fig.add_axes(get_rect(ax), *args, **kwargs)
    #ax.remove()
    return ret


def add_axes(ax, rect=None, **kwargs):
    '''
    Args:
        ax (plt.Axes)
        rect ((float, float, float, float)): (left, bottom, width, height)
            refer to plt.rcParams if None
    Returns:
        (plt.Axes)
    '''
    left0, bottom0, width0, height0 = get_rect(ax)
    if rect is None:
        rect = (
            plt.rcParams['figure.subplot.left'  ],
            plt.rcParams['figure.subplot.bottom'],
            plt.rcParams['figure.subplot.right' ] - plt.rcParams['figure.subplot.left'  ],
            plt.rcParams['figure.subplot.top'   ] - plt.rcParams['figure.subplot.bottom'],
        )
    leftr, bottomr, widthr, heightr = rect
    left1   = left0 + width0 * leftr
    bottom1 = bottom0 + height0 * bottomr
    width1  = width0 * widthr
    height1 = height0 * heightr

    fig = ax.get_figure()
    return fig.add_axes((left1, bottom1, width1, height1), **kwargs)

# ===================================================================================================
def merge_axes(ax0, ax1, *args, **kwargs):
    '''
    Args:
        ax0, ax1 (Axes)
    Returns:
        ax (Axes)
    '''
    left0, bottom0, width0, height0 = get_rect(ax0)
    right0 = left0 + width0
    top0 = bottom0 + height0
    
    left1, bottom1, width1, height1 = get_rect(ax1)
    right1 = left1 + width1
    top1 = bottom1 + height1
    
    left = min(left0, left1)
    bottom = min(bottom0, bottom1)
    right = max(right0, right1)
    top = max(top0, top1)
    
    #print(left, bottom, right - left, top - bottom)
    ax = ax0.figure.add_axes((left, bottom, right - left, top - bottom), *args, **kwargs)
    return ax

# ===================================================================================================
# v/hsplit supports hspace and wspace, but not left, right, bottom, and top in subplots_adjust
def vsplit(ax, v, hspace=None, *args, **kwargs):
    '''
    Args:
        ax (plt.Axes)
        v (array-like or float or int): split ratio from top. if int, split into same height
        hspace (float): "the amount of height reserved for space between subplots,
                         expressed as a fraction of the average axis height"
                        default to plt.rcParams['figure.subplot.hspace']
        *args, **kwargs: for Figure.add_axes
    Returns:
        (tuple of Axes): from top to bottom
    '''
    if hspace is None: hspace = plt.rcParams['figure.subplot.hspace']
    left, bottom, width, height = get_rect(ax)
    ax.tick_params(
        left=False, bottom=False, right=False, top=False,
        labelleft=False, labelbottom=False, labelright=False, labeltop=False
    )

    if isinstance(v, int):
        if v == 1: return [ax]
        rheights = __int2interval(v, hspace)
        rhspaces = [rheights[0] * hspace] * (v - 1)
    else:
        rheights = v
        #rheights = __bound2interval(v)
        rhspaces = [0.0] * (len(v) - 1)
    heights = [rheight * height for rheight in rheights]
    hspaces = [rhspace * height for rhspace in rhspaces]

    _bottom = bottom + height - heights[0]
    bottoms = [_bottom]
    for _height, _hspace in zip(heights[1:], hspaces):
        _bottom -= (_height + _hspace)
        bottoms += [_bottom]
    fig = ax.get_figure()
    return [
        fig.add_axes((left, _bottom, width, _height), *args, **kwargs)
        for _bottom, _height in zip(bottoms, heights)
    ]


def hsplit(ax, h, wspace=None, *args, **kwargs):
    '''
    Args:
        ax (plt.Axes)
        h (array-like or float): split ratio from left. if int, split into same width
        wspace (float): "the amount of width reserved for space between subplots,
                         expressed as a fraction of the average axis width"
                        default to plt.rcParams['figure.subplot.wspace']
        *args, **kwargs: for Figure.add_axes
    Returns:
        ([plt.Axes]): from left to right
    '''
    if wspace is None: wspace = plt.rcParams['figure.subplot.wspace']
    left, bottom, width, height = get_rect(ax)
    ax.tick_params(
        left=False, bottom=False, right=False, top=False,
        labelleft=False, labelbottom=False, labelright=False, labeltop=False
    )
                     
    if isinstance(h, int):
        if h == 1: return [ax]
        rwidths = __int2interval(h, wspace)
        rwspaces = [rwidths[0] * wspace] * (h - 1)
    else:
        rwidths = h
        #rwidths = __bound2interval(h)
        rwspaces = [0.0] * (len(h) - 1)
    widths = [rwidth * width for rwidth in rwidths]
    wspaces = [rwspace * width for rwspace in rwspaces]

    _left = left
    lefts = [_left]
    for _width, _wspace in zip(widths[:-1], wspaces):
        _left += _width + _wspace
        lefts += [_left]
    fig = ax.get_figure()
    return [
        fig.add_axes((_left, bottom, _width, height), *args, **kwargs)
        for _left, _width in zip(lefts, widths)
    ]


def __int2interval(a, space=0.0):
    '''
    Args:
        a (int): split number. should be a > 1
        space (float): "the amount of height/width reserved for space between subplots
                        expressed as a fraction of the average axis height/width"
    Returns:
        bounds (list of float)
    '''
    if a < 2:
        raise ValueError('__int2intervalaries: a should be > 1, but {}'.format(a))
    return [1.0 / (float(a) + float(a - 1) * space)] * a
