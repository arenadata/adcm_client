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

"""Utilities to work with objects' configurations"""

from collections.abc import Mapping


def update(current_config: dict, changes: dict) -> dict:
    """
    If the old and new values are dictionaries, we try to update, otherwise we replace.
    Current config is updated, not copied.
    """
    for key, value in changes.items():
        if (
            isinstance(value, Mapping)
            and key in current_config
            and isinstance(current_config[key], Mapping)
        ):
            current_config[key] = update(current_config[key], value)
            continue
        current_config[key] = value
    return current_config
