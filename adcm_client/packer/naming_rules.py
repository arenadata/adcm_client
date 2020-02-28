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
import sys
import io
from time import gmtime, strftime

from git import Repo
from git.exc import InvalidGitRepositoryError

from .data.config_data import ConfigData


class NoVersionFound(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors


class RestrictedSymbol(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors


class ReadFileWrapper:
    def __init__(self, stream: io.StringIO):
        self.stream = stream

    def __next__(self):
        if self.stream.tell() == self.get_end():
            raise StopIteration
        start, line = self.stream.tell(), self.stream.readline()
        end = self.stream.tell()
        return start, line, end

    def __iter__(self):
        return self

    def get_end(self):
        cur_pos = self.stream.tell()
        end_pos = self.stream.seek(0, 2)
        self.stream.seek(cur_pos)
        return end_pos


def add_build_id(path, reponame, edition, master_branches: list):
    def write_version(file, old_version, new_version):
        with io.open(file, 'r+') as config:
            for start_pos, line, end_pos in ReadFileWrapper(config):
                if 'version:' in line and old_version in line:
                    # remember tail
                    # truncate from position before line
                    # write new line
                    # write end of file
                    config.seek(end_pos)
                    tail = config.read()
                    config.seek(start_pos)
                    config.truncate()
                    new_end_pos = config.write(line.replace(old_version, new_version))
                    config.write(tail)
                    config.seek(new_end_pos)

    edition = "community" if edition is None or edition == "None" else edition
    bundle = ConfigData(catalog=path)
    version = bundle.get_data('version', 'catalog', explict_raw=True)

    if version is None:
        raise NoVersionFound('No version detected').with_traceback(sys.exc_info()[2])

    try:
        git = Repo(path).git
        if git.describe('--all').split('/')[0] == 'tags':
            tag = git.describe('--all')
            branch = [out.split('/')[2] for out in git.branch('-a', '--contains', tag).splitlines()
                      if 'origin' in out][0]
        else:
            try:
                branch = git.describe('--all').split('/')[2]
            except IndexError:
                branch = git.rev_parse('--abbrev-ref', 'HEAD')
        if branch in master_branches:
            branch = '-1'
        elif git.describe('--all').split('/')[1] == 'pr':
            branch = '-rc' + branch + '.' + strftime("%Y%m%d%H%M%S", gmtime())
        else:
            branch = '-' + branch.replace("-", "_")
    except InvalidGitRepositoryError:
        branch = ''
    else:
        if not isinstance(version, str):
            raise TypeError('Bundle version must be string').with_traceback(sys.exc_info()[2])
        if '-' in version:
            raise RestrictedSymbol('Version contains restricted symbol \
                "-" in position %s' % version.index('-')).with_traceback(sys.exc_info()[2])
        write_version(bundle.file, version, version + branch)

    return str(reponame) + '_v' + str(version) + branch + '_' + edition + '.tgz'
