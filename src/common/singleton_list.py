from threading import Lock

class SingletonList:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        # 保证线程安全
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._diary_type_list = []   # 初始化 list
        return cls._instance

    @property
    def diary_type_list(self):
        return self._diary_type_list

    @diary_type_list.setter
    def diary_type_list(self, value):
        if isinstance(value, list):
            self._diary_type_list = value
        else:
            self._diary_type_list.append(value)

    def __repr__(self):
        return f"SingletonList({self._diary_type_list})"