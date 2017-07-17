import numpy as np
import ni
import leica_scope
import physik_instrumente
import image_data_pipeline
from pco import pco_edge_camera_child_process, legalize_roi
import time

if __name__ == '__main__':
    import multiprocessing as mp
    import logging
    logger = mp.log_to_stderr()
    logger.setLevel(logging.INFO)

    # Analog out card channel definitions
    ao_camera = 0
    ao_insert_piezo = 1
    ao_rr_piezo = 2
    
    # COM port defitions
    dmi8_com_port = 'COM4'
    rr_piezo_com_port = 'COM6'

    # Acquisition settings
    exposure_ms = 1 # includes rolling time
    num_frames = 1000
    filename_format = '%s_z_step_%s.tif' # (light_channel, z_step)
    light_channel = 'transmitted'
    roi = legalize_roi({'top':925, # Be careful to choose a 'legal' roi!
##                        'left':1,
##                        'right':2060
                        })

    # Objective choice
    objective = 'oil' # Choose 'air' or 'oil'
    #  'air':0.98 for best correction collar setting of 0.19 for Argolight
    #  'oil':1.45
    z_ratio = {'air':0.98, 'oil':1.45}[objective]

    # Z step size half amplitude
    focus = 0
    z_step = 10 # microns, relative to current set point
    dmi8_z_step = -z_step # insert can only move away so match polarity here
    insert_piezo_z_step = z_step
    rr_piezo_z_step = -z_step * z_ratio # microns, scaled piezo step size 

    # Initialize hardware
    idp = image_data_pipeline.Image_Data_Pipeline(
            num_buffers=1,
            buffer_shape=(num_frames,
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
    dmi8 = leica_scope.DMI_8_Microscope(dmi8_com_port)
    # insert_piezo will be controlled via analog and should be
    # setup manually using manufacturer software
    rr_piezo = physik_instrumente.E753_Z_Piezo(which_port=rr_piezo_com_port,
                                               verbose=False)  
    # Set DMI8 tube lens changer to fourth (empty) position
    dmi8.set_max_pos_magn(max_n=4)
    dmi8.change_magn(4)
    ######################## to do check piezo insert control
    def insert_voltage_from_position(desired_insert_offset_um):
        insert_position_abs = desired_insert_offset_um
        insert_analog_in_voltage = insert_position_abs / 50
        assert 0 <= insert_analog_in_voltage <= 10
        return insert_analog_in_voltage
    # Send piezo to default zero position
    rr_piezo.move(50) # Microns
    rr_piezo._finish_moving()
    rr_piezo.set_analog_control_state(True)
    def piezo_voltage_from_position(desired_piezo_offset_um):
        piezo_position_abs = 50 + desired_piezo_offset_um
        piezo_analog_in_voltage = (piezo_position_abs - 50) / 5
        assert -10 <= piezo_analog_in_voltage <= 10
        return piezo_analog_in_voltage

    # Set up voltages for analog out control
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
    # Create voltages for camera to run for n frames for dmi8 motion
    static_frame_voltages = np.zeros(voltage_shape, dtype=np.float64)
    static_frame_voltages[:start_pix, ao_camera] = TTL_HIGH_V
    static_frames = round(num_frames / 2)
    for n in range(static_frames):
        voltages_list.append(static_frame_voltages)
    # Create stage insert step voltages
    insert_piezo_voltages = np.zeros(voltage_shape, dtype=np.float64)
    insert_piezo_voltages[:, ao_insert_piezo] = insert_voltage_from_position(
        insert_piezo_z_step)
    insert_piezo_voltages[:start_pix, ao_camera] = TTL_HIGH_V
    insert_piezo_frames = 50
    for n in range(insert_piezo_frames):
        voltages_list.append(insert_piezo_voltages)
    # Create voltages for camera to run for n frames after stage insert motion
    static_frames = round(num_frames / 4) - insert_piezo_frames
    for n in range(static_frames):
        voltages_list.append(static_frame_voltages)
    # Create rr piezo step voltages
    rr_piezo_voltages = np.zeros(voltage_shape, dtype=np.float64)
    rr_piezo_voltages[:, ao_rr_piezo] = piezo_voltage_from_position(
        rr_piezo_z_step)
    rr_piezo_voltages[:start_pix, ao_camera] = TTL_HIGH_V
    rr_piezo_frames = 15
    for n in range(rr_piezo_frames):
        voltages_list.append(rr_piezo_voltages)
    # Create voltages for camera to run for n frames after piezo motion
    static_frames = round(num_frames / 4) - rr_piezo_frames
    for n in range(static_frames):
        voltages_list.append(static_frame_voltages)
    # Combine voltages into single array
    voltages = np.concatenate(voltages_list, axis=0)
    # Wait for any previous file saving to finish:
    while len(idp.idle_data_buffers) == 0:
        idp.collect_permission_slips()
    # Tell the camera to start trying to take a stack of images, and
    # tell it where to save the images:
    idp.load_permission_slips(
        num_slips=1,
        file_saving_info=[
            {'filename': filename_format %(light_channel, z_step)}])
    while not idp.camera.input_queue.empty(): # Is the camera ready?
        pass

    # Play analog voltages non blocking
    ao.play_voltages(voltages, block=False)

    time.sleep(0.05)
    
    # Step the DMI8 z drive
    dmi8_z0_um = dmi8.current_z_microns
    dmi8_z_absolute = dmi8_z0_um + dmi8_z_step
    dmi8.move_z_drive(target=dmi8_z_absolute, blocking=True, timeout=1)
    dmi8.move_z_drive(target=dmi8_z0_um, blocking=True, timeout=1)

    # Make sure ao has finished play
    ao._ensure_task_is_stopped()

    # Close all objects
    idp.close()
    ao.close()
    dmi8.close()
    rr_piezo.close()
