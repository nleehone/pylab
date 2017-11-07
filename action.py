"""
The Feature class implements getter and setter functions that can check their type and process parameters.

When a Feature is initialized (__init__) it creates two function slots to store the getter (fget) and setter (fset)
The Feature is first called (__call__) during decoration and sets the getter function
    @Feature()
    def feature_name(self):
        ...

After this, a setter function can be added by either calling the Feature again, or calling its setter:
    @feature_name
    def setter(self, val):
        ...

    @feature_name.setter
    def setter(self, val):
        ...

When the getter is called (e.g. print(feature_name)), the __get__ function is called which uses the fget function
to execute the action.

When the setter is called (e.g. feature_name = 10), the __set__ function is called which uses the fset function to
execute the action.

"""


class Action(object):
    def __init__(self):
        self.func = None

    def __call__(self, func):
        self.func = func

        return self.func
