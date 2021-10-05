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
import io
import sys

from ad_ci_tools import JenkinsRepo
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


def check_version(version):
    """Check version format rules

    :param version: bundle_version
    :type version: str
    :raises NoVersionFound: no version is given
    :raises TypeError: version is not string
    :raises RestrictedSymbol: version contains dash
    """
    if not isinstance(version, str):
        raise TypeError('Bundle version must be string').with_traceback(sys.exc_info()[2])
    if '-' in version:
        raise RestrictedSymbol(f'Version contains restricted symbol \
            "-" in position {version.index("-")}').with_traceback(sys.exc_info()[2])


def resolve_build_id(git_data, master_branches, timestamp):
    """resolves build id according to discovered git data

    :param git_data: discovered git data
    :type git_data: None or dict
    :param master_branches: list of master branches
    :type master_branches: list
    :param timestamp: Timestamp string to be added to version
    :return: build id
    :rtype: str
    """
    if git_data:
        if 'pull_request' in git_data:
            build_id = '-rc' + git_data['pull_request'] + '.' + timestamp
        else:
            if git_data['branch'] in master_branches:
                build_id = '-1'
            else:
                build_id = '-' + git_data['branch'].replace("-", "_").replace("/", "_")
    else:
        build_id = '-1'
    return build_id


def add_build_id(path, reponame, edition, master_branches: list, timestamp):
    def write_version(file, old_version, new_version):
        with io.open(file, 'r+', encoding='utf-8') as config:
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
                    new_end_pos = start_pos + config.write(line.replace(old_version, new_version))
                    config.write(tail)
                    config.seek(new_end_pos)

    edition = "community" if edition is None or edition == "None" else edition
    bundle = ConfigData(catalog=path)
    version = bundle.get_data('version', 'catalog', explict_raw=True)

    if version is None:
        raise NoVersionFound('No version detected').with_traceback(sys.exc_info()[2])

    try:
        git_data = JenkinsRepo(path).get_git_data()
    except InvalidGitRepositoryError:
        git_data = None

    build_id = ''
    if git_data:
        check_version(version)
        build_id = resolve_build_id(git_data, master_branches, timestamp)
        write_version(bundle.file, version, version + build_id)

    return str(reponame) + '_v' + str(version) + build_id + '_' + edition + '.tgz'
