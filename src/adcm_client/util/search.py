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


from collections.abc import Mapping


class TooManyResult(Exception):
    pass


def search_one(data, **attrs):
    """Returns on element of data array that have the same attrs that in **attrs

    Data should be in form array of dictionary:

    data = [
        {
            attr1: attr1_value,
            attr2: attr2_value,
            ...
        },
        ...
    ]

    **attrs is a values to filter something

    search_one return one element from data if all **attrs equal to attrs
    from dict. It doesn't metter if len(**attrs) < len(element)

    search_one returns None if no result found

    search_one raises TooManyResult if more than one element in result
    """
    result = None
    for i in search(data, **attrs):
        if result is None:
            result = i
        else:
            # if we have one element in search generator than
            # we should not be here
            raise TooManyResult
    return result


def search(data, **attrs):
    """Return subset of data array with elements that have
    the same attrs that in **attrs

    Data should be in form array of dictionary:

    data = [
        {
            attr1: attr1_value,
            attr2: attr2_value,
            ...
        },
        ...
    ]

    **attrs is a values to filter something

    search return array of elements elements from data
    if all **attrs are equal to attrs of element.
    It doesn't metter if len(**attrs) < len(element)

    search returns None if no result found
    """

    # for backward compatibility
    if not attrs:
        return data

    def filter_data(x):
        new_attrs = {}
        new_data = {}
        for key, value in x.items():
            if not isinstance(value, (Mapping, list)):
                new_data[key] = value
                if key in attrs:
                    new_attrs[key] = attrs[key]

        result = []
        for k, v in new_attrs.items():
            if k in new_data and v == new_data[k]:
                result.append(True)
            else:
                result.append(False)
        if result:
            return all(result)
        return False

    return (item for item in data if filter_data(item))
