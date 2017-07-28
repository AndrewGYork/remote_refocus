import os
import subprocess as sp
from shutil import copyfile
import numpy as np
import matplotlib.pyplot as plt
import np_tif

## Set/create directories
input_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'big_data_input', 'SIM_lines_center'))
temp_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'temp'))
if not os.path.isdir(temp_directory): os.mkdir(temp_directory)
temp_directory = os.path.join(temp_directory, 'SIM_lines_center')
if not os.path.isdir(temp_directory): os.mkdir(temp_directory)
output_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'big_data_output'))
if not os.path.isdir(output_directory): os.mkdir(output_directory)
output_directory = os.path.join(output_directory, 'SIM_lines_center')
if not os.path.isdir(output_directory): os.mkdir(output_directory)

## Set input file name and acquisition parameters for processing
mz_step = 5 # microscope z step
num_f = 13 # number of files
num_slices = 17 # number of z slices in a stack
input_filename = ('SpXcyan-dmi8GFPcube_dmi8z_%1s.0.tif')
input_filename_list = num_f*[None]
hyperstack_filename = os.path.splitext(input_filename)[0] + '_hyperstack.tif'
input_filename = os.path.join(input_directory, input_filename)
hyperstack_filename = os.path.join(temp_directory, hyperstack_filename)

## Cropping parameters
left_crop = 725
right_crop = 775
top_crop = 790
bottom_crop = 710

## If hyperstack file exists then skip processing
if os.path.exists(hyperstack_filename):
    print('Found hyperstack tif, loading...', end='')
    data = np_tif.tif_to_array(hyperstack_filename)
    data = data.reshape((num_f, num_slices) + data.shape[-2:])
    print('done')

## If no hyperstack file then process original data
else:
    data_list = num_f*[None]
    for fn in range(num_f):
        input_filename_list[fn] = (input_filename
                                   %((fn-int(0.5*(num_f-1)))*mz_step))
        print('Found input files, loading...', end='')
        data_list[fn] = np_tif.tif_to_array(input_filename_list[fn])
        print('done')
    print('Creating np data array...', end='')
    data = np.asarray(data_list)
    data = data.reshape((num_f, num_slices) + data.shape[-2:])        
    print('done')
    print('Cropping...', end='', sep='')
    if left_crop or right_crop > 0:
        data = data[:, :, :, left_crop:-right_crop]
    if top_crop or bottom_crop > 0:
        data = data[:, :, top_crop:-bottom_crop, :]
    print('done')
    print("Saving result...", end='')
    np_tif.array_to_tif(
        data.reshape(num_f*num_slices, data.shape[-2], data.shape[-1]),
        hyperstack_filename, slices=num_slices, channels=1, frames=num_f)
    print('done')

print('tif shape (Microsope z, RR z, y, x) =', data.shape)

## Add white scale bar to all images
for t in range(data.shape[0]):
    for z in range(data.shape[1]):
        image = data[t, z, :, :]
        image[20:30, 350:535] = 3000

## Choose parameters for video
current_frame = -1
xmargin = 0.15
ymargin = 0.16
space = 0.03
z_scale = 0.25

## Set output folder and filename for images to make video
output_filename = os.path.join(output_directory, 'img%02i%02i.png')

## Make images for video
fig = plt.figure(figsize=(10,10),dpi=(600))
for fn in range(num_f):
    mz = (fn-int(0.5*(num_f-1)))*mz_step
    print('Microscope z = ', mz)
    for z in range(num_slices):
        rrz = 1.52*mz + z_scale*(z-(num_slices-1)/2)
        current_frame += 1
        print('frame = ', current_frame)
        plt.clf()
        print('RR z = ', rrz)
        plt.imshow(data[fn, z, :, :], cmap='gray', vmin=750, vmax=3000)
        plt.gca().get_xaxis().set_ticks([])
        plt.gca().get_yaxis().set_ticks([])
        plt.figtext(xmargin, ymargin + 22*space,
                    'Diffraction limited resolution',
                    color='yellow', family='monospace')
        plt.figtext(xmargin, ymargin + 2*space, 'RR z=%6s$\mu$m'%('%0.2f'%rrz),
                    color='yellow', family='monospace')
        plt.figtext(xmargin, ymargin + space, 'Microscope z=%6s$\mu$m'%('%0.2f'%mz),
                    color='yellow', family='monospace')
        plt.figtext(xmargin, ymargin, 'Field of view = centre',
                        color='yellow', family='monospace')
        plt.savefig(output_filename%(fn, z), bbox_inches='tight')
plt.close(fig)

## Choose 'poster' image and copy to video location
copyfile(os.path.join(output_directory, 'img0608.png'),
         os.path.join(output_directory, 'default.png'))

## This is a default figure so copy to 'images' in 'master' directory
image_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'master', 'images', 'SIM_lines_center'))
if not os.path.isdir(image_directory): os.mkdir(image_directory)
copyfile(os.path.join(output_directory, 'default.png'),
         os.path.join(image_directory, 'default.png'))
