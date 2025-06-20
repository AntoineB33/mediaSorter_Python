import asyncio
import random
from .data_structures import AsyncTask, TaskTypes
import re


async def checkings_thread(self):
    global find_valid_sortings
    from models.generate_sortings import find_valid_sortings
    self.imports_loaded.set()
    firstIteration = True
    while True:
        task = None
        with self.condition:
            if not firstIteration:
                del self._collections.checkings_list[0]
            firstIteration = False
            while not self._collections.checkings_list:
                self.condition.wait()
            task = self._collections.checkings_list[0]
        data = self._collections.collections[task.collectionName].data
        roles = self._collections.collections[task.collectionName].roles
        res = find_valid_sortings(data, roles)
        if type(res) is str:
            self._errorMsg = res
            self.signal.emit({"type": "FloatingWindow_text_changed", "value": res})
        else:
            if self._errorMsg:
                self._errorMsg = ""
                self.signal.emit({"type": "FloatingWindow_text_changed", "value": ""})

async def sortings_thread(self):
    self.imports_loaded.wait()
    firstIteration = True
    while True:
        with self.condition:
            if not firstIteration:
                del self._collections.checkings_list[0]
            firstIteration = False
            while not self._collections.checkings_list:
                self.condition.wait()
            task = self._collections.sortings_list[0]
            collectionName = task.collectionName
            task_id = task.id
        data = self._collections.collections[collectionName].data
        roles = self._collections.collections[collectionName].roles
        res = find_valid_sortings(data, roles)
        async with self._data_lock:
            if self._collections.sortings_list[0][1] != task_id:
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
                try:
                    self._errorMsg.remove(e)
                    self.signal.emit({"type": "FloatingWindow_text_changed", "value": "\n".join([" : ".join(e) for e in self._errorMsg])})
                except ValueError:
                    pass
                if res[0] != list(range(len(data))):
                    if collectionName == self._collections.collectionName:
                        self.beginResetModel()
                        self._data = [data[i] for i in res[0]]
                        for r in self._data:
                            for c in r:
                                match = re.match(r'after\s+([1-9][0-9]*)', c)
                                if match:
                                    j = int(match.group(1)) - 1
                                    c = re.sub(r'(after\s+)([1-9][0-9]*)', r'\1' + data.index(j), c)
                                else:
                                    match = re.match(r'as far as possible from (\d+)', c)
                                    if match:
                                        X = int(match.group(1)) - 1
                                        c = re.sub(r'as far as possible from (\d+)', f'as far as possible from {data.index(X)}', c)
                        for i in range(len(self._data) - 1, -1, -1):
                            if self._data[i] == [""] * len(self._data[0]):
                                self._data.pop(i)
                                self._rowHeights.pop(i)
                        self.verticalScroll(self._verticalScrollPosition, self._verticalScrollSize, self._tableViewContentY, self._tableViewHeight)
                        self.endResetModel()
                        self.save_to_file()


def setup_background_tasks(model):
    model._executor.submit(model.run_async, checkings_thread(model))
    model._executor.submit(model.run_async, sortings_thread(model))