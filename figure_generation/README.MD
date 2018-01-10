# remote_refocus
Scripts used to generate the figures in the remote refocus manuscript. One script for each interactive figure, e.g.: `figure_1_worm_DIC.py`,
`figure_1_worm_TL_FL.py`, `figure_2_yeast_cyto_FL.py`, `figure_3_RR_animation.py`, etc; run these scripts to generate the corresponding
figures in the main text. Note there is no script for figure 4 of the main text or the figures in the appendix as they are static.

If you want to run the code you'll need to excetute the following:
1) Download the remote_refocus repository, unzip and place the contents into a new directory named 'master'
2) Download the original 'big_data_input' folder from zenodo (17.5GB) DOI: and unzip (27.3GB)
3) Create a new directory and add 'master' and 'big_data_input' to the folder
4) Create a Python 3 environment with the associated subpackages [Numpy](http://www.numpy.org/), [Scipy](https://www.scipy.org/), and
[Matplotlib](http://matplotlib.org/). [Anaconda](https://www.continuum.io/downloads) satisfies these requirements with a single
installation.
5) Install [ImageMagick](https://www.imagemagick.org/script/index.php) and [ffmpeg](https://ffmpeg.org/) or equivalent software to make
the '.gif' or '.mp4' animations.
6) Now run the scripts from the 'figure_generation' folder to generate the desired figure. The scipts will generate temporary data in the
'temp' folder (which can be deleted afterwards) and the figures from the manuscript in the 'big_data_output' folder.

Note that `np_tif.py` and `stack_registration.py` are utility scripts that the other scripts depend on; do not run these scripts
individually.
