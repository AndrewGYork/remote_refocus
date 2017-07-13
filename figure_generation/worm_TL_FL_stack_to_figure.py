import os
import subprocess as sp
from shutil import copyfile
import numpy as np
import matplotlib.pyplot as plt
import np_tif

## Set/create directories
input_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'big_data_input', 'Worm TL FL'))
temp_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'temp'))
if not os.path.isdir(temp_directory): os.mkdir(temp_directory)
temp_directory = os.path.join(temp_directory, 'Worm TL FL')
if not os.path.isdir(temp_directory): os.mkdir(temp_directory)
output_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'big_data_output'))
if not os.path.isdir(output_directory): os.mkdir(output_directory)
output_directory = os.path.join(output_directory, 'Worm TL FL')
if not os.path.isdir(output_directory): os.mkdir(output_directory)

## Set input file name and acquisition parameters for processing
input_filename = (
    'Worm TL FL - spx_cyan_100_vol_10um_stk_1um_step_5ms_exp good-015.tif')
re_ordered_filename = os.path.splitext(input_filename)[0] + '_re_ordered.tif'
input_filename = os.path.join(input_directory, input_filename)
re_ordered_filename = os.path.join(temp_directory, re_ordered_filename)
num_channels = 2 # Number of colors
num_slices = 11 # Number of z stack slices
num_tps = 100 # Number of volumes or time points in series

## If re-ordered file exists then skip re-ordering and cropping
if os.path.exists(re_ordered_filename):
    print('Found re-ordered tif, loading...', end='', sep='')
    data = np_tif.tif_to_array(re_ordered_filename)
    data = data.reshape((num_tps, num_slices, num_channels) + data.shape[-2:])
    print('done')
    print('tif shape (t, z, c, y, x) =', data.shape)
## If no registered file is found then process original data file
else:
    print('Loading tif...', end='', sep='')
    data = np_tif.tif_to_array(input_filename)
    data = data.reshape((num_tps, num_slices, num_channels) + data.shape[-2:])
    print('done')
    print('tif shape (t, z, c, y, x) =', data.shape)
    # Since our volumes were taken bidirectionally we also need to fix
    # the order.
    print('Re-ordering...', end='', sep='')
    for which_t in range(num_tps):
        # Flip every other volume in the Z-direction
        if which_t % 2 == 0:
            data[which_t, :, :, :, :] = data[which_t, ::-1, :, :, :]
    print('done')
    print("Saving result...", end='')
    np_tif.array_to_tif(
        data.reshape(num_tps*num_channels*num_slices, data.shape[-2],
                     data.shape[-1]), re_ordered_filename,
                     slices=num_slices, channels=num_channels, frames=num_tps)
    print('done')
    print('tif shape (t, z, c, y, x) =', data.shape)

## Choose parameters for video
num_z_stack = 3
pause = 25
z_slow_down_factor = 5
z_scale = 1
current_frame = -1
current_tp = -1
xmargin = 0.3
ymargin = 0.775
space = 0.03
min_int = 1000
max_int = 40000

## Set output folder and filename for images to make video
output_filename = os.path.join(temp_directory, 'img%06i.png')

## Define normalisation function for RGB conversion
data0_max = 12500
def norm0(x):
        if data0_max == x.min(): return np.zeros_like(x)
        return (x - x.min()) / (data0_max - x.min())
data1_max = 4000
def norm1(x):
        if data1_max == x.min(): return np.zeros_like(x)
        return (x - x.min()) / (data1_max - x.min())

