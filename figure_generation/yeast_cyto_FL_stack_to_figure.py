import os
import subprocess as sp
from shutil import copyfile
import numpy as np
import matplotlib.pyplot as plt
import np_tif
import stack_registration as sr

## Set/create directories
input_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'big_data_input', 'Yeast cyto FL'))
temp_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'temp'))
if not os.path.isdir(temp_directory): os.mkdir(temp_directory)
temp_directory = os.path.join(temp_directory, 'Yeast cyto FL')
if not os.path.isdir(temp_directory): os.mkdir(temp_directory)
output_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'big_data_output'))
if not os.path.isdir(output_directory): os.mkdir(output_directory)
output_directory = os.path.join(output_directory, 'Yeast cyto FL')
if not os.path.isdir(output_directory): os.mkdir(output_directory)

## Set input file name and acquisition parameters for processing
input_filename = (
    'Yeast cyto FL - spx_cyan_600_vol_20um_stk_5um_step_2ms_exp '
    'FL only hd 100 volumes.tif')
re_ordered_filename = os.path.splitext(input_filename)[0] + '_re_ordered.tif'
input_filename = os.path.join(input_directory, input_filename)
re_ordered_filename = os.path.join(temp_directory, re_ordered_filename)
num_slices = 5 # Number of z stack slices
num_tps = 600 # Number of volumes or time points in series
left_crop = 50
right_crop = 100
top_crop = 1
bottom_crop = 1

## If re-ordered file exists then skip re-ordering and cropping
if os.path.exists(re_ordered_filename):
    print('Found re-ordered tif, loading...', end='', sep='')
    data = np_tif.tif_to_array(re_ordered_filename)
    data = data.reshape((num_tps, num_slices) + data.shape[-2:])
    print('done')
    print('tif shape (t, z, y, z) =', data.shape)
## If no registered file is found then process original data file
else:
    print('Loading tif...', end='', sep='')
    data = np_tif.tif_to_array(input_filename)
    data = data.reshape((num_tps, num_slices) + data.shape[-2:])
    print('done')
    print('tif shape (t, z, y, z) =', data.shape)
    # Since our volumes were taken bidirectionally we also need to fix
    # the order.
    print('Re-ordering...', end='', sep='')
    for which_t in range(num_tps):
        # Flip every other volume in the Z-direction
        if which_t % 2 == 0:
            data[which_t, :, :, :] = data[which_t, ::-1, :, :]
    print('done')
    # Crop image for best aspect ratio
    print('Cropping...', end='', sep='')
    data = data[:, :, top_crop:-bottom_crop, left_crop:-right_crop]
    print('done')
    print("Saving result...", end='')
    np_tif.array_to_tif(
        data.reshape(num_tps*num_slices, data.shape[-2], data.shape[-1]),
        re_ordered_filename, slices=num_slices, channels=1, frames=num_tps)
    print('done')
    print('tif shape (t, z, y, z) =', data.shape)

## Choose parameters for video
current_frame = -1
xmargin = 0.105
ymargin = 0.2375
plot_space = 0.08
txt_space = 0.015
t = num_tps - 1 # set initial t to reject noisy frame

## Set output folder and filename for images to make video
output_filename = os.path.join(temp_directory, 'img%06i.png')

## Define normalisation function for RGB conversion
data_max = data.max()
def norm(x):
        if data_max == x.min(): return np.zeros_like(x)
        return (x - x.min()) / (data_max - x.min())

## Make images for video
fig = plt.figure(figsize=(15, 15))
ax = 2*num_slices*[None]

## Make image series for each video
for t in range(num_tps):
    t_unit = 0.02
    z_cal = 1.66666
    time = 0.5*(t_unit*t - t_unit)
    print('time', time)
    if t % 2 != 0:
        for z in range(num_slices):
            print('slice', 2*z+1)
            ax[2*z+1] = plt.axes([0.1, 0.04*(2*z+1), 0.5, 0.5])
            rgb = np.zeros(data[t, z, :, :].shape + (3,))
            rgb[:, :, 1] = 1.0*norm(data[t, z, :, :])
            if z == 4:
                scale_bar = rgb[ :, :, :]
                scale_bar[30:40, 1695:1880] = 1
            ax[2*z+1].imshow(rgb)
            plt.setp(ax[2*z+1].get_xticklabels(), visible=False)
            plt.setp(ax[2*z+1].get_yticklabels(), visible=False)
            plt.setp(ax[2*z+1].get_xticklines(), visible=False)
            plt.setp(ax[2*z+1].get_yticklines(), visible=False)
            fig.text(xmargin, ymargin + txt_space + (0.5 + z)*plot_space,
                     'z=%6s$\mu$m'%('%0.2f'%((2*z+1)*z_cal)),
                        color='yellow', family='monospace')
            fig.text(xmargin, ymargin + 0.5*plot_space + plot_space*z,
                     't=%6ss'%('%0.3f'%(time + z*t_unit/(2*num_slices))),
                        color='yellow', family='monospace')
    else:
        for z in range(num_slices):
            print('slice', 2*z)
            ax[2*z] = plt.axes([0.1, 0.04*(2*z), 0.5, 0.5])
            rgb = np.zeros(data[t, z, :, :].shape + (3,))
            rgb[:, :, 1] = 1.0*norm(data[t, z, :, :])
            ax[2*z].imshow(rgb)
            plt.setp(ax[2*z].get_xticklabels(), visible=False)
            plt.setp(ax[2*z].get_yticklabels(), visible=False)
            plt.setp(ax[2*z].get_xticklines(), visible=False)
            plt.setp(ax[2*z].get_yticklines(), visible=False)
            if t > 1:
                fig.text(xmargin, ymargin + txt_space + plot_space*z,
                     'z=%6s$\mu$m'%('%0.2f'%(2*z*z_cal)),
                        color='yellow', family='monospace')
                fig.text(xmargin, ymargin + plot_space*z,
                         't=%6ss'%('%0.3f'%(time +
                                            z*t_unit/(2*num_slices))),
                        color='yellow', family='monospace')
    if t > 1:
        if t % 2 == 0:
            current_frame += 1
            print('saving')
            plt.savefig(output_filename%current_frame, bbox_inches='tight')
            plt.clf()
plt.close(fig)

## Choose 'poster' image and copy to video location
copyfile(os.path.join(temp_directory, 'img000000.png'),
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
    os.getcwd(), os.pardir, os.pardir, 'master', 'images', 'Yeast cyto FL'))
if not os.path.isdir(image_directory): os.mkdir(image_directory)
copyfile(os.path.join(output_directory, 'figure.mp4'),
         os.path.join(image_directory, 'figure.mp4'))
copyfile(os.path.join(output_directory, 'poster.png'),
         os.path.join(image_directory, 'poster.png'))
