from driver import Driver
from feature import Feature
from action import Action
import visa


class LS350_Driver(Driver):
    def __init__(self, resource):
        super().__init__(resource)
        self.instr.baud_rate = 57600
        self.instr.parity = visa.constants.Parity.odd
        self.instr.data_bits = 7
        self.instr.read_termination = '\n'
        self.instr.write_termination = '\n'

    def set_ramp_parameters(self, output, rate, enable=True):
        if rate is None:
            enable = False
            rate = 0
        enable = 1 if enable else 0
        print('RAMP {},{},{}'.format(output, enable, rate))
        self.send('RAMP {},{},{}'.format(output, enable, rate))

    def get_ramp_parameters(self):
        return self.query('RAMP?')

    def set_temperature_celsius(self, output, T):
        # Assumes that the control loop sensor preferred units are Kelvin. If this is not the case use set_temperature
        self.send('SETP {},{}'.format(output, float(T) + 273.15))

    def get_temperature_celsius(self, input):
        T = self.query('CRDG? {}'.format(input))
        return float(T)

    def get_sensor_reading(self, input):
        S = self.query('SRDG? {}'.format(input))
        return float(S)

    def is_ramping(self, output):
        rampst = self.query('RAMPST? {}'.format(output))
        return bool(rampst)

    """"@Action()
    def clear_interface(self):
        self.send("*CLS")

    @Feature()
    def identification(self):
        self.query("*IDN?")

    @Feature()
    def event_status_enable_register(self):
        return self.query('*ESE?')

    @event_status_enable_register.setter
    def event_status_enable_register(self, value):
        self.send('*ESE {}'.format(value))

    @Feature()
    def temperature_Kelvin(self, value):
        self.query('*KRDG? {}'.format(value))"""


if __name__ == '__main__':
    driver = LS350_Driver()

    driver.clear_interface()
    print(driver.message)
    print(driver.ramp_rate)
    driver.ramp_rate = 10
    print(driver.ramp_rate)
