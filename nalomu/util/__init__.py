import hashlib
import inspect
import re
from typing import Callable, Union, Any


def md5(s):
    s = str(s)
    # 创建md5对象
    hl = hashlib.md5()

    # Tips
    # 此处必须声明encode
    # 否则报错为：hl.update(str)    Unicode-objects must be encoded before hashing
    hl.update(s.encode(encoding='utf-8'))
    return hl.hexdigest()


def is_number(num):
    """
    判断是否是数字
    :rtype: bool
    """
    pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
    result = pattern.match(str(num))
    if result:
        return True
    else:
        return False


class NDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, item):
        d = self.get(item) if item in self else None
        return NDict(**d) if isinstance(d, dict) else d

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    # def __missing__(self, key):
    #     return None


def get_class_that_defined_method(meth: Union[Callable, Any]):
    if inspect.ismethod(meth):
        for cls in inspect.getmro(meth.__self__.__class__):
            if cls.__dict__.get(meth.__name__) is meth:
                return cls
        meth = meth.__func__  # fallback to __qualname__ parsing
    if inspect.isfunction(meth):
        cls = getattr(inspect.getmodule(meth),
                      meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])
        if isinstance(cls, type):
            return cls
    return None  # not required since None would have been implicitly returned anyway
