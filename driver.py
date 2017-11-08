class Driver(object):
    def __init__(self, resource):
        self.instr = resource

    def query(self, query_string):
        return self.instr.query(query_string)

    def send(self, message):
        self.instr.write(message)
