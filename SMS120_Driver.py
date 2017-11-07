from driver import Driver
from feature import Feature


class SMS120_Driver(Driver):
    @Feature()
    def ramp_rate(self):
        return self.query('GET RATE')

    @ramp_rate.setter
    def ramp_rate(self, value):
        self.send('SET RAMP {}'.format(value))

    @Feature
    def tesla_per_amp(self):
        return self.query('TPA')

    @tesla_per_amp.setter
    def tesla_per_amp(self, value):
        self.send('SET TPA {}'.format(value))



if __name__ == '__main__':
    driver = SMS120_Driver()

    print(driver.message)
    print(driver.ramp_rate)
    driver.ramp_rate = 10
    print(driver.ramp_rate)