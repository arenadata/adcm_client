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
import logging
import os
import sys
import tarfile
from distutils.dir_util import copy_tree, remove_tree
from io import BytesIO
from tempfile import mkdtemp

from .add_to_tar import add_to_tar
from .naming_rules import add_build_id
from .spec import SpecFile, spec_processing


def _prepare_ws(reponame, workspace, src_path, spec: SpecFile):
    edition_dirs = {}
    tmpdir = mkdtemp(prefix=reponame + '_', dir=workspace)
    for edition in spec.data['editions']:
        edition_dirs.update({edition['name']: os.path.join(tmpdir, str(edition['name']))})
        copy_tree(src_path, edition_dirs[edition['name']])
    return tmpdir, edition_dirs


def _prepare_result_dir(workspace, tarball_path):
    if tarball_path:
        os.makedirs(tarball_path, exist_ok=True)
        return tarball_path
    else:
        return workspace


def _pack(reponame, repopaths, tarpaths, spec: SpecFile, **kwargs):
    for edition in spec.data['editions']:
        name = edition.get('name')
        tarpath = tarpaths[name] if isinstance(tarpaths, dict) else tarpaths
        repopath = repopaths[name]
        tar_except = edition.get('exclude', [])

        # naming rules
        tarname = add_build_id(repopath, reponame, name, kwargs['master_branches'])

        stream = BytesIO()
        tar = tarfile.open(fileobj=stream, mode='w|gz')
        add_to_tar(spec.data['version'], repopath, tar_except, tar)
        logging.info("#######\n Edition %s \n#######", name)
        logging.info("#######\n Packed files list:\n%s\n#######", "\n".join(tar.getnames()))
        tar.close()
        stream.seek(0)
        # saving tarball
        yield os.path.join(tarpath, tarname), stream


def _clean_ws(path):
    if isinstance(path, dict):
        for i in path.values():
            remove_tree(i)
    else:
        remove_tree(path)


def build(reponame=None, repopath=None, workspace='/tmp',  # pylint: disable=R0913
          tarball_path=None, loglevel='ERROR',
          clean_ws=True, master_branches=None, **args):
    """Moves sources to workspace inside of temporary directory. \
    Some operations over sources cant be proceed concurent(for exemple in pytest with xdist \
    plugin) that why each thread need is own tmp dir with sources. \
    Also when there is complex docker containers launching to process some information there is \
    necessery to share same workspace with every used container.
    Proceed spec file.
    Writes build number to bundle config file.
    Recursively add files to bytes stream.
    Cleanup tmp dirs.

    :param repopath: Where bundle sources are
    :type repopath: str
    :param reponame: arenadata repository name. Used for naming aftifact and tmp dir.
    :type reponame: str
    :param workspace: where build operations will be performed, defaults to /tmp.
    :type workspace: str, optional
    :param tarball_path: where to copy builded bundle, defaults to None.
    None means that tarball will be left in temporary directory inside of workspace.
    :type tarball_path: str, optional
    :param loglevel: lower or equal to INFO will be stdout
    :type loglevel: str, optional
    :return: return a dict.
    Keys - path and name of tarball to save.
    Value - stream of bytes.
    :rtype: dict
    """
    if not master_branches:
        master_branches = ['master']
    if not repopath:
        raise ValueError('path to source should be defined')
    if not reponame:
        reponame = os.path.basename(os.path.realpath(repopath))

    logging.basicConfig(stream=sys.stdout, level=getattr(logging, loglevel))
    spec = SpecFile(os.path.join(repopath, 'spec.yaml'))
    spec.normalize_spec()

    ws_tepm_dir, work_dir_paths = _prepare_ws(reponame, workspace, repopath, spec)

    tarpath = _prepare_result_dir(workspace, tarball_path)
    spec_processing(spec, work_dir_paths, workspace)

    out = dict(
        _pack(
            reponame,
            work_dir_paths,
            tarpath,
            spec,
            master_branches=master_branches))

    if clean_ws:
        _clean_ws(ws_tepm_dir)

    return out
