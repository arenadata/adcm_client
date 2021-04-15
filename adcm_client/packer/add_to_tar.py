# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import re
import sys
from fnmatch import fnmatch
from os import DirEntry, chdir, getcwd, scandir
from os.path import normpath


class NotValidSpecVersion(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors


def compare_helper(version, except_list):
    if version not in (None, "1.0"):
        raise NotValidSpecVersion("Not valid spec version").with_traceback(
            sys.exc_info()[2]
        )

    if version is None:
        except_list.extend(
            [
                "spec.yaml",
                "pylintrc",
                ".[0-9a-zA-Z]*",
                "*pycache*",
                "README.md",
                "*requirements*",
                "*.gz",
                "*.md",
            ]
        )

        def v_none(sub: DirEntry):
            for pattern in except_list:
                if fnmatch(normpath(sub.path), pattern) or fnmatch(sub.name, pattern):
                    return True
            return False

        func = v_none
    elif version == "1.0":
        prog = [re.compile(i) for i in except_list]

        def v_1_0(sub: DirEntry):
            for pattern in prog:
                if pattern.match(normpath(sub.path)):
                    return True
            return False

        func = v_1_0
    return func


def add_to_tar(version, directory, except_list, tar):
    comparator = compare_helper(version, except_list)
    cwd = getcwd()
    chdir(directory)

    def _add_to_tar(path="./"):
        for sub in scandir(path):
            if not comparator(sub=sub):
                if sub.is_dir():
                    _add_to_tar(path=normpath(sub.path))
                else:
                    tar.add(normpath(sub.path))

    _add_to_tar()
    chdir(cwd)
