from LS350_Driver import LS350_Driver
from time import time
import logging
import visa

# ----------------------------------
# Configuration. Set parameters here
# ----------------------------------
filename = 'test.dat'
T_range = 0.01
ramp_rate = 10 # 10 K/minute
settle_time = 30*1000 # milliseconds
timeout = 600*1000 # milliseconds

sensor_input = 'A'
sensor_output = 1


def set_temperature_and_settle(T_set, T_range, settle_time, timeout):
    LS350.set_temperature_celsius(sensor_output, T_set)

    timer = time()

    settled = False

    while True:
        if timeout < time() - timer:
            logging.warning('Reached timeeout! Possible Causes: timeout may be too small, heater power not set correctly, wrong flow rate.')
            break

        T_curr = LS350.get_temperature_celsius(sensor_input)

        if abs(T_set - T_curr) < T_range:
            if settle_time < time() - timer:
                settled = True
                break
        else:
            # Reset the timer if the temperature is out of range
            logging.info('Timer reset because temperature out of range: T_set={}, T_curr={}, T_range={}'.format(T_set, T_curr, T_range))
            timer = time()

    return settled, time() - timer


def measure_temperature():
    T_curr = LS350.get_temperature_celsius(sensor_input)
    file.write('{} {}'.format(time(), T_curr))
    return T_curr


rm = visa.ResourceManager()
rm.list_resources()
LS350 = LS350_Driver(rm.open_resource(''))

log_filename = '{}.log'.format(filename.split('.')[0])
logging.basicConfig(filename=log_filename, format='%(asctime)s:%(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')

file = open(filename, 'w')
file.write('SETUP: Ramp Rate={} C/minute'.format(ramp_rate))
file.write('SETUP: Temperature settle range=+/-{} C'.format(ramp_rate))
file.write('\n')
file.write('DATA:')


# ------------------------------------------------
# Measurement protocol
# ------------------------------------------------
logging.info('Ramp rate set to None for fast ramp')
LS350.set_ramp_parameters(1, None)

# Step: Set temperature to room temperature
# -----------------------------------------
T_room = 20
logging.info('Set temperature to {} C and wait for settle'.format(T_room))

settled, timer = set_temperature_and_settle(T_room, T_range, settle_time, timeout)
if not settled:
    logging.error('Could not set the temperature to {} C. Check the flow rate and heater power.'.format(20))
    exit(1)
else:
    logging.info('Settled at 20 C in {} seconds'.format(timer))

# Step: Ramp to T_set and then settle there
# -----------------------------------------
T_set = -95

logging.info('Ramp rate set to {} C/minute'.format())
LS350.set_ramp_parameters(1, ramp_rate)
logging.info('Set temperature to {} C. Initiating ramp.'.format(T_set))
LS350.set_temperature_celsius(T_set)
file.write('INFO: Ramp BEGIN') # Split the data file

ramp_end = False
while True:
    T_curr = measure_temperature()

    if not LS350.is_ramping() and not ramp_end:
        logging.info('Ramp ended because setpoint reached. T_set={}, T_curr={}, T_range={}'.format(-95, T_curr, T_range))
        file.write('INFO: Ramp END') # Split the data file
        ramp_end = True # Make sure we don't re-record this event

    if abs(T_set - T_curr) < T_range:
        if settle_time < time() - timer:
            # Settling will happen after the ramp ends. This will track how much time elapsed
            logging.info('Settled at {} C'.format(T_set))
            file.write('INFO: Settled at {} C'.format(T_set))
            settled = True
            break
    else:
        # Reset the timer if the temperature is out of range
        timer = time()

# Step: Hold temperature stable
# -----------------------------------------

stable_time = 1*3600*1000 # Time to keep temperature stable in milliseconds
timer = time()
file.write('INFO: Stability BEGIN')
while True:
    T_curr = measure_temperature()

    if time() - timer > stable_time:
        logging.info('Finished stability test for: {}'.format(time() - timer))
        break

file.write('INFO: Stability END')

logging.info('Measurement protocol finished')
file.close()
