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
import os

import requests
from adcm_client.packer.bundle_build import build


def file(path, **args):
    if os.path.isdir(path):
        return list(build(repopath=path, **args).values())
    else:
        with io.open(path, 'rb') as p:
            open_file = p.read()
        stream = io.BytesIO()
        stream.write(open_file)
        stream.seek(0)
        return [stream]


def web(url, timeout=600):
    response = requests.get(url=url, timeout=timeout)
    response.raise_for_status()
    return response.content
