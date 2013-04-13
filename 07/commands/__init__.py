from tools.mycollections import OrderedSet

_classes = OrderedSet()

def register(_class):
    _classes.add(_class)

def new(*args, **kwargs):
    for _class in _classes:
        if _class.accept(*args, **kwargs):
            return _class(*args, **kwargs)