from LS350_Driver import LS350_Driver
from time import time
import logging
import visa

rm = visa.ResourceManager()
print(rm.list_resources())

# ----------------------------------
# Configuration. Set parameters here
# ----------------------------------
filename = 'test.dat'
T_range = 0.1
ramp_rate = 10 # 10 K/minute
settle_time = 30 # seconds
timeout = 600 # seconds

LS350_address = 'ASRL6::INSTR'
sensor_input = 'A'
sensor_output = 1


def set_temperature_and_settle(T_set, T_range, settle_time, timeout):
    LS350.set_temperature_celsius(sensor_output, T_set)

    timer = time()
    settled_timer = time()

    settled = False

    while True:
        if timeout < time() - timer:
            logging.warning('Reached timeout! Possible Causes: timeout may be too small, heater power not set correctly, wrong flow rate.')
            break

        T_curr = measure_temperature()

        if abs(T_set - T_curr) <= T_range:
            if settle_time < time() - settled_timer:
                settled = True
                break
        else:
            # Reset the timer if the temperature is out of range
            logging.info('Timer reset because temperature out of range: T_set={}, T_curr={}, T_range={}'.format(T_set, T_curr, T_range))
            settled_timer = time()

    return settled, time() - timer


def measure_temperature():
    T_curr = LS350.get_temperature_celsius(sensor_input)
    S_curr = LS350.get_sensor_reading(sensor_input)
    file.write('{} {} {}\n'.format(time(), T_curr, S_curr))
    return T_curr


def close():
    global rm
    LS350.instr.close()
    del LS350.instr
    rm.close()
    del rm


LS350 = LS350_Driver(rm.open_resource(LS350_address))
print(LS350.instr)
print(LS350.instr.query("*IDN?"))
print(LS350.instr.write("*CLS"))

log_filename = '{}.log'.format(filename.split('.')[0])
logging.basicConfig(filename=log_filename, format='%(asctime)s.%(msecs)03d:%(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)

file = open(filename, 'w', buffering=1)
file.write('SETUP: Ramp Rate={} C/minute\n'.format(ramp_rate))
file.write('SETUP: Temperature settle range=+/-{} C\n'.format(ramp_rate))
file.write('\n')
file.write('DATA:\n')


# ------------------------------------------------
# Measurement protocol
# ------------------------------------------------

# Step: Set temperature to room temperature
# -----------------------------------------
print("Set temperature to room temperature")

logging.info('Ramp rate set to None for fast ramp')
LS350.set_ramp_parameters(sensor_output, None)

T_room = 23
logging.info('Set temperature to {} C and wait for settle'.format(T_room))

file.write("INFO: Settle room temperature BEGIN.".format(T_room))
settled, timer = set_temperature_and_settle(T_room, T_range, settle_time, timeout)
if not settled:
    logging.error('Could not set the temperature to {} C. Check the flow rate and heater power.'.format(20))
    close()
    file.close()
    exit(1)
else:
    logging.info('Settled at {} C in {} seconds'.format(T_room, timer))
file.write("INFO: Settle room temperature END.\n".format(T_room))

# Step: Ramp to T_set and then settle there
# -----------------------------------------
print("Ramp to T_set and then settle there")

T_set = -95

logging.info('Ramp rate set to {} C/minute'.format(ramp_rate))
LS350.set_ramp_parameters(sensor_output, ramp_rate)
logging.info('Set temperature to {} C. Initiating ramp.'.format(T_set))
LS350.set_temperature_celsius(sensor_input, T_set)
file.write('INFO: Ramp BEGIN\n') # Split the data file

ramp_end = False
while True:
    T_curr = measure_temperature()

    if not LS350.is_ramping(sensor_input) and not ramp_end:
        logging.info('Ramp ended because setpoint reached. T_set={}, T_curr={}, T_range={}'.format(-95, T_curr, T_range))
        file.write('INFO: Ramp END\n') # Split the data file
        ramp_end = True # Make sure we don't re-record this event

    if abs(T_set - T_curr) < T_range:
        if settle_time < time() - timer:
            # Settling will happen after the ramp ends. This will track how much time elapsed
            logging.info('Settled at {} C'.format(T_set))
            file.write('INFO: Settled at {} C\n'.format(T_set))
            settled = True
            break
    else:
        # Reset the timer if the temperature is out of range
        timer = time()

# Step: Hold temperature stable
# -----------------------------------------
print("Hold temperature stable")

stable_time = 1*3600 # Time to keep temperature stable in seconds
timer = time()
file.write('INFO: Stability BEGIN\n')
while True:
    T_curr = measure_temperature()

    if time() - timer > stable_time:
        logging.info('Finished stability test for: {}'.format(time() - timer))
        break

file.write('INFO: Stability END\n')

logging.info('Measurement protocol finished')
close()
file.close()
