import os
from subprocess import check_call
from shutil import copyfile

## Set/create directories
input_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'big_data_input', 'RR_animation'))
output_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'big_data_output'))
if not os.path.isdir(output_directory): os.mkdir(output_directory)
output_directory = os.path.join(output_directory, 'RR_animation')
if not os.path.isdir(output_directory): os.mkdir(output_directory)

## Create movies
for name in ('fast', 'slow'):
    if name == 'slow':
        input_filenames = ['img%i.png'%i for i in range(9)]
        output_filename_gif = 'slow.gif'
        output_filename_mp4 = 'slow.mp4'
    elif name == 'fast':
        input_filenames = ['img%i.png'%i for i in range(9, 18)]
        output_filename_gif = 'fast.gif'
        output_filename_mp4 = 'fast.mp4'
    input_filenames += input_filenames[::-1]
    print(input_filenames)
    os.chdir(input_directory)
    convert_command = ["magick", "-loop", "0"]
    for f in input_filenames:
        if name == 'fast':
            convert_command.extend(["-delay", "4", f])
        elif name == 'slow':
            convert_command.extend(["-delay", "12", f])
    ##convert_command.extend(["-delay", "50", input_filenames[-1]])
    convert_command.append(output_filename_gif)
    try: # Try to convert the PNG output to animated GIF
        with open('conversion_messages.txt', 'wt') as f:
            f.write("So far, everything's fine...\n")
            f.flush()
            check_call(convert_command, stderr=f, stdout=f)
    except: # Don't expect this conversion to work on anyone else's system.
        print("Gif conversion failed. Is ImageMagick installed?")
    convert_command = [
        'ffmpeg', '-y',
        '-i', output_filename_gif,
        '-movflags', 'faststart',
        '-pix_fmt', 'yuv420p',
        '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
        '-preset', 'veryslow',
        '-crf', '25',
        output_filename_mp4]
    try: # Now try to convert the gif to mp4
        with open('conversion_messages.txt', 'wt') as f:
            f.write("So far, everthing's fine...\n")
            f.flush()
            check_call(convert_command, stderr=f, stdout=f)
            f.flush()
        os.remove('conversion_messages.txt')
    except: # This is also unlikely to be platform independent :D
        print("MP4 conversion failed. Is ffmpeg installed?")

## Copy movies and posters to output folder
copyfile(os.path.join(input_directory, 'slow.mp4'),
         os.path.join(output_directory, 'slow.mp4'))
copyfile(os.path.join(input_directory, 'fast.mp4'),
         os.path.join(output_directory, 'fast.mp4'))
copyfile(os.path.join(input_directory, 'img0.png'),
         os.path.join(output_directory, 'slowposter.png'))
copyfile(os.path.join(input_directory, 'img9.png'),
         os.path.join(output_directory, 'fastposter.png'))

## This is a default figure so copy to 'images' in 'master' directory
image_directory = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, os.pardir, 'master', 'images', 'RR_animation'))
if not os.path.isdir(image_directory): os.mkdir(image_directory)
copyfile(os.path.join(output_directory, 'slow.mp4'),
         os.path.join(image_directory, 'slow.mp4'))
copyfile(os.path.join(output_directory, 'slowposter.png'),
         os.path.join(image_directory, 'slowposter.png'))
copyfile(os.path.join(output_directory, 'fast.mp4'),
         os.path.join(image_directory, 'fast.mp4'))
copyfile(os.path.join(output_directory, 'fastposter.png'),
         os.path.join(image_directory, 'fastposter.png'))
