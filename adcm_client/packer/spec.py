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
import sys
from os.path import join
from subprocess import check_output

import yaml

from adcm_client.packer.types import get_type_func


class SpecFile:
    def __init__(self, spec):
        try:
            with open(spec, "r") as file:
                self.data = yaml.safe_load(file)
                # TODO supported verions check
                self.current_version = self.version = str(self.data.get("version", 0))

        except FileNotFoundError:
            self.data = {}

    def to_1_0(self):
        new_spec = dict(
            [
                ("version", None),
                (
                    "editions",
                    [
                        {
                            "name": None,
                            "exclude": self.except_var(self.data),
                            "preprocessors": [],
                        }
                    ],
                ),
            ]
        )
        for i in self.data.get("processing", {}):
            if i.get("script"):
                new_spec["editions"][0]["preprocessors"].append(
                    {
                        "type": "script",
                        "script": join(self.data[i["name"] + "_dir"], i["script"]),
                        "args": [i["file"]],
                    }
                )
            elif i.get("name") == "python_mod_req":
                new_spec["editions"][0]["preprocessors"].append(
                    {"type": i["name"], "requirements": i["file"]}
                )
            else:
                sys.exit("Used unrecognized func:%s" % i.get("name"))
        return new_spec

    def normalize_spec(self):
        versions = ["1.0"]
        migrations = dict([("1.0", self.to_1_0)])
        index = (
            versions.index(self.data.get("version")) + 1
            if self.data.get("version") in versions
            else 0
        )
        for i in versions[index:]:
            self.data = migrations[i]()
        self.current_version = versions[-1]
        return self.data

    def pop_edition(self, user_edition):
        if float(self.current_version) < 1.0:
            raise ValueError("Current spec version doent support editions")
        for edition in self.data["editions"][:]:
            if edition.get("name") == user_edition:
                self.data["editions"] = [edition]
                break
        else:
            raise ValueError("setuped build edition is not present in spec file")

    # deprecated method. Needed for backward compatibility with old specs
    @staticmethod
    def except_var(config):
        tar_except = []
        for key, value in config.items():
            if "_dir" in key:
                tar_except.append(value)
        for key in config.get("processing", {}):
            if key.get("except_file", False):
                tar_except.append(key.get("file"))
        return tar_except

    def spec_processing(self, path: dict, workspace: str, release_version):
        for edition in self.data["editions"]:
            for operation in edition.get("preprocessors", ()):
                if operation["type"] == "script":
                    command = [operation["script"]]
                    if "args" in operation:
                        command.extend(operation["args"])
                    logging.info(
                        check_output(command, cwd=path[edition["name"]]).decode("utf-8")
                    )
                else:
                    if operation["type"] == "splitter":
                        params = {
                            "jinja_values": {
                                "edition": edition["name"],
                                "release_version": release_version,
                            }
                        }
                    else:
                        params = {}
                    get_type_func(operation["type"])(
                        path[edition["name"]], workspace, **params, **operation
                    )
