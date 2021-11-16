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

from os.path import realpath, dirname

import setuptools
from ad_ci_tools import JenkinsRepo  # pylint: disable=E0401
from pytz import timezone  # pylint: disable=E0401

test_deps = [
    'pytest',
]
setup_deps = [
    'ad_ci_tools==0.1.5',
    'pytz',
    'setuptools',
    'wheel'
]
extras = {
    'test': test_deps,
    'setup': setup_deps
}


def version_build():
    repo = JenkinsRepo(dirname(realpath(__file__)))
    git_data = repo.get_git_data()
    headoffice_tz = timezone('Europe/Moscow')
    version = repo.head.commit.committed_datetime.astimezone(headoffice_tz).strftime('%Y.%m.%d.%H')
    postfix = ''
    if 'pull_request' in git_data:
        postfix = 'rc' + git_data['pull_request']
    elif git_data.get('branch') != 'master':
        postfix = '.dev+' + git_data['branch']

    return version + postfix


setuptools.setup(
    name="adcm_client",
    version=version_build(),
    author="Anton Chevychalov",
    author_email="cab@arenadata.io",
    description="ArenaData Cluster Manager Client",
    url="https://github.com/arenadata/adcm",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'pyyaml', 'coreapi', 'ipython', 'ad_ci_tools==0.1.5',
        'docker', 'jinja2', 'version_utils'
    ],
    tests_require=test_deps,
    setup_require=setup_deps,
    extras_require=extras,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    scripts=['src/bin/adcm_sdk_shell', 'src/bin/adcm_sdk_pack'],
)
