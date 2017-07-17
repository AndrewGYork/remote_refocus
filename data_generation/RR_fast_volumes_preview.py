import time
import tkinter
import numpy as np
import ni
import leica_scope
import physik_instrumente
import image_data_pipeline
import lumencor
from pco import pco_edge_camera_child_process, legalize_roi

if __name__ == '__main__':
    import multiprocessing as mp
    import logging
    logger = mp.log_to_stderr()
    logger.setLevel(logging.INFO)

    ### COM port assignment
    dmi8_com_port = 'COM4'
    rr_piezo_com_port = 'COM6'
    epi_com_port = 'COM10'

    ### Analog out channel settings
    ao_ch = {'camera'    :0,
             'rr_piezo'  :1,
             'spx_uv'    :2,
             'spx_blue'  :3,
             'spx_cyan'  :4,
             'spx_teal'  :5,
             'spx_green' :6,
             'spx_red'   :7,}
    ao_ch_name = {}
    for name, index in ao_ch.items():
        ao_ch_name[index]= name

    ### Objective choice
    objective = 'oil' # Choose 'air' or 'oil'
    #  'air':0.98 for best correction collar setting of 0.19 for Argolight
    #  'oil':1.42
    z_ratio = {'air':0.98, 'oil':1.42}[objective]

    ### Stack parameters
    stk_amp = 5 # set half amplitude of stack around current focus (um)
    stk_step_size = 1 # set stack step size (um)
    stk_num_steps = round(2 * stk_amp / stk_step_size) + 1
    # RR stack conversion
    rr_stk_amp = stk_amp * z_ratio

    ### Volumetric image information
    num_vol = 2
    num_colors = 2 # To change from 2 must edit voltage code
    num_frames = stk_num_steps * num_vol * num_colors
    assert num_frames < 1001 # Set sensible upper bound on buffer

    ### Illumination settings
    tl_ao_ch = ao_ch['spx_green'] # take an epi channels for trans light
    led_ao_ch = ao_ch['spx_cyan'] # set epi excitation color
    led_intensities = {'uv':255, # set epi excitation intensities
                       'blue':255,
                       'cyan':255,
                       'teal':255,
                       'green':255,
                       'red':255,}

    ### Camera settings
    exposure_ms = 20 # set exposure - includes rolling time (ms)
    filename_format = '%s_%s_vol_%sum_stk_%sum_step_%sms_exp.tif'
                    # (led_ao_ch, num_vol, stk_amp, stk_step_size, exp_ms)
    roi = legalize_roi({'top':1, # Be careful to choose a 'legal' roi!
##                        'left':1,
##                        'right':2060
                        })

    ### Initialize hardware
    # Camera
    idp = image_data_pipeline.Image_Data_Pipeline(
            num_buffers=1,
            buffer_shape=(num_frames,   # Buffer size for full volume series
                          roi['bottom']-roi['top']+1,
                          roi['right']-roi['left']+1),
            camera_child_process=pco_edge_camera_child_process)
    idp.apply_camera_settings(
            exposure_time_microseconds=exposure_ms*1000,
            trigger='external_trigger',
            preframes=0,
            region_of_interest=roi)
    ao = ni.Analog_Out(
            num_channels='all',
            rate=1e5,       # Voltages per second
            daq_type='6733',
            board_name='Dev1')
    # Microscope
    dmi8 = leica_scope.DMI_8_Microscope(dmi8_com_port)
    dmi8.set_max_pos_magn(max_n=4)
    dmi8.change_magn(4) # Set tube lens to empty position
    # Epi light source
    epi_source = lumencor.SpectraX(epi_com_port, verbose=False)
    epi_source.set_intensity(**led_intensities)
    # Remote re-focus piezo
    rr_piezo = physik_instrumente.E753_Z_Piezo(which_port=rr_piezo_com_port,
                                               verbose=False)      
    rr_piezo.move(50) # Send piezo to default zero position (um)
    rr_piezo._finish_moving()
    rr_piezo.set_analog_control_state(True)
    def piezo_volts_from_pos(desired_piezo_offset_um):
        piezo_position_abs = 50 + desired_piezo_offset_um
        piezo_analog_in_voltage = (piezo_position_abs - 50) / 5
        assert -10 <= piezo_analog_in_voltage <= 10
        return piezo_analog_in_voltage

    ### Set up voltages for analog out control
    #  Camera timing information
    TTL_HIGH_V = 3 # 3V TTL
    rolling_time_s = idp.camera.get_setting('rolling_time_microseconds')*1e-6
    exposure_time_s = idp.camera.get_setting('exposure_time_microseconds')*1e-6
    jitter_time_s = 50e-6
    assert rolling_time_s < exposure_time_s
    jitter_pix = round(jitter_time_s * ao.rate)
    assert jitter_pix > 1 # Helps ensure the camera won't swallow a trigger
    start_pix = jitter_pix + round(rolling_time_s * ao.rate)
    stop_pix = round(exposure_time_s * ao.rate)
    # Create voltage list and voltage shape
    voltages_list = [] # To fill with numpy arrays
    voltage_shape = (stop_pix + jitter_pix, ao.num_channels)
    # Create voltages for volumes
    for v in range(num_vol):
        # Create voltages for stacks
        for rr_piezo_z in np.linspace(-rr_stk_amp, rr_stk_amp, stk_num_steps):
            # Create voltages for frames
            # Transmitted light
            tl_frame_voltages = np.zeros(voltage_shape, dtype=np.float64)
            tl_frame_voltages[:start_pix, ao_ch['camera']] = TTL_HIGH_V
            tl_frame_voltages[start_pix:stop_pix, tl_ao_ch] = TTL_HIGH_V
            tl_frame_voltages[:, ao_ch['rr_piezo']] = piezo_volts_from_pos(
                rr_piezo_z)
            voltages_list.append(tl_frame_voltages)
            # Epi led excitation
            led_frame_voltages = np.zeros(voltage_shape, dtype=np.float64)
            led_frame_voltages[:start_pix, ao_ch['camera']] = TTL_HIGH_V
            led_frame_voltages[start_pix:stop_pix, led_ao_ch] = TTL_HIGH_V
            led_frame_voltages[:, ao_ch['rr_piezo']] = piezo_volts_from_pos(
                rr_piezo_z)
            voltages_list.append(led_frame_voltages)
        rr_stk_amp = -rr_stk_amp # bidirectional z scanning for speed
    # Combine voltages into single array
    voltages = np.concatenate(voltages_list, axis=0)

    ### Prepare and run livemode for preview of sample
    # Turn on transmitted light
    tl_on_voltage_shape = (10, ao.num_channels) # 10 time units wide
    tl_ao_ch_high = np.zeros(tl_on_voltage_shape, dtype=np.float64)
    tl_ao_ch_high[:, tl_ao_ch] = TTL_HIGH_V
    ao.play_voltages(tl_ao_ch_high, force_final_zeros=False)
    # Reset camera buffer for livemode
    idp.apply_camera_settings(frames_per_buffer=1) # For livemode image
    def live_mode():
        # Tell the camera to start trying to take an image
        idp.load_permission_slips(num_slips=1)
        idp.camera.commands.send(('force_trigger', {}))
        assert idp.camera.commands.recv() # Trigger must be successful
        # Wait for any previous image to finish:
        while len(idp.idle_data_buffers) == 0: idp.collect_permission_slips()
        tk.after(1, live_mode) # Re-schedule livemode
    # Set up event loop for livemode
    tk = tkinter.Tk()
    tkinter.Label(tk, text="Close window to take a volumetric series").pack()
##    tkinter.Button(tk, text="Snap", command=live_mode).pack()
    tk.after(1, live_mode) # Schedule 1st instance of live mode in event loop
    tk.mainloop() # Run event loop for livemode

    ### Reset camera properties for ao triggered stack
    idp.apply_camera_settings(frames_per_buffer=num_frames) # Reset for volumes
    # Wait for any previous file saving to finish:
    while len(idp.idle_data_buffers) == 0: idp.collect_permission_slips()
    # Tell the camera to start trying to take stacks and where to save
    idp.load_permission_slips(
        num_slips=1,
        file_saving_info=[
            {'filename': filename_format %(ao_ch_name[led_ao_ch],
                                           num_vol,
                                           2*stk_amp,
                                           stk_step_size,
                                           exposure_ms)}])
    while not idp.camera.input_queue.empty(): # Is the camera ready?
        pass # If not then hold ao play until camera is ready
            
    ### Play analog voltages
    start = time.perf_counter()
    ao.play_voltages(voltages)
    end = time.perf_counter()
##    print('Time elapsed in seconds =', end - start)
##    input('hit enter to continue...')

    ### Close all objects
    idp.close()
    ao.close()
    dmi8.close()
    rr_piezo.close()
