#!/usr/bin/env python3
# Dependencies from the Python 3 standard library:
import os
import subprocess as sp
from shutil import copyfile
# Dependencies from the Scipy stack https://www.scipy.org/stackspec.html :
import numpy as np
import matplotlib.pyplot as plt
# Dependencies from https://github.com/AndrewGYork/remote_refocus/figure_generation :
import np_tif

## Set/create directories
input_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'big_data_input', 'SIM_3D_projected'))
temp_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'temp'))
if not os.path.isdir(temp_directory): os.mkdir(temp_directory)
temp_directory = os.path.join(temp_directory, 'SIM_3D_projected')
if not os.path.isdir(temp_directory): os.mkdir(temp_directory)
output_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'big_data_output'))
if not os.path.isdir(output_directory): os.mkdir(output_directory)
output_directory = os.path.join(output_directory, 'SIM_3D_projected')
if not os.path.isdir(output_directory): os.mkdir(output_directory)

## Set input file name and acquisition parameters for processing
num_angles = 120 # number of rotation angles in stack
input_filename = ('SpXcyan-dmi8GFPcube_dmi8z_0.0_+-25um_in_0.5um_steps_'
                  'cropped_3DP_4.6pix,360deg,3deg_steps,intp.tif')
input_filename = os.path.join(input_directory, input_filename)

## If file exists then load
if os.path.exists(input_filename):
    print('Found tif, loading...', end='')
    data = np_tif.tif_to_array(input_filename)
    data = data.reshape((num_angles,) + data.shape[-2:])
    print('done')
    print('tif shape (theta, y, x) =', data.shape)

## If no file exists then
else:
    print('No tif found')

## Add white scale bar to all images
for t in range(data.shape[0]):
    image = data[t, :, :]
    image[30:40, 550:735] = image.max()

## Choose parameters for video
current_frame = -1
xmargin = 0.15
ymargin = 0.25

## Set output folder for images to make video
output_filename = os.path.join(temp_directory, 'img%06i.png')

## Make images for video
fig = plt.figure(figsize=(7.5,7.5),dpi=(600))
for z in range(num_angles):
    plt.clf()
    angle = 3*z
    current_frame += 1
    print('frame = ', current_frame)
    plt.imshow(data[z, :, :], cmap='gray', vmin=50, vmax=200)
    plt.gca().get_xaxis().set_ticks([])
    plt.gca().get_yaxis().set_ticks([])
    plt.figtext(xmargin, ymargin, 'array=(40$\mu$m)\u00b3, '
                'rotation=%3sdeg'%('%0.0f'%angle),
                color='yellow', family='monospace')
    plt.savefig(output_filename%current_frame, bbox_inches='tight')
plt.close(fig)

## Choose 'poster' image and copy to video location
copyfile(os.path.join(temp_directory, 'img000004.png'),
         os.path.join(output_directory, 'poster.png'))

## Make video from images
print("Converting images to mp4...", end='')
convert_command = [
   'ffmpeg', '-y',              # auto overwrite files
   '-r', '10',                  # frame rate
   '-f', 'image2',              # format is image sequence
   '-i', os.path.join(temp_directory,
                      'img%06d.png'),  # image sequence name
   '-movflags', 'faststart',    # internet optimisation...(?)
   '-pix_fmt', 'yuv420p',       # cross browser compatibility
   '-vcodec', 'libx264',        # codec choice
   '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',  # even pixel number (important)
   '-preset', 'veryslow',       # take time and compress to max
   '-crf', '25',                # image quality vs file size
   os.path.join(output_directory, 'figure.mp4')]  # output file name
try:
   with open('conversion_messages.txt', 'wt') as f:
       f.write("So far, everthing's fine...\n")
       f.flush()
       sp.check_call(convert_command, stderr=f, stdout=f)
       f.flush()
   os.remove('conversion_messages.txt')
except: # This is unlikely to be platform independent :D
   print("MP4 conversion failed. Is ffmpeg installed?")
   raise
print('"figure.mp4" created')
print('done.')

## This is a default figure so copy to 'images' in 'master' directory
image_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'master', 'images', 'SIM_3D_projected'))
if not os.path.isdir(image_directory): os.mkdir(image_directory)
copyfile(os.path.join(output_directory, 'figure.mp4'),
         os.path.join(image_directory, 'figure.mp4'))
copyfile(os.path.join(output_directory, 'poster.png'),
         os.path.join(image_directory, 'poster.png'))

## Also copy files that detail ImageJ processing from input directory to
## output directory and images directory
copyfile(os.path.join(input_directory, '3D_project_parameters.txt'),
         os.path.join(output_directory, '3D_project_parameters.txt'))
copyfile(os.path.join(output_directory, '3D_project_parameters.txt'),
         os.path.join(image_directory, '3D_project_parameters.txt'))
copyfile(os.path.join(input_directory, '3D_project_step_1.png'),
         os.path.join(output_directory, '3D_project_step_1.png'))
copyfile(os.path.join(output_directory, '3D_project_step_1.png'),
         os.path.join(image_directory, '3D_project_step_1.png'))
copyfile(os.path.join(input_directory, '3D_project_step_2.png'),
         os.path.join(output_directory, '3D_project_step_2.png'))
copyfile(os.path.join(output_directory, '3D_project_step_2.png'),
         os.path.join(image_directory, '3D_project_step_2.png'))
