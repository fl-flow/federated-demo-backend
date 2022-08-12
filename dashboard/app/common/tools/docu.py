import os

import os
from zipfile import ZipFile


class Recursion(object):
    def __init__(self):
        pass

    def unzips(self, path, total_count):
        """
        层级解压并写入zip压缩当前路径
        :param path: 目录路径
        :param total_count: 文件执行数
        """
        for root, dirs, files in os.walk(path):
            for file in files:
                # file_name = (os.path.join(root, file)).replace('\\', '/')
                file_name = root + '/' + file
                if not (file_name.endswith('.zip')):
                    total_count += 1
                else:
                    currentdir = file_name[:-4]
                    if not os.path.exists(currentdir):
                        os.makedirs(currentdir)
                    with ZipFile(file_name) as zipObj:
                        zipObj.extractall(currentdir)
                    os.remove(file_name)
                    # print(file_name, '1111111111111')
                    total_count = self.unzips(currentdir, total_count)
        return total_count


