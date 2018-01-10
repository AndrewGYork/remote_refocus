#!/usr/bin/env python3
# Dependencies from the Python 3 standard library:
import os
import subprocess as sp
from shutil import copyfile
# Dependencies from the Scipy stack https://www.scipy.org/stackspec.html:
import numpy as np
import matplotlib.pyplot as plt
# Dependencies from https://github.com/AndrewGYork/tools:
import np_tif
import stack_registration as sr

## Set/create directories
input_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'big_data_input', 'Worm_DIC'))
temp_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'temp'))
if not os.path.isdir(temp_directory): os.mkdir(temp_directory)
temp_directory = os.path.join(temp_directory, 'Worm_DIC')
if not os.path.isdir(temp_directory): os.mkdir(temp_directory)
output_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'big_data_output'))
if not os.path.isdir(output_directory): os.mkdir(output_directory)
output_directory = os.path.join(output_directory, 'Worm_DIC')
if not os.path.isdir(output_directory): os.mkdir(output_directory)

## Set input file name and acquisition parameters for processing
input_filename = (
    'Worm_DIC-spx_cyan_200_vol_10um_stk_1um_step_5ms_exp_DIC2-014.tif')
registered_filename = os.path.splitext(input_filename)[0] + '_registered.tif'
input_filename = os.path.join(input_directory, input_filename)
registered_filename = os.path.join(temp_directory, registered_filename)
num_slices = 11 # Number of z stack slices
num_tps = 200 # Number of volumes or time points in series
border = 10 # Number of pixels to crop around image after registration

## If registerd file exists then skip registration and cropping
if os.path.exists(os.path.join(temp_directory, registered_filename)):
    print('Found registered tif, loading...')
    data = np_tif.tif_to_array(registered_filename)
    data = data.reshape((num_tps, num_slices) + data.shape[-2:])
    print('done')
    print('tif shape (t, z, y, z) =', data.shape)
## If no registered file is found then process original data file
else:
    print('Loading tif...')
    data = np_tif.tif_to_array(input_filename)
    data = data.reshape((num_tps, num_slices) + data.shape[-2:])
    print('done')
    print('tif shape (t, z, y, z) =', data.shape)
    # Register data
    # Since our volumes were taken bidirectionally we also need to fix
    # the order.
    print('Registering...', end='', sep='')
    for which_t in range(num_tps):
        # Flip every other volume in the Z-direction
        if which_t % 2 == 0:
            data[which_t, :, :, :] = data[which_t, ::-1, :, :]
    # XY-Register a time-averaged version of the stack
    registration_shifts = sr.mr_stacky(
        data.sum(axis=0),
        align_to_this_slice=5,
        register_in_place=False,
        fourier_cutoff_radius=0.05)
    for which_t in range(num_tps):
        # Apply the time-averaged registration shifts to each time point:
        print('.', end='', sep='')
        sr.apply_registration_shifts(
            data[which_t, :, :, :], registration_shifts)
    print('done')
    # Registraction will often leave black borders so it's best to crop
    # at the end to tidy up.
    print('Cropping...')
    left_crop = border
    right_crop = border
    top_crop = border
    bottom_crop = border
    data = data[:, :, top_crop:-bottom_crop, left_crop:-right_crop]
    print('done')
    print("Saving result...", end='')
    np_tif.array_to_tif(
        data.reshape(num_tps*num_slices, data.shape[-2], data.shape[-1]),
        registered_filename, slices=num_slices, channels=1, frames=num_tps)
    print('done')
    print('tif shape (t, z, y, x) =', data.shape)

## Add white scale bar to all images
for t in range(data.shape[0]):
    for z in range(data.shape[1]):
        image = data[t, z, :, :]
        image[30:40, 635:820] = 2500

## Choose parameters for video
num_z_stack = 4
pause = 25
z_slow_down_factor = 5
current_frame = -1
current_tp = -1
xmargin = 0.25
ymargin = 0.775
space = 0.03
t = num_tps - 1 # set initial t to reject noisy frame

## Set output folder and filename for images to make video
output_filename = os.path.join(temp_directory, 'img%06i.png')