## Make images for video
for n in range(num_z_stack):
    fig = plt.figure()
    z = int(num_slices/2)
    for t in range(current_tp +1 , current_tp + 1 + int(num_tps/num_z_stack)):
        plt.clf()
        current_frame += 1
        current_tp += 1
        time = 0.01*current_tp
        print('time = ', time)
        rgb0 = np.zeros(data[t, z, 0, :, :].shape + (3,))
        rgb1 = np.zeros(data[t, z, 1, :, :].shape + (3,))
        rgb0[:, :, :] = norm0(data[t, z, 0, :, :]).reshape(data.shape[-2], data.shape[-1], 1)
        rgb1[:, :, 1] = norm1(data[t, z, 1, :, :])
        overlay = np.clip(rgb0 + rgb1, 0, 1)
        plt.imshow(overlay)
        plt.gca().get_xaxis().set_ticks([])
        plt.gca().get_yaxis().set_ticks([])
        plt.figtext(xmargin, ymargin + 3*space,
                    'Every time point is a 3D volume',
                    color='white', family='monospace')
        plt.figtext(xmargin, ymargin + 2*space, 't=%6ss'%('%0.2f'%time),
                    color='white', family='monospace')
        plt.figtext(xmargin, ymargin + space,
                    'z=%6s$\mu$m'%('%0.2f'%(z_scale*z)),
                    color='white', family='monospace')
        plt.savefig(output_filename%current_frame, bbox_inches='tight')
    for copy in range(pause):
        copyfile(output_filename%current_frame,
                 output_filename%(current_frame + 1))
        current_frame += 1
    for z in range(int(num_slices/2), num_slices - 1, 1):        
        plt.clf()
        current_frame += 1
        print('current z', z)
        rgb0 = np.zeros(data[t, z, 0, :, :].shape + (3,))
        rgb1 = np.zeros(data[t, z, 1, :, :].shape + (3,))
        rgb0[:, :, :] = norm0(data[t, z, 0, :, :]).reshape(data.shape[-2], data.shape[-1], 1)
        rgb1[:, :, 1] = norm1(data[t, z, 1, :, :])
        overlay = np.clip(rgb0 + rgb1, 0, 1)
        plt.imshow(overlay)
        plt.gca().get_xaxis().set_ticks([])
        plt.gca().get_yaxis().set_ticks([])
        plt.figtext(xmargin, ymargin + 3*space,
                    'Every time point is a 3D volume',
                    color='white', family='monospace')
        plt.figtext(xmargin, ymargin + 2*space, 't=%6ss'%('%0.2f'%time),
                    color='white', family='monospace')
        plt.figtext(xmargin, ymargin + space,
                    'z=%6s$\mu$m 10 volumes/s!'%('%0.2f'%(z_scale*z)),
                    color='yellow', family='monospace')
        plt.savefig(output_filename%current_frame, bbox_inches='tight')
        for r in range(z_slow_down_factor):
            copyfile(output_filename%current_frame,
                 output_filename%(current_frame + 1))
            current_frame += 1
    for z in range(num_slices - 1, 0, -1):
        plt.clf()
        current_frame += 1
        print('current z', z)
        rgb0 = np.zeros(data[t, z, 0, :, :].shape + (3,))
        rgb1 = np.zeros(data[t, z, 1, :, :].shape + (3,))
        rgb0[:, :, :] = norm0(data[t, z, 0, :, :]).reshape(data.shape[-2], data.shape[-1], 1)
        rgb1[:, :, 1] = norm1(data[t, z, 1, :, :])
        overlay = np.clip(rgb0 + rgb1, 0, 1)
        plt.imshow(overlay)
        plt.gca().get_xaxis().set_ticks([])
        plt.gca().get_yaxis().set_ticks([])
        plt.figtext(xmargin, ymargin + 3*space,
                    'Every time point is a 3D volume',
                    color='white', family='monospace')
        plt.figtext(xmargin, ymargin + 2*space, 't=%6ss'%('%0.2f'%time),
                    color='white', family='monospace')
        plt.figtext(xmargin, ymargin + space,
                    'z=%6s$\mu$m 10 volumes/s!'%('%0.2f'%(z_scale*z)),
                    color='yellow', family='monospace')
        plt.savefig(output_filename%current_frame, bbox_inches='tight')
        for r in range(z_slow_down_factor):
            copyfile(output_filename%current_frame,
                 output_filename%(current_frame + 1))
            current_frame += 1
    for z in range(0, int(num_slices/2) + 1, 1):
        plt.clf()
        current_frame += 1
        print('current z', z)
        rgb0 = np.zeros(data[t, z, 0, :, :].shape + (3,))
        rgb1 = np.zeros(data[t, z, 1, :, :].shape + (3,))
        rgb0[:, :, :] = norm0(data[t, z, 0, :, :]).reshape(data.shape[-2], data.shape[-1], 1)
        rgb1[:, :, 1] = norm1(data[t, z, 1, :, :])
        overlay = np.clip(rgb0 + rgb1, 0, 1)
        plt.imshow(overlay)
        plt.gca().get_xaxis().set_ticks([])
        plt.gca().get_yaxis().set_ticks([])
        plt.figtext(xmargin, ymargin + 3*space,
                    'Every time point is a 3D volume',
                    color='white', family='monospace')
        plt.figtext(xmargin, ymargin + 2*space, 't=%6ss'%('%0.2f'%time),
                    color='white', family='monospace')
        plt.figtext(xmargin, ymargin + space,
                    'z=%6s$\mu$m 10 volumes/s!'%('%0.2f'%(z_scale*z)),
                    color='yellow', family='monospace')
        plt.savefig(output_filename%current_frame, bbox_inches='tight')
        for r in range(z_slow_down_factor):
            copyfile(output_filename%current_frame,
                 output_filename%(current_frame + 1))
            current_frame += 1
    for copy in range(pause):
        copyfile(output_filename%current_frame,
                 output_filename%(current_frame + 1))
        current_frame += 1
    plt.close(fig)

## Choose 'poster' image and copy to video location
copyfile(os.path.join(temp_directory, 'img000058.png'),
         os.path.join(output_directory, 'poster.png'))

## Make video from images
print("Converting images to mp4...", end='')
convert_command = [
   'ffmpeg', '-y',              # auto overwrite files
   '-r', '45',                  # frame rate
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
