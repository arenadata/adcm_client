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
    if version is None:
        except_list.extend([
            'spec.yaml', 'pylintrc', '.[0-9a-zA-Z]*', '*pycache*',
            'README.md', '*requirements*', '*.gz', '*.md'])

        def v_None(sub: DirEntry):
            for n in except_list:
                if fnmatch(normpath(sub.path), n) or fnmatch(sub.name, n):
                    return True
            return False
        return v_None
    elif version == "1.0":
        prog = [re.compile(i) for i in except_list]

        def v_1_0(sub: DirEntry):
            for n in prog:
                if n.match(normpath(sub.path)):
                    return True
            return False
        return v_1_0
    else:
        raise NotValidSpecVersion('Not valid spec version').with_traceback(sys.exc_info()[2])


def add_to_tar(version, directory, except_list, tar):
    comparator = compare_helper(version, except_list)
    cwd = getcwd()
    chdir(directory)

    def _add_to_tar(path='./'):
        for sub in scandir(path):
            if not comparator(sub=sub):
                if sub.is_dir():
                    _add_to_tar(path=normpath(sub.path))
                else:
                    tar.add(normpath(sub.path))
    _add_to_tar()
    chdir(cwd)