## Make images for video
fig = plt.figure()
for n in range(num_z_stack):
    z = int(num_slices/2)
    for t in range(num_tps - current_tp - 2,
                   num_tps - current_tp - 2 - int(num_tps/num_z_stack),
                   -1):
        if t < 1: break # ditch noisy first frame
        plt.clf()
        current_frame += 1
        current_tp += 1
        time = -0.05 * (t - num_tps)
        print('time', time)
        plt.imshow(data[t, z, :, :], cmap='gray', vmin=0, vmax=2500)
        plt.gca().get_xaxis().set_ticks([])
        plt.gca().get_yaxis().set_ticks([])
        plt.figtext(xmargin, ymargin + 3*space,
                    '20 volumes/s',
                    color='white', family='monospace')
        plt.figtext(xmargin, ymargin + 2*space, 't=%6ss'%('%0.1f'%time),
                    color='white', family='monospace')
        plt.figtext(xmargin, ymargin + space, 'z=%6s$\mu$m'%('%0.1f'%z),
                    color='white', family='monospace')
        plt.savefig(output_filename%current_frame, bbox_inches='tight')
    for copy in range(pause):
        copyfile(output_filename%current_frame,
                 output_filename%(current_frame + 1))
        current_frame += 1
    for z in range(int(num_slices/2), num_slices - 1, 1):        
        if t < 1: t = 1 # ditch noisy first frame
        plt.clf()
        current_frame += 1
        print('current z', z)
        plt.imshow(data[t, z, :, :], cmap='gray', vmin=0, vmax=2500)
        plt.gca().get_xaxis().set_ticks([])
        plt.gca().get_yaxis().set_ticks([])
        plt.figtext(xmargin, ymargin + 3*space,
                    '20 volumes/s',
                    color='white', family='monospace')
        plt.figtext(xmargin, ymargin + 2*space, 't=%6ss'%('%0.1f'%time),
                    color='white', family='monospace')
        plt.figtext(xmargin, ymargin + space,
                    'z=%6s$\mu$m Every time point is a 3D volume'%('%0.1f'%z),
                    color='yellow', family='monospace')
        plt.savefig(output_filename%current_frame, bbox_inches='tight')
        for r in range(z_slow_down_factor):
            copyfile(output_filename%current_frame,
                 output_filename%(current_frame + 1))
            current_frame += 1
    for z in range(num_slices - 1, 0, -1):
        if t < 1: t = 1 # ditch noisy first frame
        plt.clf()
        current_frame += 1
        print('current z', z)
        plt.imshow(data[t, z, :, :], cmap='gray', vmin=0, vmax=2500)
        plt.gca().get_xaxis().set_ticks([])
        plt.gca().get_yaxis().set_ticks([])
        plt.figtext(xmargin, ymargin + 3*space,
                    '20 volumes/s',
                    color='white', family='monospace')
        plt.figtext(xmargin, ymargin + 2*space, 't=%6ss'%('%0.1f'%time),
                    color='white', family='monospace')
        plt.figtext(xmargin, ymargin + space,
                    'z=%6s$\mu$m Every time point is a 3D volume'%('%0.1f'%z),
                    color='yellow', family='monospace')
        plt.savefig(output_filename%current_frame, bbox_inches='tight')
        for r in range(z_slow_down_factor):
            copyfile(output_filename%current_frame,
                 output_filename%(current_frame + 1))
            current_frame += 1
    for z in range(0, int(num_slices/2) + 1, 1):
        if t < 1: t = 1 # ditch noisy first frame
        plt.clf()
        current_frame += 1
        print('current z', z)
        plt.imshow(data[t, z, :, :], cmap='gray', vmin=0, vmax=2500)
        plt.gca().get_xaxis().set_ticks([])
        plt.gca().get_yaxis().set_ticks([])
        plt.figtext(xmargin, ymargin + 3*space,
                    '20 volumes/s',
                    color='white', family='monospace')
        plt.figtext(xmargin, ymargin + 2*space, 't=%6ss'%('%0.1f'%time),
                    color='white', family='monospace')
        plt.figtext(xmargin, ymargin + space,
                    'z=%6s$\mu$m Every time point is a 3D volume'%('%0.1f'%z),
                    color='yellow', family='monospace')
        plt.savefig(output_filename%current_frame, bbox_inches='tight')
        for r in range(z_slow_down_factor):
            copyfile(output_filename%current_frame,
                 output_filename%(current_frame + 1))
            current_frame += 1
    for copy in range(pause):
        if t < 1: t = 1 # ditch noisy first frame
        copyfile(output_filename%current_frame,
                 output_filename%(current_frame + 1))
        current_frame += 1
    plt.close(fig)

## Choose 'poster' image and copy to video location
copyfile(os.path.join(temp_directory, 'img000877.png'),
         os.path.join(output_directory, 'poster.png'))

## Make video from images
print("Converting images to mp4...", end='')
convert_command = [
   'ffmpeg', '-y',              # auto overwrite files
   '-r', '60',                  # frame rate
   '-f', 'image2',              # format is image sequence
   '-i', os.path.join(temp_directory,
                      'img%06d.png'),  # image sequence name
   '-movflags', 'faststart',    # internet optimisation...(?)
   '-pix_fmt', 'yuv420p',       # cross browser compatibility
   '-vcodec', 'libx264',        # codec choice
   '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2', # even pixel number (important)
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
    os.getcwd(), os.pardir, os.pardir, 'master', 'images', 'Worm_DIC'))
if not os.path.isdir(image_directory): os.mkdir(image_directory)
copyfile(os.path.join(output_directory, 'figure.mp4'),
         os.path.join(image_directory, 'figure.mp4'))
copyfile(os.path.join(output_directory, 'poster.png'),
         os.path.join(image_directory, 'poster.png'))
