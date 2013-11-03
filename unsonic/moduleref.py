class ModuleRef(object):
    def __init__(self, obj=None):
        self.__setobj__(obj)

    def __setobj__(self, obj):
        self.__dict__["__obj__"] = obj

    def __getattr__(self, name):
        if not self.__obj__:
            raise AttributeError("ModuleRef.__obj__ is None")
        return getattr(self.__obj__, name)

    def __setattr__(self, name, val):
        self.__obj__.__setattr__(name, val)

    def __call__(self, *args, **kwargs):
        return self.__obj__.__call__(*args, **kwargs)
