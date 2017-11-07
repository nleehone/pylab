class Driver(object):
    def __init__(self, resource):
        self.inst = resource

    def query(self, query_string):
        return self.inst.query(query_string)

    def send(self, message):
        self.inst.write(message)
