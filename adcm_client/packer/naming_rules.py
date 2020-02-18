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


def add_build_id(path, reponame, edition, master_branches: list):
    def write_version(file, old_version, new_version):
        with open(file, 'r+') as config:
            data = config.read()
            data = data.replace(old_version, new_version)
            config.seek(0)
            config.truncate()
            config.write(data)

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
