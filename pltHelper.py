import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def surveyGradingProgress(results, category_names):
    # https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/horizontal_barchart_distribution.html
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.get_cmap('RdYlGn')(
        np.linspace(0.3, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        ax.barh(labels, widths, left=starts, height=0.5,
                label=colname, color=color)
        xcenters = starts + widths / 2

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        for y, (x, c) in enumerate(zip(xcenters, widths)):
            if c == 0:  
                continue
            ax.text(x, y, str(int(c)), ha='center', va='center',
                    color=text_color)
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='x-small')
    return fig, ax

def surveyDistribution(f, data, max, axs, figname): 
    plt.hist(data, bins=max)
    plt.xlim(0, max)
    plt.xlabel('Score')
    plt.ylabel('Frequency')

    plt.savefig('tex/fig/'+figname + '.png', bbox_inches='tight', dpi=300)
    # -- Insert figure into LaTeX
    fwidth = 3   # figure width in inches
    f.write(r"\includegraphics[width="+str(fwidth)+"in]{fig/"+figname+r".png}\\")
    plt.clf() 
