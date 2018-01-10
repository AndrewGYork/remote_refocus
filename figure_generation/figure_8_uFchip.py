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
    os.getcwd(), os.pardir, os.pardir, 'big_data_input', 'uFchip'))
temp_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'temp'))
if not os.path.isdir(temp_directory): os.mkdir(temp_directory)
temp_directory = os.path.join(temp_directory, 'uFchip')
if not os.path.isdir(temp_directory): os.mkdir(temp_directory)
output_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'big_data_output'))
if not os.path.isdir(output_directory): os.mkdir(output_directory)
output_directory = os.path.join(output_directory, 'uFchip')
if not os.path.isdir(output_directory): os.mkdir(output_directory)

## Set input file name and acquisition parameters for processing
input_filename = ('transmitted_z_step_10_uF2.tif')
cropped_filename = os.path.splitext(input_filename)[0] + '_cropped.tif'
input_filename = os.path.join(input_directory, input_filename)
cropped_filename = os.path.join(temp_directory, cropped_filename)
num_tps = 1000 # Number of time points in series
left_crop = 400
right_crop = 750
top_crop = 0
bottom_crop = 0

## If cropped file exists then load
if os.path.exists(cropped_filename):
    print('Found cropped tif, loading...', end='', sep='')
    data = np_tif.tif_to_array(cropped_filename)
    print('done')
    print('tif shape (t, y, x) =', data.shape)

## If no file found then load original and crop
else:
    print('Loading original file...', end='', sep='')
    data = np_tif.tif_to_array(input_filename)
    print('done')
    data = data.reshape((num_tps,) + data.shape[-2:])
    print('tif shape (t, y, x) =', data.shape)
    print('Cropping...', end='', sep='')
    if left_crop or right_crop > 0:
        data = data[:, :, left_crop:-right_crop]
    if top_crop or bottom_crop > 0:
        data = data[:, top_crop:-bottom_crop, :]
    print('done')
    print("Saving result...", end='', sep='')
    np_tif.array_to_tif(
        data.reshape(num_tps, data.shape[-2], data.shape[-1]),
        cropped_filename, slices=1, channels=1, frames=num_tps)
    print('done')
    print('tif shape (t, y, x) =', data.shape)

## Choose parameters for video
current_frame = -1
xmargin = 0.01
ymargin = 0.025
space = 0.175
img_size = 0.5
max_intensity = 12500
wlw = 2 # white line width half amplitude
start_tp = 0 # removing uneventful begging
stop_tp = 100 # remove uneventful end
xslice = 86 # choose slice along x for display

## Set output folder for images to make video
output_filename = os.path.join(temp_directory, 'img%06i.png')

## Make images for video
fig = plt.figure()
for t in range(wlw + start_tp, num_tps - wlw - stop_tp):
    plt.clf()
    current_frame += 1
    time = 0.001*t - 0.002 - 0.001*start_tp
    print('time = ', time)
    ax1 = plt.axes([0, 0.575, img_size, img_size])
    ax1_data = data[t, :, :]
    ax1.imshow(ax1_data, cmap='gray', vmin=0, vmax=max_intensity)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax1.get_yticklabels(), visible=False)
    plt.setp(ax1.get_xticklines(), visible=False)
    plt.setp(ax1.get_yticklines(), visible=False)
    ax2 = plt.axes([0, 0, img_size, 1.5*img_size])
    ax2_data = np.zeros((data.shape[0], data.shape[2], 3)) # RGB
    make_me_rgb = data[:, xslice, :].reshape(data.shape[0], data.shape[2], 1)
    make_me_rgb = np.clip(make_me_rgb/max_intensity, 0, 1) # Normalize to 0, 1
    ax2_data[:, :, :] = make_me_rgb # Broadcast across all three color channels
    white_line = ax2_data[t-wlw:t+wlw, :, :]
    yellow = np.array([1, 1, 0])
    white_line[0, :, :] = 0.5*yellow # Woo, broadcasting.
    white_line[1, :, :] = 1.0*yellow
    white_line[2, :, :] = 1.0*yellow
    white_line[3, :, :] = 0.5*yellow
    ax2.imshow(ax2_data)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.setp(ax2.get_yticklabels(), visible=False)
    plt.setp(ax2.get_xticklines(), visible=False)
    plt.setp(ax2.get_yticklines(), visible=False)
    if 50 < t < 275: 
        plt.figtext(xmargin, ymargin + 3.9*space, 'Microscope',
                    color='yellow', family='monospace')
    else:
        plt.figtext(xmargin, ymargin + 3.9*space, 'Microscope',
                    color='white', family='monospace')
    if 475 < t < 625: 
        plt.figtext(xmargin, ymargin + 2*space, 'Stage',
                    color='yellow', family='monospace')
    else:
        plt.figtext(xmargin, ymargin + 2*space, 'Stage',
                    color='white', family='monospace')
    if 725 < t < 800: 
        plt.figtext(xmargin, ymargin + space, 'Remote',
                    color='yellow', family='monospace')
    else:
        plt.figtext(xmargin, ymargin + space, 'Remote',
                    color='white', family='monospace')
    plt.figtext(xmargin, ymargin, 't=%6ss'%('%0.3f'%time),
                color='yellow', family='monospace')
    plt.savefig(output_filename%current_frame, bbox_inches='tight')
plt.close(fig)

## Choose 'poster' image and copy to video location
copyfile(os.path.join(temp_directory, 'img000250.png'),
         os.path.join(output_directory, 'poster.png'))

## Make video from images
print("Converting images to mp4...", end='')
convert_command = [
   'ffmpeg', '-y',              # auto overwrite files
   '-r', '50',                  # frame rate
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
    os.getcwd(), os.pardir, os.pardir, 'master', 'images', 'uFchip'))
if not os.path.isdir(image_directory): os.mkdir(image_directory)
copyfile(os.path.join(output_directory, 'figure.mp4'),
         os.path.join(image_directory, 'figure.mp4'))
copyfile(os.path.join(output_directory, 'poster.png'),
         os.path.join(image_directory, 'poster.png'))
