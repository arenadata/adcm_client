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
# pylint: disable=too-many-lines, too-many-public-methods, too-many-ancestors

import logging
import warnings
from collections import namedtuple
from io import BytesIO
from json import dumps
from typing import List, Union, Optional

from coreapi.exceptions import ErrorMessage
from version_utils import rpm

from adcm_client.base import (
    ADCMApiError,
    BaseAPIListObject,
    BaseAPIObject,
    ObjectNotFound,
    TooManyArguments,
    WaitTimeout,
    strip_none_keys,
    min_server_version,
    allure_step,
    allure_attach_json,
    allure_attach,
    legacy_server_implementaion,
    EndPoint,
    NoSuchEndpointOrAccessIsDenied,
)
from adcm_client.util import stream
from adcm_client.util.config import update
from adcm_client.wrappers.api import ADCMApiWrapper

# Init logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

Me = namedtuple(
    'Me',
    ('id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'password', 'profile'),
)


class NoCredentionsProvided(Exception):
    """There is no user/password provided. It was not passed as init parameters
    during ADCMClient initialization and was not passed as a parameter to auth()
    function
    """


##################################################
#                 B U N D L E S
##################################################
class IncorrectPrototypeType(Exception):
    pass


class Bundle(BaseAPIObject):
    """The 'Bundle' object from the API"""

    IDNAME = "bundle_id"
    PATH = ["stack", "bundle"]
    FILTERS = ["name", "version"]
    id = None
    bundle_id = None
    name = None
    description = None
    version = None
    edition = None

    def __repr__(self):
        return f"<Bundle {self.name} {self.version} {self.edition} at {id(self)}>"

    def provider_prototype(self) -> "ProviderPrototype":
        """Return ProviderPrototype object"""
        return self._child_obj(ProviderPrototype)

    def provider_create(self, name, description=None) -> "Provider":
        """Creates Provider object from the prototype"""
        try:
            prototype = self.provider_prototype()
        except ObjectNotFound:
            raise IncorrectPrototypeType from None
        return prototype.provider_create(name, description)

    def provider_list(self, paging=None, **args) -> "ProviderList":
        """Return list of 'Provider' objects"""
        try:
            prototype = self.provider_prototype()
        except ObjectNotFound:
            raise IncorrectPrototypeType from None
        return prototype.provider_list(paging=paging, **args)

    def provider(self, **args) -> "Provider":
        """Return 'Provider' object from the 'ProviderPrototype' object"""
        try:
            prototype = self.provider_prototype()
        except ObjectNotFound:
            raise IncorrectPrototypeType from None
        return prototype.provider(**args)

    def service_prototype(self, **args) -> "ServicePrototype":
        """Return 'ServicePrototype' object"""
        return self._child_obj(ServicePrototype, **args)

    def cluster_prototype(self) -> "ClusterPrototype":
        """Return 'ClusterPrototype' object"""
        return self._child_obj(ClusterPrototype)

    def cluster_create(self, name, description=None) -> "Cluster":
        """Creates 'Cluster' object from the 'ClusterPrototype' object"""
        try:
            prototype = self.cluster_prototype()
        except ObjectNotFound:
            raise IncorrectPrototypeType from None
        return prototype.cluster_create(name, description)

    def cluster_list(self, paging=None, **args) -> "ClusterList":
        """Return list of 'Cluster' objects"""
        try:
            prototype = self.cluster_prototype()
        except ObjectNotFound:
            raise IncorrectPrototypeType from None
        return prototype.cluster_list(paging=paging, **args)

    def cluster(self, **args) -> "Cluster":
        """Return 'Cluster' object from the 'ClusterPrototype' object"""
        try:
            prototype = self.cluster_prototype()
        except ObjectNotFound:
            raise IncorrectPrototypeType from None
        return prototype.cluster(**args)

    def license(self):
        """Provide endpoint to licence/read"""
        return self._subcall("license", "read")

    def license_accept(self):
        """Provide endpoint to licence/accept/update"""
        self._subcall("license", "accept", "update")


class BundleList(BaseAPIListObject):
    """List of 'Bundle' object from the API"""

    _ENTRY_CLASS = Bundle


##################################################
#              P R O T O T Y P E
##################################################
class Prototype(BaseAPIObject):
    """The 'Prototype' object from the API"""

    PATH = ["stack", "prototype"]
    IDNAME = "prototype_id"
    FILTERS = ["name", "bundle_id"]

    id = None
    prototype_id = None
    name = None
    display_name = None
    type = None
    description = None
    version = None
    bundle_id = None
    config = None
    actions = None
    url = None

    def bundle(self) -> "Bundle":
        """Return 'Bundle' object"""
        return self._parent_obj(Bundle)


class PrototypeList(BaseAPIListObject):
    """List of 'Prototype' object from the API"""

    _ENTRY_CLASS = Prototype


class ClusterPrototype(Prototype):
    """The 'ClusterPrototype' object from the API"""

    PATH = ["stack", "cluster"]
    FILTERS = ["name", "bundle_id"]

    def cluster_create(self, name, description=None) -> "Cluster":
        """Create 'Cluster' object with relevant parameters"""
        if self.type != 'cluster':
            raise IncorrectPrototypeType
        return new_cluster(
            self._api,
            prototype_id=self.prototype_id,
            name=name,
            description=description,
        )

    def cluster_list(self, paging=None, **args) -> "ClusterList":
        """Return list of 'Cluster' objects"""
        return self._child_obj(ClusterList, paging=paging, **args)

    def cluster(self, **args) -> "Cluster":
        """Return 'Cluster' object"""
        return self._child_obj(Cluster, **args)


class ClusterPrototypeList(BaseAPIListObject):
    """List of 'ClysterPrototype' object from the API"""

    _ENTRY_CLASS = ClusterPrototype


class ServicePrototype(Prototype):
    """The 'ServicePrototype' object from the API"""

    PATH = ["stack", "service"]
    FILTERS = ["name", "bundle_id"]

    shared = None
    display_name = None
    required = None
    components = None
    exports = None
    imports = None
    monitoring = None
    path = None
    bundle_edition = None

    @min_server_version('2020.09.25.13')
    def service_list(self, paging=None, **args) -> "ServiceList":
        """Return list of 'Service' objects and check its minimal version"""
        return self._child_obj(ServiceList, paging=paging, **args)

    @min_server_version('2020.09.25.13')
    def service(self, **args) -> "Service":
        """Return 'Service' object and check its minimal version"""
        return self._child_obj(Service, **args)


class ServicePrototypeList(BaseAPIListObject):
    """List of 'ServicePrototype' object from the API"""

    _ENTRY_CLASS = ServicePrototype


class ProviderPrototype(Prototype):
    """The 'ProvidePrototype' object from the API"""

    PATH = ["stack", "provider"]
    FILTERS = ["name", "bundle_id"]

    display_name = None
    required = None
    upgrade = None
    path = None
    bundle_edition = None
    license = None

    def provider_create(self, name, description=None) -> "Provider":
        """Create 'Provider' object with relevant parameters"""
        if self.type != 'provider':
            raise IncorrectPrototypeType
        return new_provider(
            self._api,
            prototype_id=self.prototype_id,
            name=name,
            description=description,
        )

    def provider_list(self, paging=None, **args) -> "ProviderList":
        """Return list of 'Provider' objects"""
        return self._child_obj(ProviderList, paging=paging, **args)

    def provider(self, **args) -> "Provider":
        """Return 'Provider' object"""
        return self._child_obj(Provider, **args)


class ProviderPrototypeList(BaseAPIListObject):
    """List of 'ProvidePrototype' object from the API"""

    _ENTRY_CLASS = ProviderPrototype


class HostPrototype(Prototype):
    """The 'HostPrototype' object from the API"""

    PATH = ["stack", "host"]
    FILTERS = ["name", "bundle_id"]

    display_name = None
    required = None
    monitoring = None
    path = None
    bundle_edition = None

    def host_list(self, paging=None, **args) -> "HostList":
        """Return list of 'Host' objects"""
        return self._child_obj(HostList, paging=paging, **args)

    def host(self, **args) -> "Host":
        """Return 'Host' object"""
        return self._child_obj(Host, **args)


class HostPrototypeList(BaseAPIListObject):
    """List of 'HostPrototype' objects from the API"""

    _ENTRY_CLASS = HostPrototype


##################################################
#           B A S E  O B J E C T
##################################################


def _config_set_diff(object_with_config, data: dict, attach_to_allure: bool = True) -> dict:
    """
    General method to use when config should be updated without passing the full config.

    :param object_with_config: Object with methods `config(..., full: bool) -> dict`
                               and `config_set(data, attach_to_allure, ...) -> dict`
    :param data: Dictionary with new config fields
                 (may or may not contain "config" and "attr" fields)
    :param attach_to_allure: Flag to decide whether attach
                             changed fields and original config or not
    """
    if attach_to_allure:
        allure_attach_json(data, name="Changed fields")
    if "attr" not in data:
        data = {"config": {**data.get("config", data)}, "attr": {}}
    config = object_with_config.config(full=True)
    if attach_to_allure:
        allure_attach_json(config, name="Original config")
    return object_with_config.config_set(update(config, data), attach_to_allure=attach_to_allure)


class _BaseObject(BaseAPIObject):
    """
    Base class 'BaseObject' for adcm_client objects
    """

    id = None
    url = None
    state = None
    prototype_id = None
    locked = None
    multi_state = None

    def prototype(self):
        """Return Error if method or function hasn't implemented in derived class"""
        raise NotImplementedError

    def action(self, **args) -> "Action":
        """Return 'Action' object"""
        return self._subobject(Action, **args)

    def action_list(self, paging=None, **args) -> "ActionList":
        """Return list of 'Action' objects"""
        return self._subobject(ActionList, paging=paging, **args)

    def action_run(self, **args) -> "Task":
        """Run action which returns 'Task' object"""
        warnings.warn(
            'Deprecated. The method accepts no arguments for the "action.run()" method.',
            DeprecationWarning,
            stacklevel=2,
        )
        action = self.action(**args)
        return action.run()

    def config(self, full=False):
        """Provide endpoint for config/current/list. If none current - returns config"""
        history_entry = self._subcall("config", "current", "list")
        if full:
            return history_entry
        return history_entry['config']

    def previous_config(self, full=False):
        """Provide endpoint for config/previous/list. Return last previous config if it exists"""
        previous = self._subcall("config", "previous", "list")
        if full:
            return previous
        return previous['config']

    def config_history(self, full=False):
        """Provide endpoint for config/history/list. Returns list of all previous configs"""
        history = self._subcall("config", "history", "list")
        if full:
            return history
        result = []
        for story in history:
            result.append(story['config'])
        return result

    @allure_step("Save config")
    def config_set(self, data, attach_to_allure=True):
        """Save completed config in history"""
        # this check is incomplete, cases of presence of keys "config" and "attr" in config
        # are not considered
        if attach_to_allure:
            allure_attach_json(data, name="Complete config")
        if "config" in data and "attr" in data:
            if data["attr"] is None:
                data["attr"] = {}
            history_entry = self._subcall(
                'config', 'history', 'create', config=data['config'], attr=data['attr']
            )
            return {key: value for key, value in history_entry.items() if key in ['config', 'attr']}
        history_entry = self._subcall('config', 'history', 'create', config=data)
        return history_entry['config']

    @allure_step("Save config")
    def config_set_diff(self, data, attach_to_allure=True):
        """Save the difference between old and new config in history"""
        return _config_set_diff(self, data, attach_to_allure)

    def config_prototype(self):
        return self.prototype().config

    def group_config(self) -> "GroupConfigList":
        return GroupConfigList(self._api, object_id=self.id, object_type=self.prototype().type)

    def group_config_create(self, name: str, description: str = '') -> "GroupConfig":
        return new_group_config(
            self._api,
            object_id=self.id,
            object_type=self.prototype().type,
            name=name,
            description=description,
        )

    @min_server_version('2021.07.16.09')
    def concerns(self):
        concern_list = ConcernList(self._api)
        data = []
        for concern in self._data['concerns']:
            data.append(Concern(api=self._api, id=concern['id']))
        concern_list.data = data
        return concern_list


##################################################
#              P R O V I D E R
##################################################
class Provider(_BaseObject):
    """The 'Provider' object from the API"""

    IDNAME = "provider_id"
    PATH = ["provider"]
    FILTERS = ["name", "prototype_id"]
    provider_id = None
    edition = None
    license = None
    name = None
    description = None
    bundle_id = None
    before_upgrade = None

    def __repr__(self):
        return f"<Provider {self.name} at {id(self)}>"

    def bundle(self) -> "Bundle":
        """Return 'Bundle' object"""
        return self._parent_obj(Bundle)

    def host_create(self, fqdn) -> "Host":
        """Create new 'Host' object includes information about FQDN"""
        return new_host(self._api, **self._merge(fqdn=fqdn))

    def host_list(self, paging=None, **args) -> "HostList":
        """Return list of 'Host' objects"""
        return self._child_obj(HostList, paging=paging, **args)

    def host(self, **args) -> "Host":
        """Return 'Host' object"""
        return self._child_obj(Host, **args)

    def prototype(self) -> "ProviderPrototype":
        """Return 'ProviderPrototype' object"""
        return self._parent_obj(ProviderPrototype)

    def upgrade(self, **args) -> "Upgrade":
        """Return 'Upgrade' object"""
        return self._subobject(Upgrade, **args)

    def upgrade_list(self, paging=None, **args) -> "UpgradeList":
        """Return list of 'Upgrade' objects"""
        return self._subobject(UpgradeList, paging=paging, **args)


class ProviderList(BaseAPIListObject):
    """List of 'Provider' objects from the API"""

    _ENTRY_CLASS = Provider


@allure_step('Create provider {name}')
def new_provider(api, **args) -> "Provider":
    """Create new 'Provider' object"""
    try:
        provider = api.objects.provider.create(**strip_none_keys(args))
    except AttributeError as error:
        raise NoSuchEndpointOrAccessIsDenied from error
    return Provider(api, provider_id=provider['id'])


##################################################
#              C L U S T E R
##################################################
class Cluster(_BaseObject):
    """The 'Cluster' object from the API"""

    IDNAME = "cluster_id"
    PATH = ["cluster"]
    FILTERS = ["name", "prototype_id"]
    cluster_id = None
    name = None
    description = None
    bundle_id = None
    serviceprototype = None
    status = None
    edition = None
    license = None
    before_upgrade = None

    def __repr__(self):
        return f"<Cluster {self.name} from bundle - {self.bundle_id} at {id(self)}>"

    def prototype(self) -> "ClusterPrototype":
        """Return 'ClusterPrototype' object as its prototype"""
        return self._parent_obj(ClusterPrototype)

    def _bind_old(self, target):
        """Check target type. If it is cluster or service - provide matching endpoint"""
        if isinstance(target, Cluster):
            self._subcall("bind", "create", export_cluster_id=target.cluster_id)
        elif isinstance(target, Service):
            self._subcall(
                "bind",
                "create",
                export_cluster_id=target.cluster_id,
                export_service_id=target.service_id,
            )
        else:
            raise NotImplementedError

    def _bind_list_old(self, paging=None):
        """Provide endpoint to bind/list"""
        return self._subcall("bind", "list")

    @legacy_server_implementaion(_bind_old, '2022.02.1.00')
    def bind(self, target) -> "Bind":
        """Create new Bind object and return it"""
        if isinstance(target, Cluster):
            self._subcall("bind", "create", export_cluster_id=target.cluster_id)
        elif isinstance(target, Service):
            self._subcall(
                "bind",
                "create",
                export_cluster_id=target.cluster_id,
                export_service_id=target.service_id,
            )
        return self._subobject(Bind)

    @legacy_server_implementaion(_bind_list_old, '2022.02.1.00')
    def bind_list(self, paging=None, **kwargs) -> "BindList":
        """Return list of 'Bind' objects"""
        return self._subobject(BindList, paging=paging, **kwargs)

    def bundle(self) -> "Bundle":
        """Return 'Bundle' object from Cluster prototype"""
        proto = self.prototype()
        return proto.bundle()

    def button(self):
        """Return Error if method or function hasn't implemented in derived class"""
        raise NotImplementedError

    def host(self, **args) -> "Host":
        """Return 'Host' object"""
        return self._child_obj(Host, **args)

    def host_list(self, paging=None, **args) -> "HostList":
        """Return list of 'Host' objects"""
        return self._child_obj(HostList, paging=paging, **args)

    def host_add(self, host: "Host") -> "Host":
        """Create and add new 'Host' object to Cluster"""
        with allure_step(f"Add host {host.fqdn} to cluster {self.name}"):
            data = self._subcall("host", "create", host_id=host.id)
            return Host(self._api, id=data['id'])

    def host_delete(self, host: "Host"):
        """Delete 'Host' from Cluster"""
        with allure_step(f"Remove host {host.fqdn} from cluster {self.name}"):
            self._subcall("host", "delete", host_id=host.id)

    def _service_old(self, **args) -> "Service":
        """Return 'Service' object"""
        return self._subobject(Service, **args)

    # !!! If you change the version, do not forget to change it in the __new__ method
    # of the Service class as well as in the comments to them
    @legacy_server_implementaion(_service_old, '2020.09.25.13')
    def service(self, **args) -> "Service":
        """Return 'Service' object and check last version of service"""
        return self._child_obj(Service, **args)

    def _service_list_old(self, paging=None, **args) -> "ServiceList":
        """Return list of 'Service' objects"""
        return self._subobject(ServiceList, paging=paging, **args)

    # !!! If you change the version, do not forget to change it in the __new__ method
    # of the Service class as well as in the comments to them
    @legacy_server_implementaion(_service_list_old, '2020.09.25.13')
    def service_list(self, paging=None, **args) -> "ServiceList":
        """Return list of 'Service' objects"""
        return self._child_obj(ServiceList, paging=paging, **args)

    def _service_add_old(self, **args) -> "Service":
        """Add existed Service from prototype to cluster, return 'Service' object"""
        proto = self.bundle().service_prototype(**args)
        with allure_step(f"Add service {proto.name} to cluster {self.name}"):
            data = self._subcall("service", "create", prototype_id=proto.id)
            return self._subobject(Service, service_id=data['id'])

    # !!! If you change the version, do not forget to change it in the __new__ method
    # of the Service class as well as in the comments to them
    @legacy_server_implementaion(_service_add_old, '2020.09.25.13')
    def service_add(self, **args) -> "Service":
        """Add new Service from prototype to cluster, return 'Service' object"""
        proto = self.bundle().service_prototype(**args)
        with allure_step(f"Add service {proto.name} to cluster {self.name}"):
            data = self._subcall("service", "create", prototype_id=proto.id, cluster_id=self.id)
            return Service(self._api, id=data['id'])

    @min_server_version('2020.05.13.00')
    def service_delete(self, service: "Service"):
        """Delete service from cluster"""
        with allure_step(f"Remove service {service.name} from cluster {self.name}"):
            self._subcall("service", "delete", service_id=service.id)

    def hostcomponent(self):
        """Provide endpoint to hostcomponent/list"""
        return self._subcall("hostcomponent", "list")

    @allure_step("Save hostcomponents map")
    def hostcomponent_set(self, *hostcomponents):
        """Add readable and complete host components to JSON"""
        hc = []
        readable_hc = []
        for i in hostcomponents:
            h, c = i
            hc.append({'host_id': h.id, 'service_id': c.service_id, 'component_id': c.id})
            readable_hc.append({'host_fqdn': h.fqdn, 'component_name': c.display_name})
        allure_attach_json(readable_hc, name="Readable hc map")
        allure_attach_json(hc, name="Complete hc map")
        return self._subcall("hostcomponent", "create", hc=hc)

    def status_url(self):
        """Provide endpoint to status/list"""
        return self._subcall("status", "list")

    def imports(self):
        """Provide endpoint to import/list"""
        return self._subcall("import", "list")

    def upgrade(self, **args) -> "Upgrade":
        """Return 'Upgrade' object"""
        return self._subobject(Upgrade, **args)

    def upgrade_list(self, paging=None, **args) -> "UpgradeList":
        """Return list of 'Upgrade' objects"""
        return self._subobject(UpgradeList, paging=paging, **args)


class ClusterList(BaseAPIListObject):
    """List of 'HostPrototype' objects from the API"""

    _ENTRY_CLASS = Cluster


@allure_step('Create cluster {name}')
def new_cluster(api: ADCMApiWrapper, **args) -> "Cluster":
    """Create new 'Cluster' object"""
    try:
        cluster = api.objects.cluster.create(**strip_none_keys(args))
    except AttributeError as error:
        raise NoSuchEndpointOrAccessIsDenied from error
    return Cluster(api, cluster_id=cluster['id'])


##################################################
#          U P G R A D E
##################################################
class Upgrade(BaseAPIObject):
    """The 'Upgrade' object from the API"""

    IDNAME = "upgrade_id"
    PATH = None
    SUBPATH = ["upgrade"]

    id = None
    upgrade_id = None
    bundle_id = None
    license_url = None
    url = None
    name = None
    description = None
    min_version = None
    max_version = None
    min_strict = None
    max_strict = None
    state_available = None
    state_on_success = None
    from_edition = None
    ui_options = None
    config = None

    def do(self, **args) -> Optional['Task']:
        """
        Do upgrade and provide do/create endpoint.
        Returns a task if an action was fired on the upgrade, or None otherwise

        :param args: config - configuration for action
        :type args: dict
        :return: task
        :rtype: Optional[Task]
        """
        with allure_step(f"Do upgrade {self.name}"):
            data = self._subcall("do", "create", **args)
        task = None
        if data.get('task_id') is not None:
            task = Task(self._api, task_id=data['task_id'])
        return task


class UpgradeList(BaseAPIListObject):
    """List of 'Upgrade' objects from the API"""

    SUBPATH = ["upgrade"]
    _ENTRY_CLASS = Upgrade


##################################################
#                B I N D
##################################################


class Bind(BaseAPIObject):
    """The 'Bind' object from the API"""

    IDNAME = "bind_id"
    PATH = None
    SUBPATH = ["bind"]

    id = None
    bind_id = None
    export_cluster_id = None
    export_cluster_name = None
    export_cluster_prototype_name = None
    export_service_id = None
    export_service_name = None
    import_service_id = None
    import_service_name = None

    def delete(self):
        with allure_step(f"Remove bind {self.bind_id}"):
            self._subcall("delete", bind_id=self.id)


class BindList(BaseAPIListObject):
    """List of 'Bind' objects from the API"""

    SUBPATH = ["bind"]
    _ENTRY_CLASS = Bind


##################################################
#           S E R V I C E S
##################################################
class Service(_BaseObject):
    """The 'Service' object from the API"""

    IDNAME = "service_id"
    PATH = ['service']
    SUBPATH = ['service']
    FILTERS = ['cluster_id']

    id = None
    service_id = None
    bundle_id = None
    name = None
    description = None
    display_name = None
    cluster_id = None
    status = None
    monitoring = None

    def __new__(cls, *args, **kwargs):
        """
        Set PATH=None, if adcm version < `2020.09.25.13`. See ADCM-1439.
        This method is associated with the action of the `legacy_server_implementaion()` decorator.
        """
        wrapper = args[0]
        instance = super().__new__(cls)
        # !!! If you change the version, do not forget to change it in the service(), service_list()
        # and service_add() methods of the Cluster class as well as in the comments to them
        if rpm.compare_versions(wrapper.adcm_version, '2020.09.25.13') < 0:
            instance.PATH = None
        return instance

    def __repr__(self):
        return f"<Service {self.name} form cluster - {self.cluster_id} at {id(self)}>"

    def _bind_old(self, target):
        """Check target type. If it is cluster or service - provide matching endpoint"""
        if isinstance(target, Cluster):
            self._subcall("bind", "create", export_cluster_id=target.cluster_id)
        elif isinstance(target, Service):
            self._subcall(
                "bind",
                "create",
                export_cluster_id=target.cluster_id,
                export_service_id=target.service_id,
            )
        else:
            raise NotImplementedError

    def _bind_list_old(self, paging=None):
        """Provide endpoint bind/list"""
        return self._subcall("bind", "list")

    @legacy_server_implementaion(_bind_old, '2022.02.1.00')
    def bind(self, target) -> "Bind":
        """Create new Bind object and return it"""
        if isinstance(target, Cluster):
            self._subcall("bind", "create", export_cluster_id=target.cluster_id)
        elif isinstance(target, Service):
            self._subcall(
                "bind",
                "create",
                export_cluster_id=target.cluster_id,
                export_service_id=target.service_id,
            )
        return self._subobject(Bind)

    @legacy_server_implementaion(_bind_list_old, '2022.02.1.00')
    def bind_list(self, paging=None, **kwargs) -> "BindList":
        """Return list of 'Bind' objects"""
        return self._subobject(BindList, paging=paging, **kwargs)

    def prototype(self) -> "ServicePrototype":
        """Return new 'ServicePrototype' object"""
        return ServicePrototype(self._api, id=self.prototype_id)

    def cluster(self) -> Cluster:
        """Return 'Cluster' object"""
        return Cluster(self._api, id=self.cluster_id)

    def imports(self):
        """Provide endpoint to import/list"""
        return self._subcall("import", "list")

    def _component_old(self, **args) -> "Component":
        """Return 'Component' object"""
        return self._subobject(Component, **args)

    # Set a real version when components feature will be merged into develop
    # https://github.com/arenadata/adcm/pull/778
    # !!! If you change the version, do not forget to change it in the __new__ method
    # of the Component class as well as in the comments to them
    @legacy_server_implementaion(_component_old, '2021.03.12.16')
    def component(self, **args) -> "Component":
        """
        Return 'Component' object according to the version
        (Return old version of func if version is older)
        """
        return self._child_obj(Component, **args)

    def _component_list_old(self, paging=None, **args) -> "ComponentList":
        """Return list of 'Component' objects"""
        return self._subobject(ComponentList, paging=paging, **args)

    # Set a real version when components feature will be merged into develop
    # https://github.com/arenadata/adcm/pull/778
    # !!! If you change the version, do not forget to change it in the __new__ method
    # of the Component class as well as in the comments to them
    @legacy_server_implementaion(_component_list_old, '2021.03.12.16')
    def component_list(self, paging=None, **args) -> "ComponentList":
        """
        Return list of 'Component' object according to the version
        (Return old version of func if version is older)
        """
        return self._child_obj(ComponentList, paging=paging, **args)


class ServiceList(BaseAPIListObject):
    """List of 'Service' objects from the API"""

    PATH = ['service']
    SUBPATH = ['service']
    _ENTRY_CLASS = Service

    def __new__(cls, *args, **kwargs):
        """
        Set PATH=None, if adcm version < `2020.09.25.13`. See ADCM-1439.
        This method is associated with the action of the `legacy_server_implementaion()` decorator.
        """
        wrapper = args[0]
        instance = super().__new__(cls)
        # !!! If you change the version, do not forget to change it in the service(), service_list()
        # and service_add() methods of the Cluster class as well as in the comments to them
        if rpm.compare_versions(wrapper.adcm_version, '2020.09.25.13') < 0:
            instance.PATH = None
        return instance


##################################################
#           C O M P O N E N T S
##################################################
class Component(_BaseObject):
    """The 'Component' object from the API"""

    IDNAME = "component_id"
    PATH = ["component"]
    SUBPATH = ["component"]
    FILTERS = ["service_id"]

    id = None
    component_id = None
    cluster_id = None
    _service_id = None
    name = None
    display_name = None
    description = None
    constraint = None
    prototype_id = None
    requires = None
    bound_to = None
    monitoring = None
    status = None
    state = None

    def __new__(cls, *args, **kwargs):
        """
        Set PATH=None, if adcm version < `2021.03.12.16`. See ADCM-1439.
        This method is associated with the action of the `legacy_server_implementaion()` decorator.
        """
        wrapper = args[0]
        instance = super().__new__(cls)
        # !!! If you change the version, do not forget to change it in the component()
        # and component_list() methods of the Service class as well as in the comments to them
        if rpm.compare_versions(wrapper.adcm_version, '2021.03.12.16') < 0:
            instance.PATH = None
        return instance

    def prototype(self) -> "Prototype":
        return Prototype(self._api, prototype_id=self.prototype_id)

    @property
    def service_id(self):
        """Return {service_id} if it isn't None"""
        # this code is for backward compatibility
        if self._service_id is not None:
            return self._service_id
        try:
            return self._endpoint.path_args["service_id"]
        except KeyError:
            return self._data['service_id']

    @service_id.setter
    def service_id(self, value):
        """Set service_id as {value}"""
        self._service_id = value


class ComponentList(BaseAPIListObject):
    """List of 'Component' objects from the API"""

    PATH = ["component"]
    SUBPATH = ["component"]
    _ENTRY_CLASS = Component

    def __new__(cls, *args, **kwargs):
        """
        Set PATH=None, if adcm version < `2021.03.12.16`. See ADCM-1439.
        This method is associated with the action of the `legacy_server_implementaion()` decorator.
        """
        wrapper = args[0]
        instance = super().__new__(cls)
        # !!! If you change the version, do not forget to change it in the component()
        # and component_list() methods of the Service class as well as in the comments to them
        if rpm.compare_versions(wrapper.adcm_version, '2021.03.12.16') < 0:
            instance.PATH = None
        return instance


##################################################
#              H O S T
##################################################
class Host(_BaseObject):
    """The 'Host' object from the API"""

    IDNAME = "host_id"
    PATH = ["host"]
    SUBPATH = ["host"]
    FILTERS = ["fqdn", "prototype_id", "provider_id", "cluster_id"]

    id = None
    host_id = None
    fqdn = None
    provider_id = None
    cluster_id = None
    description = None
    bundle_id = None
    status = None
    maintenance_mode: str = None

    def maintenance_mode_set(self, value: str) -> None:
        self._api.objects.host.partial_update(host_id=self.id, maintenance_mode=value)
        self.reread()

    def __repr__(self):
        return f"<Host {self.fqdn} form provider - {self.provider_id} at {id(self)}>"

    def provider(self) -> "Provider":
        """Return 'Provider' object"""
        return self._parent_obj(Provider)

    def cluster(self) -> "Cluster":
        """Return 'Cluster' object"""
        if self.cluster_id is None:
            return None
        return self._parent_obj(Cluster)

    def bundle(self) -> "Bundle":
        """Return 'Bundle' object"""
        return self._parent_obj(Bundle)

    def prototype(self) -> "HostPrototype":
        """Return 'HostPrototype' object"""
        return self._parent_obj(HostPrototype)

    def group_config(self) -> "GroupConfigList":
        raise NotImplementedError

    def group_config_create(self, name: str, description: str = '') -> "GroupConfig":
        raise NotImplementedError


class HostList(BaseAPIListObject):
    """List of 'Host' objects from the API"""

    _ENTRY_CLASS = Host
    SUBPATH = ["host"]


@allure_step('Create host {fqdn}')
def new_host(api, **args) -> "Host":
    """Create new 'Host' object and return it"""
    try:
        host = api.objects.provider.host.create(**args)
    except AttributeError as error:
        raise NoSuchEndpointOrAccessIsDenied from error
    return Host(api, host_id=host['id'])


##################################################
#              A C T I O N
##################################################
class Action(BaseAPIObject):
    """The 'Action' object from the API"""

    IDNAME = "action_id"
    PATH = None
    SUBPATH = ["action"]
    FILTERS = ["name"]

    action_id = None
    button = None
    id = None
    name = None
    display_name = None
    description = None
    params = None
    prototype_id = None
    hostcomponentmap = None
    script = None
    script_type = None
    state_available = None
    state_unavailable = None
    multi_state_available = None
    multi_state_unavailable = None
    state_on_fail = None
    state_on_success = None
    type = None
    subs = None
    config = None
    ui_options = None
    allow_to_terminate = None
    partial_execution = None
    host_action = None
    disabling_cause = None

    def __repr__(self):
        return f"<Action {self.name} at {id(self)}>"

    def _get_config(self):
        config = {}
        for item in self.config['config']:
            if item['type'] == 'group':
                config[item['name']] = {}
            elif item['subname']:
                config[item['name']][item['subname']] = item['value']
            else:
                config[item['name']] = item['value']
        return config

    def log_files(self):
        raise NotImplementedError

    def task(self, **args) -> "Task":
        """Return 'Task' object"""
        return self._child_obj(Task, **args)

    def task_list(self, **args) -> "TaskList":
        """Return 'TaskList' object"""
        return self._child_obj(TaskList, **args)

    def run(self, **args) -> "Task":  # pylint: disable=too-many-branches
        attach_to_allure = args.pop("attach_to_allure", True)
        with allure_step(f"Run action {self.name}"):

            if 'hc' in args and attach_to_allure:
                allure_attach_json(args.get('hc'), name="Hostcomponent map")

            if 'config' in args and 'config_diff' in args:
                raise TypeError("only one argument is expected 'config' or 'config_diff'")

            if 'config' not in args:
                args['config'] = self._get_config()

                if 'config_diff' in args:
                    config_diff = args.pop('config_diff')
                    if attach_to_allure:
                        allure_attach_json(config_diff, name="Action config")
                    if 'config' in config_diff and 'attr' in config_diff:
                        args['attr'] = {}
                        for item in self.config["attr"]:
                            args['attr'][item] = (
                                config_diff['attr'].get(item) or self.config['attr'][item]
                            )
                        config_diff = config_diff['config']
                    for item in self.config['config']:
                        if item['type'] == 'group':
                            continue

                        key, subkey = item['name'], item['subname']
                        if subkey and subkey in config_diff.get(key, {}):
                            args['config'][key][subkey] = config_diff[key][subkey]
                        elif not subkey and key in config_diff:
                            args['config'][key] = config_diff[key]
            # check backward compatibility for `verbose` option
            if rpm.compare_versions(self.adcm_version, '2021.02.04.13') >= 0:
                args.setdefault('verbose', False)
            elif 'verbose' in args:
                warnings.warn(
                    f"ADCM {self.adcm_version} doesn't support action "
                    f"argument 'verbose'. It will be skipped"
                )
                args.pop('verbose')
            data = self._subcall("run", "create", **args)
            return Task(self._api, task_id=data["id"])


class ActionList(BaseAPIListObject):
    """List of 'Action' objects from the API"""

    SUBPATH = ["action"]
    _ENTRY_CLASS = Action


##################################################
#              T A S K
##################################################
class TaskFailed(Exception):
    pass


TASK_PARENT = {
    'cluster': Cluster,
    'service': Service,
    'host': Host,
    'provider': Provider,
    'component': Component,
}


class Task(BaseAPIObject):
    """The 'Task' object from the API"""

    IDNAME = "task_id"
    PATH = ["task"]
    FILTERS = ['action_id', 'pid', 'status', 'start_date', 'finish_date']
    _END_STATUSES = ["failed", "success"]
    action_id = None
    config = None
    hostcomponentmap = None
    task_id = None
    id = None
    jobs = None
    pid = None
    selector = None
    status = None
    url = None
    object_id = None
    object_type = None

    @min_server_version('2020.08.27.00')
    def action(self) -> "Action":
        # for component object method will work after version `2021.03.12.16`
        kwargs = {f'{self.object_type}_id': self.object_id}
        return TASK_PARENT[self.object_type](self._api, **kwargs).action(action_id=self.action_id)

    def __repr__(self):
        return f"<Task {self.task_id} at {id(self)}>"

    def job(self, **args) -> "Job":
        """Return 'Job' object"""
        return Job(self._api, task_id=self.id, **args)

    def job_list(self, paging=None, **args) -> "JobList":
        """Return list of 'Job' objects"""
        return JobList(self._api, paging=paging, task_id=self.id, **args)

    @allure_step("Wait for task end")
    def wait(self, timeout=None, log_failed=True):
        try:
            status = self.wait_for_attr("status", self._END_STATUSES, timeout=timeout)
            if log_failed and status == "failed":
                self._log_jobs(status=status)
        except WaitTimeout as e:
            if log_failed:
                self._log_jobs()
            raise WaitTimeout from e
        return status

    @allure_step("Wait for the task to success")
    def try_wait(self, timeout=None):
        status = self.wait(timeout=timeout)

        if status == "failed":
            raise TaskFailed

        return status

    def _log_jobs(self, **filters):
        for job in self.job_list(**filters):
            log_func = logger.error if job.status == "failed" else logger.info
            try:
                action_name = self.action().name
            except ErrorMessage:
                action = EndPoint(self._api, 'action_id', ['stack', 'action']).read(self.action_id)
                action_name = action['name']
            log_func("Action: %s", action_name)
            for file in job.log_files:
                try:
                    response = self._api.client.get(file["url"])
                except ErrorMessage as error:
                    # pylint: disable=protected-access
                    if error.error._data['code'] == 'LOG_NOT_FOUND':
                        # pylint: enable=protected-access
                        continue
                    raise error
                content_format = response.get("format", "txt")
                if "type" in response:
                    log_func("Type: %s", response['type'])
                if "content" in response:
                    if content_format == "json":
                        log_func(dumps(response["content"], indent=2))
                    else:
                        log_func(response["content"])


class TaskList(BaseAPIListObject):
    """List of 'Task' objects from the API"""

    _ENTRY_CLASS = Task


##################################################
#              L O G
##################################################
class Log(BaseAPIObject):
    """The 'Log' object from the API"""

    IDNAME = 'log_id'
    PATH = ['job', 'log']
    SUBPATH = ['log']
    id = None
    name = None
    type = None
    format = None
    content = None


class LogList(BaseAPIListObject):
    """List of 'Log' objects from the API"""

    _ENTRY_CLASS = Log
    SUBPATH = ["log"]


##################################################
#              J O B
##################################################
class Job(BaseAPIObject):
    """The 'Job' object from the API"""

    IDNAME = "job_id"
    PATH = ["job"]
    FILTERS = ['action_id', 'task_id', 'pid', 'status', 'start_date', 'finish_date']
    _END_STATUSES = ["failed", "success"]
    _WAIT_INTERVAL = 0.2
    id = None
    job_id = None
    pid = None
    status = None
    url = None
    log_files = None
    task_id = None
    display_name = None
    start_date = None
    finish_date = None

    def __repr__(self):
        return f"<Job {self.job_id} at {id(self)}>"

    def task(self) -> "Task":
        """Return 'Task' object"""
        return self._parent_obj(Task)

    def wait(self, timeout=None):
        """Wait for the time ={timeout}"""
        return self.wait_for_attr("status", self._END_STATUSES, timeout=timeout)

    def log(self, **kwargs) -> "Log":
        """Return 'Log' object"""
        return self._subobject(Log, **kwargs)

    def log_list(self, paging=None, **kwargs) -> "LogList":
        """Return list of 'Log' objects"""
        return self._subobject(LogList, paging=paging, **kwargs)


class JobList(BaseAPIListObject):
    """List of 'Job' objects from the API"""

    _ENTRY_CLASS = Job


##################################################
#              GROUP CONFIG
##################################################
class GroupConfig(BaseAPIObject):
    IDNAME = 'id'
    PATH = ['group-config']
    FILTERS = ['object_id', 'object_type']
    id = None
    object_id = None
    object_type = None
    config_id = None
    name = None
    description = None

    def hosts(self, paging=None, **kwargs) -> "HostList":
        return HostList(
            api=self._api,
            path=self.PATH + HostList.SUBPATH,
            path_args={'parent_lookup_group_config': self.id},
            paging=paging,
            **kwargs,
        )

    def host_add(self, host: "Host") -> "Host":
        with allure_step(f'Add host {host.fqdn} to group config {self.name}'):
            path = ("host", "create")
            args = {"parent_lookup_group_config": self.id, "id": host.id}
            data = self._sub_call(*path, **args)
            return Host(self._api, id=data['id'])

    def host_delete(self, host: "Host"):
        with allure_step(f'Remove host {host.fqdn} from group config {self.name}'):
            path = ("host", "delete")
            args = {"parent_lookup_group_config": self.id, "host_id": host.id}
            self._sub_call(*path, **args)

    def _get_object_config(self):
        """Return 'ObjectConfig' for group"""
        path = ("config", "read")
        args = {"parent_lookup_group_config": self.id, "id": self.config_id}
        return self._sub_call(*path, **args)

    def config(self, full=False):
        object_config = self._get_object_config()
        current_id = object_config.get("current_id")
        path = ("config", "config-log", "read")
        args = {
            "parent_lookup_obj_ref__group_config": self.id,
            "parent_lookup_obj_ref": self.config_id,
            "id": current_id,
        }
        current_config = self._sub_call(*path, **args)
        if full:
            return current_config
        return current_config["config"]

    @allure_step("Save group config")
    def config_set(self, data, attach_to_allure=True):
        """Save completed config in history"""
        # this check is incomplete, cases of presence of keys "config" and "attr" in config
        # are not considered
        if attach_to_allure:
            allure_attach_json(data, name="Complete group config")
        path = ("config", "config-log", "create")
        args = {
            "parent_lookup_obj_ref__group_config": self.id,
            "parent_lookup_obj_ref": self.config_id,
        }
        if "config" in data and "attr" in data:
            if data["attr"] is None:
                data["attr"] = {}
            args.update({"config": data["config"], "attr": data["attr"]})
            current_config = self._sub_call(*path, **args)
            return {
                key: value for key, value in current_config.items() if key in ["config", "attr"]
            }
        args.update({"config": data})
        current_config = self._sub_call(*path, **args)
        return current_config["config"]

    @allure_step("Save group config")
    def config_set_diff(self, data: dict, attach_to_allure: bool = True) -> dict:
        """Partial config update"""
        return _config_set_diff(self, data, attach_to_allure)

    def host_candidate(self, paging=None, **kwargs) -> "HostList":
        return HostList(
            api=self._api,
            path=self.PATH + ['host-candidate'],
            path_args={'parent_lookup_group_config': self.id},
            paging=paging,
            **kwargs,
        )


class GroupConfigList(BaseAPIListObject):
    """List of 'GroupConfig' objects from the API"""

    _ENTRY_CLASS = GroupConfig


@allure_step('Create group config {name}')
def new_group_config(api, **args) -> "GroupConfig":
    """Create new 'GroupConfig' and return it"""
    endpoint = getattr(api.objects, 'group-config')
    try:
        group = endpoint.create(**args)
    except AttributeError as error:
        raise NoSuchEndpointOrAccessIsDenied from error
    return GroupConfig(api, id=group['id'])


##################################################
#              A D C M
##################################################
class ADCM(_BaseObject):
    IDNAME = "adcm_id"
    PATH = ["adcm"]
    id = None
    name = None
    prototype_id = None
    url = None
    prototype_version = None
    bundle_id = None

    def prototype(self) -> "Prototype":
        """Return 'Prototype' object with id={prototype_id}"""
        return Prototype(self._api, id=self.prototype_id)

    def group_config(self) -> "GroupConfigList":
        raise NotImplementedError

    def group_config_create(self, name: str, description: str = '') -> "GroupConfig":
        raise NotImplementedError


class Concern(BaseAPIObject):
    IDNAME = 'concern_id'
    PATH = ['concern']
    id = None
    type = None
    blocking = None
    name = None
    reason = None
    url = None

    def related_objects(self):
        objects = {
            'cluster': Cluster,
            'service': Service,
            'component': Component,
            'provider': Provider,
            'host': Host,
            'adcm': ADCM,
        }
        data = []
        for related_object in self._data['related_objects']:
            object_type = related_object['type']
            object_id = related_object['id']
            data.append(objects[object_type](self._api, id=object_id))
        return data


class ConcernList(BaseAPIListObject):
    _ENTRY_CLASS = Concern


##################################################
#              U S E R
##################################################
class User(BaseAPIObject):
    IDNAME = 'id'
    PATH = ['rbac', 'user']
    FILTERS = ['id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'group']
    id = None
    username = None
    first_name = None
    last_name = None
    email = None
    is_superuser = None
    password = None
    profile = None

    def group_list(self) -> "GroupList":
        """Return list of `Group` object"""
        # TODO: I can't do this, because search() is not working
        # return GroupList(self._api, user=self.id)
        groups = GroupList(self._api)
        data = []
        for group in self._data['group']:
            data.append(Group(self._api, id=group['id']))
        groups.data = data
        return groups

    def change_password(self, password: str) -> None:
        """Changing user password"""
        try:
            self._api.objects.rbac.user.partial_update(id=self.id, password=password)
        except AttributeError as error:
            raise NoSuchEndpointOrAccessIsDenied from error
        self.reread()


class UserList(BaseAPIListObject):
    """List of `User` objects"""

    _ENTRY_CLASS = User


@allure_step('Create user {username}')
def new_user(api: ADCMApiWrapper, username: str, password: str, **kwargs):
    """Create new `User` object"""
    try:
        user = api.objects.rbac.user.create(
            username=username, password=password, **strip_none_keys(kwargs)
        )
    except AttributeError as error:
        raise NoSuchEndpointOrAccessIsDenied from error
    return User(api, id=user['id'])


##################################################
#              G R O U P
##################################################
class Group(BaseAPIObject):
    IDNAME = 'id'
    PATH = ['rbac', 'group']
    FILTERS = ['id', 'name', 'group']
    id = None
    name = None
    description = None

    def user_list(self) -> "UserList":
        # TODO: I can't do this, because search() is not working
        # return UserList(self._api, group=self.id)
        users = UserList(self._api)
        data = []
        for user in self._data['user']:
            data.append(User(self._api, id=user['id']))
        users.data = data
        return users

    def add_user(self, user: User) -> None:
        """Adding a user to a group"""
        current_users = self.user_list()
        users = [{'id': obj.id} for obj in current_users]
        users.append({'id': user.id})
        try:
            self._api.objects.rbac.group.partial_update(id=self.id, user=users)
        except AttributeError as error:
            raise NoSuchEndpointOrAccessIsDenied from error
        user.reread()
        self.reread()


class GroupList(BaseAPIListObject):
    _ENTRY_CLASS = Group


@allure_step('Create group {name}')
def new_group(api: ADCMApiWrapper, name: str, **kwargs):
    """Create new `Group` object"""
    try:
        group = api.objects.rbac.group.create(name=name, **strip_none_keys(kwargs))
    except AttributeError as error:
        raise NoSuchEndpointOrAccessIsDenied from error
    return Group(api, id=group['id'])


##################################################
#              R O L E
##################################################
class Role(BaseAPIObject):
    IDNAME = 'id'
    PATH = ['rbac', 'role']
    FILTERS = ['id', 'name', 'display_name', 'built_in', 'type', 'child']
    id = None
    name = None
    display_name = None
    description = None
    built_in = None
    type = None
    category = None
    parametrized_by_type = None

    def child_list(self) -> "RoleList":
        # TODO: I can't do this, because search() is not working
        # return RoleList(self._api, child=self.id)
        roles = RoleList(self._api)
        data = []
        for role in self._data['child']:
            data.append(Role(self._api, id=role['id']))
        roles.data = data
        return roles


class RoleList(BaseAPIListObject):
    _ENTRY_CLASS = Role


@allure_step('Create role {name}')
def new_role(api: ADCMApiWrapper, name: str, **kwargs):
    """Create new `Role` object"""
    try:
        role = api.objects.rbac.role.create(name=name, **strip_none_keys(kwargs))
    except AttributeError as error:
        raise NoSuchEndpointOrAccessIsDenied from error
    return Role(api, id=role['id'])


##################################################
#              P O L I C Y
##################################################
class Policy(BaseAPIObject):
    IDNAME = 'id'
    PATH = ['rbac', 'policy']
    FILTERS = ['id', 'name', 'built_in', 'role', 'user', 'group']
    id = None
    name = None
    built_in = None

    def object_list(self) -> "List[Union[Cluster, Service, Component, Provider, Host]]":
        data = []
        for obj in self._data['object']:
            data.append(TASK_PARENT[obj['type']](self._api, id=obj['id']))
        return data

    def role(self) -> "Role":
        return Role(self._api, id=self._data['role']['id'])

    def user_list(self) -> "UserList":
        users = UserList(self._api)
        data = []
        for user in self._data['user']:
            data.append(User(self._api, id=user['id']))
        users.data = data
        return users

    def group_list(self) -> "GroupList":
        groups = GroupList(self._api)
        data = []
        for group in self._data['group']:
            data.append(Group(self._api, id=group['id']))
        groups.data = data
        return groups


class PolicyList(BaseAPIListObject):
    _ENTRY_CLASS = Policy


@allure_step('Create policy {name}')
def new_policy(
    api: ADCMApiWrapper,
    name: str,
    role: Role,
    user: UserList,
    group: GroupList = None,
    objects: List[Union[Cluster, Service, Component, Provider, Host]] = None,
):
    users = [{'id': obj.id} for obj in user]
    groups = [{'id': obj.id} for obj in group or []]
    objects = [{'id': obj.id, 'type': obj.prototype().type} for obj in objects or []]
    try:
        policy = api.objects.rbac.policy.create(
            name=name, role={'id': role.id}, user=users, group=groups, object=objects
        )
    except AttributeError as error:
        raise NoSuchEndpointOrAccessIsDenied from error
    return Policy(api, id=policy['id'])


##################################################
#              C L I E N T
##################################################
class ADCMClient:
    _MIN_VERSION = "2019.02.20.00"

    def __init__(self, api=None, url=None, user=None, password=None):
        if api is not None:
            self._api = api
            self.url = api.url
            if self.api_token() is None:
                self.auth(user, password)
        else:
            self.url = url
            self._api = ADCMApiWrapper(self.url)
            self.auth(user, password)

        if self.api_token() is not None and user == 'admin':
            self.guess_adcm_url()

        self.adcm_version = self._api.adcm_version
        self._check_min_version()

    def __repr__(self):
        return f"<ADCM API Client for {self.url} at {id(self)}>"

    @allure_step("Login to ADCM API with user={user} and password={password}")
    def auth(self, user=None, password=None):
        """Login to ADCM API with user={user} and password={password}"""
        if user is None or password is None:
            raise NoCredentionsProvided
        self._api.auth(user, password)
        if self.api_token() is None:
            raise ADCMApiError("Incorrect user/password. Unable to auth.")
        self._check_min_version()

    def reread(self):
        self._api.fetch()
        self.adcm_version = self._api.adcm_version

    def reset(self, api=None, url=None, user=None, password=None):
        """Re-init object. Useful in tests"""
        self.__init__(api=api, url=url, user=user, password=password)

    def _check_min_version(self):
        """Check client version and provide information about newer version"""
        if rpm.compare_versions(self._MIN_VERSION, self._api.adcm_version) > -1:
            raise ADCMApiError(
                f"The client supports ADCM versions newer than '{self._MIN_VERSION}'"
            )

    def api_token(self):
        return self._api.api_token

    def adcm(self) -> ADCM:
        """Return 'ADCM' object"""
        return ADCM(self._api)

    def guess_adcm_url(self):
        config = self.adcm().config()
        if config['global']['adcm_url'] is None:
            self.adcm().config_set_diff({"global": {"adcm_url": self.url}})

    def bundle(self, **args) -> Bundle:
        """Return 'Bundle' object"""
        return Bundle(self._api, **args)

    def bundle_list(self, paging=None, **args) -> BundleList:
        """Return list of 'Bundle' objects"""
        return BundleList(self._api, paging=paging, **args)

    def cluster(self, **args) -> Cluster:
        """Return 'Cluster' object"""
        return Cluster(self._api, **args)

    def cluster_list(self, paging=None, **args) -> ClusterList:
        """Return list of 'Cluster' objects"""
        return ClusterList(self._api, paging=paging, **args)

    def cluster_prototype(self, **args) -> ClusterPrototype:
        """Return 'ClusterPrototype' object"""
        return ClusterPrototype(self._api, **args)

    def cluster_prototype_list(self, paging=None, **args) -> ClusterPrototypeList:
        """Return list of 'ClusterPrototype' objects"""
        return ClusterPrototypeList(self._api, paging=paging, **args)

    def host(self, **args) -> Host:
        """Return 'Host' object"""
        return Host(self._api, **args)

    def host_list(self, paging=None, **args) -> HostList:
        """Return list of 'Host' objects"""
        return HostList(self._api, paging=paging, **args)

    def host_prototype(self, **args) -> HostPrototype:
        """Return 'HostPrototype' object"""
        return HostPrototype(self._api, **args)

    def host_prototype_list(self, paging=None, **args) -> HostPrototypeList:
        """Return list of 'HostPrototype' objects"""
        return HostPrototypeList(self._api, paging=paging, **args)

    def job(self, **args) -> Job:
        """Return 'Job' object"""
        return Job(self._api, **args)

    def job_list(self, paging=None, **args) -> JobList:
        """Return list of 'Job' objects"""
        return JobList(self._api, paging=paging, **args)

    def prototype(self, **args) -> Prototype:
        """Return 'Prototype' object"""
        return Prototype(self._api, **args)

    def prototype_list(self, paging=None, **args) -> PrototypeList:
        """Return list of 'Prototype' objects"""
        return PrototypeList(self._api, paging=paging, **args)

    def provider(self, **args) -> Provider:
        """Return 'Provider' object"""
        return Provider(self._api, **args)

    def provider_list(self, paging=None, **args) -> ProviderList:
        """Return list of 'Provider' objects"""
        return ProviderList(self._api, paging=paging, **args)

    def provider_prototype(self, **args) -> ProviderPrototype:
        """Return 'ProviderPrototype' object"""
        return ProviderPrototype(self._api, **args)

    def provider_prototype_list(self, paging=None, **args) -> ProviderPrototypeList:
        """Return list of 'ProviderPrototype' objects"""
        return ProviderPrototypeList(self._api, paging=paging, **args)

    @min_server_version('2020.12.16.15')
    def service(self, **args) -> Service:
        """Return 'Service' object"""
        return Service(self._api, **args)

    @min_server_version('2020.12.16.15')
    def service_list(self, paging=None, **kwargs) -> ServiceList:
        """Return list of 'Service' objects"""
        return ServiceList(self._api, paging=paging, **kwargs)

    def service_prototype(self, **args) -> ServicePrototype:
        """Return 'ServicePrototype' object"""
        return ServicePrototype(self._api, **args)

    def service_prototype_list(self, paging=None, **args) -> ServicePrototypeList:
        """Return list of 'ServicePrototype' objects"""
        return ServicePrototypeList(self._api, paging=paging, **args)

    @min_server_version('2021.05.26.12')
    def component(self, **kwargs) -> Component:
        """Return 'Component' object"""
        return Component(self._api, **kwargs)

    @min_server_version('2021.05.26.12')
    def component_list(self, paging=None, **kwargs) -> ComponentList:
        """Return list of 'Component' objects"""
        return ComponentList(self._api, paging=paging, **kwargs)

    def _upload(self, bundle_stream: BytesIO) -> Bundle:
        """Upload and create Bundle from file={bundle_stream}"""
        try:
            self._api.objects.stack.upload.create(file=bundle_stream)
        except AttributeError as error:
            raise NoSuchEndpointOrAccessIsDenied from error
        bundle_stream.seek(0)
        allure_attach(
            body=bundle_stream.getvalue(),
            name="bundle.tgz",
            extension="tgz",
        )
        try:
            data = self._api.objects.stack.load.create(bundle_file="file")
        except AttributeError as error:
            raise NoSuchEndpointOrAccessIsDenied from error
        bundle_stream.close()
        return self.bundle(bundle_id=data['id'])

    @allure_step('Upload bundle from {dirname}')
    def upload_from_fs(self, dirname, **args) -> Bundle:
        """Upload single bundle from {dirname}"""
        streams = stream.file(dirname, **args)
        if len(streams) > 1:
            raise TooManyArguments(
                'upload_bundle_from_fs is not capable with building multiple \
                bundle editions from one dir. Use upload_from_fs_all instead.'
            )
        return self._upload(streams[0])

    @allure_step('Upload bundles from {dirname}')
    def upload_from_fs_all(self, dirname, **args) -> BundleList:
        """
        Upload multiple bundles from {dirname}
        """
        streams = stream.file(dirname, **args)
        result = BundleList(self._api, empty_bundlelist='not_existing_bundle')
        for st in streams:
            result.append(self._upload(st))
        return result

    @allure_step('Upload bundle from {url}')
    def upload_from_url(self, url) -> Bundle:
        """Upload bundle from {url}"""
        return self._upload(BytesIO(stream.web(url)))

    def bundle_delete(self, **args):
        """Delete bundle object"""
        bundle = self.bundle(**args)
        with allure_step(f"Delete bundle {bundle.name}"):
            try:
                self._api.objects.stack.bundle.delete(bundle_id=bundle.bundle_id)
            except AttributeError as error:
                raise NoSuchEndpointOrAccessIsDenied from error

    def group_config(self, **kwargs) -> GroupConfig:
        """Return 'GroupConfig object'"""
        return GroupConfig(self._api, **kwargs)

    def group_config_list(self, paging=None, **kwargs) -> GroupConfigList:
        """Return list of 'GroupConfig' objects"""
        return GroupConfigList(self._api, paging=paging, **kwargs)

    @min_server_version('2022.01.31.00')
    def me(self) -> "Me":
        return Me(**self._api.action(['rbac', 'me', 'read']))

    @min_server_version('2022.01.31.00')
    def user_create(self, username: str, password: str, **kwargs) -> "User":
        """Create `User` object"""
        return new_user(self._api, username, password, **kwargs)

    @min_server_version('2022.01.31.00')
    def user(self, **kwargs) -> "User":
        """Return `User` object"""
        return User(self._api, **kwargs)

    @min_server_version('2022.01.31.00')
    def user_list(self, paging=None, **kwargs) -> "UserList":
        """Return list of `User` objects"""
        return UserList(self._api, paging=paging, **kwargs)

    @min_server_version('2022.01.31.00')
    def group_create(self, name: str, **kwargs) -> "Group":
        """Create `Group` object"""
        return new_group(self._api, name, **kwargs)

    @min_server_version('2022.01.31.00')
    def group(self, **kwargs) -> "Group":
        return Group(self._api, **kwargs)

    @min_server_version('2022.01.31.00')
    def group_list(self, paging=None, **kwargs) -> "GroupList":
        """Return list of `Group` object"""
        return GroupList(self._api, paging=paging, **kwargs)

    @min_server_version('2022.01.31.00')
    def role_create(self, name: str, **kwargs) -> "Role":
        """Create new `Role` object"""
        return new_role(self._api, name, **kwargs)

    @min_server_version('2022.01.31.00')
    def role(self, **kwargs) -> "Role":
        """Return `Role` object"""
        return Role(self._api, **kwargs)

    @min_server_version('2022.01.31.00')
    def role_list(self, paging=None, **kwargs) -> "RoleList":
        """Return list of `Role` objects"""
        return RoleList(self._api, paging=paging, **kwargs)

    @min_server_version('2022.01.31.00')
    def policy_create(
        self,
        name: str,
        role: Role,
        user: Union[UserList, List[User]],
        group: Union[GroupList, List[Group]] = None,
        objects: List[Union[Cluster, Service, Component, Provider, Host]] = None,
    ) -> "Policy":
        """Create `Policy` object"""
        return new_policy(self._api, name, role, user, group, objects)

    @min_server_version('2022.01.31.00')
    def policy(self, **kwargs) -> "Policy":
        """Return `Policy` object"""
        return Policy(self._api, **kwargs)

    @min_server_version('2022.01.31.00')
    def policy_list(self, paging=None, **kwargs) -> "PolicyList":
        """Return list if `Policy` objects"""
        return PolicyList(self._api, paging=paging, **kwargs)
