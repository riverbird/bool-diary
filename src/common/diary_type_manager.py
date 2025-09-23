# diary_type_manager.py
# from common.singleton_meta import SingletonMeta
# 采用这种方式后，跨模块后却成了不同地址。
# class DiaryTypeManager(metaclass=SingletonMeta):
#     def __init__(self):
#         self._diary_type_list = None
#
#     @property
#     def diary_type_list(self):
#         return self._diary_type_list
#
#     @diary_type_list.setter
#     def diary_type_list(self, value):
#         self._diary_type_list = value

global_diary_type_list = []