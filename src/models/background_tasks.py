import asyncio
import random
from .data_structures import TaskTypes
import re
import threading


def checkings_thread(self):
    global find_valid_sortings
    from models.generate_sortings import find_valid_sortings
    self.imports_loaded.set()
    firstIteration = True
    while True:
        with self.condition:
            if not firstIteration:
                del self.checkings_list[0]
            firstIteration = False
            while not self.checkings_list:
                self.condition.wait()
            task = self.checkings_list[0]
        data = self.collections[task["collectionName"]].data[1:]
        roles = self.collections[task["collectionName"]].roles
        res = find_valid_sortings(data, roles)
        if type(res) is str:
            self._errorMsg = res
            self.signal.emit({"type": "FloatingWindow_text_changed", "value": res})
        else:
            if self._errorMsg:
                self._errorMsg = []
                self.signal.emit({"type": "FloatingWindow_text_changed", "value": ""})

def sortings_thread(self):
    self.imports_loaded.wait()
    firstIteration = True
    while True:
        with self.condition:
            if not firstIteration:
                del self.sortings_list[0]
            firstIteration = False
            while not self.sortings_list:
                self.condition.wait()
            task = self.sortings_list[0]
            collectionName = task["collectionName"]
            task_id = task["id"]
        data = self.collections[collectionName].data[1:]
        roles = self.collections[collectionName].roles
        res = find_valid_sortings(data, roles)
        with self._data_lock:
            if self.sortings_list[0]["id"] != task_id:
                continue
            if type(res) is str:
                for e in self._errorMsg:
                    if e[0] == collectionName:
                        e[1] = res
                        break
                else:
                    self._errorMsg.append([collectionName, res])
                self.signal.emit({"type": "FloatingWindow_text_changed", "value": "\n".join([" : ".join(e) for e in self._errorMsg])})
            else:
                new_errorMsg = filter(lambda x: x[0] != collectionName, self._errorMsg)
                if new_errorMsg != self._errorMsg:
                    self.signal.emit({"type": "FloatingWindow_text_changed", "value": "\n".join([" : ".join(e) for e in self._errorMsg])})
                if task["reorder"] and res[0] != list(range(len(data))):
                    self.beginResetModel()
                    self._data[1:] = [data[i] for i in res[0]]
                    for r in self._data[1:]:
                        for colInd, c in enumerate(r):
                            if roles[colInd] != 'dependencies':
                                continue
                            r[colInd] = re.sub(
                                r'(after\s+|as far as possible from\s+)([1-9][0-9]*)(?=;|$)',
                                lambda m: m.group(1) + str(res[0].index(int(m.group(2)) - 1) + 1),
                                c
                            )
                    for i in range(len(self._data) - 1, -1, -1):
                        if self._data[i] == [""] * len(self._data[0]):
                            self._data.pop(i)
                            self._rowHeights.pop(i)
                    self.verticalScroll(self._verticalScrollPosition, self._verticalScrollSize, self._tableViewContentY, self._tableViewHeight)
                    self.endResetModel()
                    self.save_to_file()


def setup_background_tasks(model):
    thread = threading.Thread(target=checkings_thread, args=(model,))
    thread.start()
    thread = threading.Thread(target=sortings_thread, args=(model,))
    thread.start()