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
# pylint: disable=W0611, W0621, W0404, W0212, C1801
import coreapi
import requests

try:
    # pylint: disable=unused-import
    from pytest import allure  # noqa: F401
    # pylint: disable=unused-import
    import pytest
    IS_ALLURE = True
except ImportError:
    IS_ALLURE = False


class APINode():
    pass


class ADCMApiError(Exception):
    pass


class EnvHTTPTransport(coreapi.transports.HTTPTransport):
    """
    Fix the coreapi problem that prepared request do not read requests-related env variables
    See https://docs.python-requests.org/en/latest/user/advanced/#prepared-requests
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings = self._session.merge_environment_settings(None, {}, None, None, None)
        self._session.verify = settings["verify"]
        self._session.proxies = settings["proxies"]
        self._session.stream = settings["stream"]
        self._session.cert = settings["cert"]


class ADCMApiWrapper():
    """Thin wrapper over ADCM API with coreapi (search django rest framework)
    Quick start:

    api =  ADCMApiWrapper()
    api.auth(username='admin', password='admin')

    Following function are equal and returns OrderedDict with API response:
    api.action(['cluster', 'list'])
    api.objects.cluster.list()

    Create and remove object:
    cluster = api.objects.cluster.create(name="test")
    api.objects.cluster.delete(cluster_id=cluster['id'])
    """

    def _fabric_function(self, node, path=None):
        if path is None:
            path = []

        def result(**kvargs):
            return self.action(path, params=kvargs)

        return result

    def _fabric_function_allure(self, node, path=None):
        # pylint: disable=no-member
        if path is None:
            path = []

        @pytest.allure.step(path[-1].title() + ' ' + path[-2])
        def result(**kvargs):
            return self.action(path, params=kvargs)

        return result

    def _parse_schema(self, node, is_allure=False, path=None):
        if path is None:
            path = []

        result = APINode()
        for funcname in node.links.keys():
            if is_allure:
                func = self._fabric_function_allure(node.links[funcname], path + [funcname])
            else:
                func = self._fabric_function(node.links[funcname], path + [funcname])
            setattr(result, funcname, func)

        for subnodename in node.data.keys():
            setattr(result,
                    subnodename,
                    self._parse_schema(node.data[subnodename], is_allure, path + [subnodename]))
        return result

    def __init__(self, url):
        """
        Init class with ADCM url.

        Example:
        api = ADCMApiWrapper('http://127.0.0.1:8000')
        """
        self.api_url = "/api/v1/"
        self.url = url
        self.client = None
        self.schema = None
        self.objects = None
        self.api_token = None
        self.adcm_version = None

    def _check_for_error(self, data):
        if data is not None:
            if 'level' in data and data['level'] == 'error':
                raise ADCMApiError(data['code'], data['desc'])

    def auth(self, username, password):
        """Auth api client in ADCM and fetch schema"""

        result = requests.request(
            'POST', self.url + '/api/v1/token/',
            data={'username': username, 'password': password})
        token = result.json()
        self._check_for_error(token)
        self.api_token = token['token']
        auth = coreapi.auth.TokenAuthentication(
            scheme='Token',
            token=self.api_token
        )
        self.client = coreapi.Client(transports=[EnvHTTPTransport(auth=auth)])
        self.fetch()

    def fetch(self):
        """Fetch objects"""

        self.schema = self.client.get(f"{self.url}{self.api_url}schema/")
        self.objects = self._parse_schema(self.schema, is_allure=IS_ALLURE)
        try:
            self.adcm_version = self.objects.info.list()['adcm_version']
        except (KeyError, AttributeError):
            self.adcm_version = "0"

    def action(self, *args, **kwargs):
        """
        Do operation over api. For information see coreapi documentation.

        Example:
        api.action(['cluster', 'create'], name='testcluster')
        """

        # After parsing the schema, fields for a query, a form, or a path may appear that have
        # the same names, which may cause the field value to go to the wrong place.
        # Path fields take precedence over query and form fields, so if there are path fields
        # and query or form fields with the same name, we delete the query and form fields
        # with the given name.
        path = args[0]
        link = self.schema[path[0]]
        for item in path[1:]:
            link = link[item]

        fields = []
        path_fields = [field.name for field in link.fields if field.location == 'path']
        for field in link.fields:
            if not (field.location in ('query', 'form') and field.name in path_fields):
                fields.append(field)
        fields = tuple(fields)
        overrides = {'fields': fields}

        data = self.client.action(self.schema, *args, overrides=overrides, **kwargs)
        self._check_for_error(data)
        return data
