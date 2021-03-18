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
from collections import abc
from json import dumps

from coreapi.exceptions import ErrorMessage
from version_utils import rpm

from adcm_client.base import (
    ActionHasIssues, ADCMApiError, BaseAPIListObject, BaseAPIObject, ObjectNotFound,
    TooManyArguments, WaitTimeout, strip_none_keys, min_server_version, allure_step,
    allure_attach_json, legacy_server_implementaion
)
from adcm_client.util import stream
from adcm_client.wrappers.api import ADCMApiWrapper

# Init logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NoCredentionsProvided(Exception):
    """There is no user/password provided. It was not passsed as init parameters
    during ADCMClient initialization and was not passed as a parameter to auth()
    function
    """


##################################################
#                 B U N D L E S
##################################################
class IncorrectPrototypeType(Exception):
    pass


class Bundle(BaseAPIObject):
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
        return self._child_obj(ProviderPrototype)

    def provider_create(self, name, description=None) -> "Provider":
        try:
            prototype = self.provider_prototype()
        except ObjectNotFound:
            raise IncorrectPrototypeType from None
        return prototype.provider_create(name, description)

    def provider_list(self, paging=None, **args) -> "ProviderList":
        try:
            prototype = self.provider_prototype()
        except ObjectNotFound:
            raise IncorrectPrototypeType from None
        return prototype.provider_list(paging=paging, **args)

    def provider(self, **args) -> "Provider":
        try:
            prototype = self.provider_prototype()
        except ObjectNotFound:
            raise IncorrectPrototypeType from None
        return prototype.provider(**args)

    def service_prototype(self, **args) -> "ServicePrototype":
        return self._child_obj(ServicePrototype, **args)

    def cluster_prototype(self) -> "ClusterPrototype":
        return self._child_obj(ClusterPrototype)

    def cluster_create(self, name, description=None) -> "Cluster":
        try:
            prototype = self.cluster_prototype()
        except ObjectNotFound:
            raise IncorrectPrototypeType from None
        return prototype.cluster_create(name, description)

    def cluster_list(self, paging=None, **args) -> "ClusterList":
        try:
            prototype = self.cluster_prototype()
        except ObjectNotFound:
            raise IncorrectPrototypeType from None
        return prototype.cluster_list(paging=paging, **args)

    def cluster(self, **args) -> "Cluster":
        try:
            prototype = self.cluster_prototype()
        except ObjectNotFound:
            raise IncorrectPrototypeType from None
        return prototype.cluster(**args)

    def license(self):
        return self._subcall("license", "read")

    def license_accept(self):
        self._subcall("license", "accept", "update")


class BundleList(BaseAPIListObject):
    _ENTRY_CLASS = Bundle


##################################################
#              P R O T O T Y P E
##################################################
class Prototype(BaseAPIObject):
    PATH = ["stack", "prototype"]
    IDNAME = "prototype_id"
    FILTERS = ["name", "bundle_id"]

    id = None
    prototype_id = None
    name = None
    type = None
    description = None
    version = None
    bundle_id = None
    config = None
    actions = None
    url = None

    def bundle(self) -> "Bundle":
        return self._parent_obj(Bundle)


class PrototypeList(BaseAPIListObject):
    _ENTRY_CLASS = Prototype


class ClusterPrototype(Prototype):
    PATH = ["stack", "cluster"]
    FILTERS = ["name", "bundle_id"]

    def cluster_create(self, name, description=None) -> "Cluster":
        if self.type != 'cluster':
            raise IncorrectPrototypeType
        return new_cluster(
            self._api,
            prototype_id=self.prototype_id,
            name=name,
            description=description
        )

    def cluster_list(self, paging=None, **args) -> "ClusterList":
        return self._child_obj(ClusterList, paging=paging, **args)

    def cluster(self, **args) -> "Cluster":
        return self._child_obj(Cluster, **args)


class ClusterPrototypeList(BaseAPIListObject):
    _ENTRY_CLASS = ClusterPrototype


class ServicePrototype(Prototype):
    PATH = ["stack", "service"]
    FILTERS = ["name", "bundle_id"]

    shared = None
    display_name = None
    required = None
    components = None
    exports = None
    imports = None
    monitoring = None

    @min_server_version('2020.09.25.13')
    def service_list(self, paging=None, **args) -> "ServiceList":
        return self._child_obj(ServiceList, paging=paging, **args)

    @min_server_version('2020.09.25.13')
    def service(self, **args) -> "Service":
        return self._child_obj(Service, **args)


class ServicePrototypeList(BaseAPIListObject):
    _ENTRY_CLASS = ServicePrototype


class ProviderPrototype(Prototype):
    PATH = ["stack", "provider"]
    FILTERS = ["name", "bundle_id"]

    display_name = None
    required = None
    upgrade = None

    def provider_create(self, name, description=None) -> "Provider":
        if self.type != 'provider':
            raise IncorrectPrototypeType
        return new_provider(
            self._api,
            prototype_id=self.prototype_id,
            name=name,
            description=description
        )

    def provider_list(self, paging=None, **args) -> "ProviderList":
        return self._child_obj(ProviderList, paging=paging, **args)

    def provider(self, **args) -> "Provider":
        return self._child_obj(Provider, **args)


class ProviderPrototypeList(BaseAPIListObject):
    _ENTRY_CLASS = ProviderPrototype


class HostPrototype(Prototype):
    PATH = ["stack", "host"]
    FILTERS = ["name", "bundle_id"]

    display_name = None
    required = None
    monitoring = None

    def host_list(self, paging=None, **args) -> "HostList":
        return self._child_obj(HostList, paging=paging, **args)

    def host(self, **args) -> "Host":
        return self._child_obj(Host, **args)


class HostPrototypeList(BaseAPIListObject):
    _ENTRY_CLASS = HostPrototype


##################################################
#           B A S E  O B J E C T
##################################################
class _BaseObject(BaseAPIObject):
    id = None
    url = None
    state = None
    prototype_id = None
    issue = None
    button = None

    def prototype(self):
        raise NotImplementedError

    def action(self, **args) -> "Action":
        return self._subobject(Action, **args)

    def action_list(self, paging=None, **args) -> "ActionList":
        return self._subobject(ActionList, paging=paging, **args)

    def action_run(self, **args) -> "Task":
        warnings.warn('Deprecated. The method accepts no arguments for the "action.run()" method.',
                      DeprecationWarning, stacklevel=2)
        action = self.action(**args)
        return action.run()

    def config(self, full=False):
        history_entry = self._subcall("config", "current", "list")
        if full:
            return history_entry
        return history_entry['config']

    @allure_step("Save config")
    def config_set(self, data):
        # this check is incomplete, cases of presence of keys "config" and "attr" in config
        # are not considered
        allure_attach_json(data, name="Complete config")
        if "config" in data and "attr" in data:
            if data["attr"] is None:
                data["attr"] = {}
            history_entry = self._subcall(
                'config', 'history', 'create', config=data['config'], attr=data['attr'])
            return {key: value for key, value in history_entry.items() if key in ['config', 'attr']}
        history_entry = self._subcall('config', 'history', 'create', config=data)
        return history_entry['config']

    @allure_step("Save config")
    def config_set_diff(self, data):

        def update(d, u):
            # if the old and new values are dictionaries, we try to update, otherwise we replace
            for key, value in u.items():
                if isinstance(value, abc.Mapping) and key in d and isinstance(d[key], abc.Mapping):
                    d[key] = update(d[key], value)
                    continue
                d[key] = value
            return d

        # this check is incomplete, cases of presence of keys "config" and "attr" in config
        # are not considered
        allure_attach_json(data, name="Changed fields")
        is_full = "config" in data and "attr" in data
        config = self.config(full=is_full)
        allure_attach_json(config, name="Original config")
        return self.config_set(update(config, data))

    def config_prototype(self):
        return self.prototype().config


##################################################
#              P R O V I D E R
##################################################
class Provider(_BaseObject):
    IDNAME = "provider_id"
    PATH = ["provider"]
    FILTERS = ["name", "prototype_id"]
    provider_id = None
    name = None
    description = None
    bundle_id = None

    def __repr__(self):
        return f"<Provider {self.name} at {id(self)}>"

    def bundle(self) -> "Bundle":
        return self._parent_obj(Bundle)

    def host_create(self, fqdn) -> "Host":
        return new_host(self._api, **self._merge(fqdn=fqdn))

    def host_list(self, paging=None, **args) -> "HostList":
        return self._child_obj(HostList, paging=paging, **args)

    def host(self, **args) -> "Host":
        return self._child_obj(Host, **args)

    def prototype(self) -> "ProviderPrototype":
        return self._parent_obj(ProviderPrototype)

    def upgrade(self, **args) -> "Upgrade":
        return self._subobject(Upgrade, **args)

    def upgrade_list(self, paging=None, **args) -> "UpgradeList":
        return self._subobject(UpgradeList, paging=paging, **args)


class ProviderList(BaseAPIListObject):
    _ENTRY_CLASS = Provider


@allure_step('Create provider {name}')
def new_provider(api, **args) -> "Provider":
    p = api.objects.provider.create(**strip_none_keys(args))
    return Provider(api, provider_id=p['id'])


##################################################
#              C L U S T E R
##################################################
class Cluster(_BaseObject):
    IDNAME = "cluster_id"
    PATH = ["cluster"]
    FILTERS = ["name", "prototype_id"]
    cluster_id = None
    name = None
    description = None
    bundle_id = None
    serviceprototype = None
    status = None

    def __repr__(self):
        return f"<Cluster {self.name} form bundle - {self.bundle_id} at {id(self)}>"

    def prototype(self) -> "ClusterPrototype":
        return self._parent_obj(ClusterPrototype)

    def bind(self, target):
        if isinstance(target, Cluster):
            self._subcall("bind", "create", export_cluster_id=target.cluster_id)
        elif isinstance(target, Service):
            self._subcall("bind", "create", export_cluster_id=target.cluster_id,
                          export_service_id=target.service_id)
        else:
            raise NotImplementedError

    def bind_list(self, paging=None):
        return self._subcall("bind", "list")

    def bundle(self) -> "Bundle":
        proto = self.prototype()
        return proto.bundle()

    def button(self):
        raise NotImplementedError

    def host(self, **args) -> "Host":
        return self._child_obj(Host, **args)

    def host_list(self, paging=None, **args) -> "HostList":
        return self._child_obj(HostList, paging=paging, **args)

    def host_add(self, host: "Host") -> "Host":
        with allure_step("Add host {} to cluster {}".format(host.fqdn, self.name)):
            data = self._subcall("host", "create", host_id=host.id)
            return Host(self._api, id=data['id'])

    def host_delete(self, host: "Host"):
        with allure_step("Remove host {} from cluster {}".format(host.fqdn, self.name)):
            self._subcall("host", "delete", host_id=host.id)

    def _service_old(self, **args):
        return self._subobject(Service, **args)

    # !!! If you change the version, do not forget to change it in the __new__ method
    # of the Service class as well as in the comments to them
    @legacy_server_implementaion(_service_old, '2020.09.25.13')
    def service(self, **args) -> "Service":
        return self._child_obj(Service, **args)

    def _service_list_old(self, paging=None, **args):
        return self._subobject(ServiceList, paging=paging, **args)

    # !!! If you change the version, do not forget to change it in the __new__ method
    # of the Service class as well as in the comments to them
    @legacy_server_implementaion(_service_list_old, '2020.09.25.13')
    def service_list(self, paging=None, **args) -> "ServiceList":
        return self._child_obj(ServiceList, paging=paging, **args)

    def _service_add_old(self, **args):
        proto = self.bundle().service_prototype(**args)
        with allure_step("Add service {} to cluster {}".format(proto.name, self.name)):
            data = self._subcall("service", "create", prototype_id=proto.id)
            return self._subobject(Service, service_id=data['id'])

    # !!! If you change the version, do not forget to change it in the __new__ method
    # of the Service class as well as in the comments to them
    @legacy_server_implementaion(_service_add_old, '2020.09.25.13')
    def service_add(self, **args) -> "Service":
        proto = self.bundle().service_prototype(**args)
        with allure_step("Add service {} to cluster {}".format(proto.name, self.name)):
            data = self._subcall("service", "create", prototype_id=proto.id, cluster_id=self.id)
            return Service(self._api, id=data['id'])

    @min_server_version('2020.05.13.00')
    def service_delete(self, service: "Service"):
        with allure_step("Remove service {} from cluster {}".format(service.name, self.name)):
            self._subcall("service", "delete", service_id=service.id)

    def hostcomponent(self):
        return self._subcall("hostcomponent", "list")

    @allure_step("Save hostcomponents map")
    def hostcomponent_set(self, *hostcomponents):
        hc = []
        readable_hc = []
        for i in hostcomponents:
            h, c = i
            hc.append({
                'host_id': h.id,
                'service_id': c.service_id,
                'component_id': c.id
            })
            readable_hc.append({
                'host_fqdn': h.fqdn,
                'component_name': c.display_name
            })
        allure_attach_json(readable_hc, name="Readable hc map")
        allure_attach_json(hc, name="Complete hc map")
        return self._subcall("hostcomponent", "create", hc=hc)

    def status_url(self):
        return self._subcall("status", "list")

    def imports(self):
        return self._subcall("import", "list")

    def upgrade(self, **args) -> "Upgrade":
        return self._subobject(Upgrade, **args)

    def upgrade_list(self, paging=None, **args) -> "UpgradeList":
        return self._subobject(UpgradeList, paging=paging, **args)


class ClusterList(BaseAPIListObject):
    _ENTRY_CLASS = Cluster


@allure_step('Create cluster {name}')
def new_cluster(api: ADCMApiWrapper, **args) -> "Cluster":
    c = api.objects.cluster.create(**strip_none_keys(args))
    return Cluster(api, cluster_id=c['id'])


##################################################
#          U P G R A D E
##################################################
class Upgrade(BaseAPIObject):
    IDNAME = "upgrade_id"
    PATH = None
    SUBPATH = ["upgrade"]

    id = None
    upgrade_id = None
    url = None
    name = None
    description = None
    min_version = None
    max_version = None
    min_strict = None
    max_strict = None
    upgradable = None
    state_available = None
    state_on_success = None
    from_edition = None

    def do(self, **args):
        with allure_step("Do upgrade {}".format(self.name)):
            self._subcall("do", "create", **args)


class UpgradeList(BaseAPIListObject):
    SUBPATH = ["upgrade"]
    _ENTRY_CLASS = Upgrade


##################################################
#           S E R V I C E S
##################################################
class Service(_BaseObject):
    IDNAME = "service_id"
    PATH = ['service']
    SUBPATH = ['service']

    id = None
    service_id = None
    bundle_id = None
    name = None
    description = None
    display_name = None
    cluster_id = None
    status = None
    button = None
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

    def bind(self, target):
        if isinstance(target, Cluster):
            self._subcall("bind", "create", export_cluster_id=target.cluster_id)
        elif isinstance(target, Service):
            self._subcall("bind", "create", export_cluster_id=target.cluster_id,
                          export_service_id=target.service_id)
        else:
            raise NotImplementedError

    def prototype(self) -> "ServicePrototype":
        return ServicePrototype(self._api, id=self.prototype_id)

    def cluster(self) -> Cluster:
        return Cluster(self._api, id=self.cluster_id)

    def imports(self):
        return self._subcall("import", "list")

    def bind_list(self, paging=None):
        return self._subcall("bind", "list")

    def _component_old(self, **args) -> "Component":
        return self._subobject(Component, **args)

    # Set a real version when components feature will be merged into develop
    # https://github.com/arenadata/adcm/pull/778
    # !!! If you change the version, do not forget to change it in the __new__ method
    # of the Component class as well as in the comments to them
    @legacy_server_implementaion(_component_old, '2021.12.01.01')
    def component(self, **args) -> "Component":
        return self._child_obj(Component, **args)

    def _component_list_old(self, paging=None, **args) -> "ComponentList":
        return self._subobject(ComponentList, paging=paging, **args)

    # Set a real version when components feature will be merged into develop
    # https://github.com/arenadata/adcm/pull/778
    # !!! If you change the version, do not forget to change it in the __new__ method
    # of the Component class as well as in the comments to them
    @legacy_server_implementaion(_component_list_old, '2021.12.01.01')
    def component_list(self, paging=None, **args) -> "ComponentList":
        return self._child_obj(ComponentList, paging=paging, **args)


class ServiceList(BaseAPIListObject):
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
    IDNAME = "component_id"
    PATH = ["component"]
    SUBPATH = ["component"]

    id = None
    component_id = None
    cluster_id = None
    _service_id = None
    name = None
    display_name = None
    description = None
    constraint = None
    params = None
    prototype_id = None
    requires = None
    bound_to = None
    monitoring = None
    status = None
    state = None

    def __new__(cls, *args, **kwargs):
        """
        Set PATH=None, if adcm version < `2021.12.01.01`. See ADCM-1439.
        This method is associated with the action of the `legacy_server_implementaion()` decorator.
        """
        wrapper = args[0]
        instance = super().__new__(cls)
        # !!! If you change the version, do not forget to change it in the component()
        # and component_list() methods of the Service class as well as in the comments to them
        if rpm.compare_versions(wrapper.adcm_version, '2021.12.01.01') < 0:
            instance.PATH = None
        return instance

    @property
    def service_id(self):
        # this code is for backward compatibility
        if self._service_id is not None:
            return self._service_id
        try:
            return self._endpoint.path_args["service_id"]
        except KeyError:
            return self._data['service_id']

    @service_id.setter
    def service_id(self, value):
        self._service_id = value


class ComponentList(BaseAPIListObject):
    PATH = ["component"]
    SUBPATH = ["component"]
    _ENTRY_CLASS = Component

    def __new__(cls, *args, **kwargs):
        """
        Set PATH=None, if adcm version < `2021.12.01.01`. See ADCM-1439.
        This method is associated with the action of the `legacy_server_implementaion()` decorator.
        """
        wrapper = args[0]
        instance = super().__new__(cls)
        # !!! If you change the version, do not forget to change it in the component()
        # and component_list() methods of the Service class as well as in the comments to them
        if rpm.compare_versions(wrapper.adcm_version, '2021.12.01.01') < 0:
            instance.PATH = None
        return instance


##################################################
#              H O S T
##################################################
class Host(_BaseObject):
    IDNAME = "host_id"
    PATH = ["host"]
    FILTERS = ["fqdn", "prototype_id", "provider_id", "cluster_id"]

    id = None
    host_id = None
    fqdn = None
    provider_id = None
    cluster_id = None
    description = None
    bundle_id = None
    status = None

    def __repr__(self):
        return f"<Host {self.fqdn} form provider - {self.provider_id} at {id(self)}>"

    def provider(self) -> "Provider":
        return self._parent_obj(Provider)

    def cluster(self) -> "Cluster":
        return self._parent_obj(Cluster)

    def bundle(self) -> "Bundle":
        return self._parent_obj(Bundle)

    def prototype(self) -> "HostPrototype":
        return self._parent_obj(HostPrototype)


class HostList(BaseAPIListObject):
    _ENTRY_CLASS = Host


@allure_step('Create host {fqdn}')
def new_host(api, **args) -> "Host":
    h = api.objects.provider.host.create(**args)
    return Host(api, host_id=h['id'])


##################################################
#              A C T I O N
##################################################
class Action(BaseAPIObject):
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
    required_hostcomponentmap = None
    hostcomponentmap = None
    script = None
    script_type = None
    state_available = None
    state_on_fail = None
    state_on_success = None
    type = None
    url = None
    subs = None
    config = None

    def __repr__(self):
        return f"<Action {self.name} at {id(self)}>"

    def _get_config(self):
        config = dict()
        for item in self.config['config']:
            if item['type'] == 'group':
                config[item['name']] = dict()
            elif item['subname']:
                config[item['name']][item['subname']] = item['value']
            else:
                config[item['name']] = item['value']
        return config

    def log_files(self):
        raise NotImplementedError

    def task(self, **args) -> "Task":
        return self._child_obj(Task, **args)

    def task_list(self, **args) -> "TaskList":
        return self._child_obj(TaskList, **args)

    def run(self, **args) -> "Task":
        with allure_step("Run action {}".format(self.name)):

            if 'hc' in args:
                allure_attach_json(args.get('hc'), name="Hostcomponent map")

            if 'config' in args and 'config_diff' in args:
                raise TypeError("only one argument is expected 'config' or 'config_diff'")

            if 'config' not in args:
                args['config'] = self._get_config()

                if 'config_diff' in args:
                    config_diff = args.pop('config_diff')
                    for item in self.config['config']:
                        if item['type'] == 'group':
                            continue

                        key, subkey = item['name'], item['subname']
                        if subkey and subkey in config_diff.get(key, {}):
                            args['config'][key][subkey] = config_diff[key][subkey]
                        elif not subkey and key in config_diff:
                            args['config'][key] = config_diff[key]
            # check backward compatibility for `verbose` option
            if 'verbose' not in args and rpm.compare_versions(
                    self.adcm_version, '2021.02.04.13') >= 0:
                args['verbose'] = False
            try:
                data = self._subcall("run", "create", **args)
            except ErrorMessage as error:
                if (getattr(error.error, 'title', '') == '409 Conflict'
                        and 'has issues' in getattr(error.error, '_data', {}).get('desc', '')):
                    raise ActionHasIssues from error
                raise error
            return Task(self._api, task_id=data["id"])


class ActionList(BaseAPIListObject):
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
        # for component object method will work after version `2021.12.01.01`
        kwargs = {f'{self.object_type}_id': self.object_id}
        return TASK_PARENT[self.object_type](
            self._api, **kwargs).action(action_id=self.action_id)

    def __repr__(self):
        return f"<Task {self.task_id} at {id(self)}>"

    def job(self, **args) -> "Job":
        return Job(self._api, path_args=dict(task_id=self.id), **args)

    def job_list(self, paging=None, **args) -> "JobList":
        return JobList(self._api, paging=paging, path_args=dict(task_id=self.id), **args)

    @allure_step("Wait for task end")
    def wait(self, timeout=None, log_failed=True):
        try:
            status = self.wait_for_attr("status",
                                        self._END_STATUSES,
                                        timeout=timeout)
            if log_failed and status == "failed":
                self._log_jobs(status=status)
        except WaitTimeout as e:
            if log_failed:
                self._log_jobs()
            raise WaitTimeout from e
        return status

    @allure_step("Wait for task to success.")
    def try_wait(self, timeout=None):
        status = self.wait(timeout=timeout)

        if status == "failed":
            raise TaskFailed

        return status

    def _log_jobs(self, **filters):
        for job in self.job_list(**filters):
            log_func = logger.error if job.status == "failed" else logger.info
            log_func("Action: %s", self.action().name)
            for file in job.log_files:
                response = self._api.client.get(file["url"])
                content_format = response.get("format", "txt")
                if "type" in response:
                    log_func("Type: %s", response['type'])
                if "content" in response:
                    if content_format == "json":
                        log_func(dumps(response["content"], indent=2))
                    else:
                        log_func(response["content"])


class TaskList(BaseAPIListObject):
    _ENTRY_CLASS = Task


##################################################
#              L O G
##################################################
class Log(BaseAPIObject):
    IDNAME = 'log_id'
    PATH = ['job', 'log']
    SUBPATH = ['log']
    id = None
    name = None
    type = None
    format = None
    content = None


class LogList(BaseAPIListObject):
    _ENTRY_CLASS = Log
    SUBPATH = ['log']


##################################################
#              J O B
##################################################
class Job(BaseAPIObject):
    IDNAME = "job_id"
    PATH = ["job"]
    FILTERS = ['action_id', 'task_id', 'pid', 'status', 'start_date', 'finish_date']
    _END_STATUSES = ["failed", "success"]
    _WAIT_INTERVAL = .2
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

    # FIXME: remove method __init__, deal with argument path_args
    def __init__(self, api: ADCMApiWrapper, path=None, path_args=None, **args):
        super().__init__(api, path, **args)

    def task(self) -> "Task":
        return self._parent_obj(Task)

    def wait(self, timeout=None):
        return self.wait_for_attr("status",
                                  self._END_STATUSES,
                                  timeout=timeout)

    def log(self, **kwargs) -> "Log":
        return self._subobject(Log, **kwargs)

    def log_list(self, paging=None, **kwargs) -> "LogList":
        return self._subobject(LogList, paging=paging, **kwargs)


class JobList(BaseAPIListObject):
    _ENTRY_CLASS = Job


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
        return Prototype(self._api, id=self.prototype_id)


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

        if self.api_token() is not None:
            self.guess_adcm_url()

        self.adcm_version = self._api.adcm_version
        self._check_min_version()

    def __repr__(self):
        return f"<ADCM API Client for {self.url} at {id(self)}>"

    def auth(self, user=None, password=None):
        if user is None or password is None:
            raise NoCredentionsProvided
        self._api.auth(user, password)
        if self.api_token() is None:
            raise ADCMApiError("Incorrect user/password. Unable to auth.")
        self._check_min_version()

    def _check_min_version(self):
        if rpm.compare_versions(self._MIN_VERSION, self._api.adcm_version) > -1:
            raise ADCMApiError(
                "The client supports ADCM versions newer than '{}'".format(self._MIN_VERSION)
            )

    def api_token(self):
        return self._api.api_token

    def adcm(self) -> ADCM:
        return ADCM(self._api)

    def guess_adcm_url(self):
        config = self.adcm().config()
        if config['global']['adcm_url'] is None:
            self.adcm().config_set_diff({"global": {"adcm_url": self.url}})

    def bundle(self, **args) -> Bundle:
        return Bundle(self._api, **args)

    def bundle_list(self, paging=None, **args) -> BundleList:
        return BundleList(self._api, paging=paging, **args)

    def cluster(self, **args) -> Cluster:
        return Cluster(self._api, **args)

    def cluster_list(self, paging=None, **args) -> ClusterList:
        return ClusterList(self._api, paging=paging, **args)

    def cluster_prototype(self, **args) -> ClusterPrototype:
        return ClusterPrototype(self._api, **args)

    def cluster_prototype_list(self, paging=None, **args) -> ClusterPrototypeList:
        return ClusterPrototypeList(self._api, paging=paging, **args)

    def host(self, **args) -> Host:
        return Host(self._api, **args)

    def host_list(self, paging=None, **args) -> HostList:
        return HostList(self._api, paging=paging, **args)

    def host_prototype(self, **args) -> HostPrototype:
        return HostPrototype(self._api, **args)

    def host_prototype_list(self, paging=None, **args) -> HostPrototypeList:
        return HostPrototypeList(self._api, paging=paging, **args)

    def job(self, **args) -> Job:
        return Job(self._api, **args)

    def job_list(self, paging=None, **args) -> JobList:
        return JobList(self._api, paging=paging, **args)

    def prototype(self, **args) -> Prototype:
        return Prototype(self._api, **args)

    def prototype_list(self, paging=None, **args) -> PrototypeList:
        return PrototypeList(self._api, paging=paging, **args)

    def provider(self, **args) -> Provider:
        return Provider(self._api, **args)

    def provider_list(self, paging=None, **args) -> ProviderList:
        return ProviderList(self._api, paging=paging, **args)

    def provider_prototype(self, **args) -> ProviderPrototype:
        return ProviderPrototype(self._api, **args)

    def provider_prototype_list(self, paging=None, **args) -> ProviderPrototypeList:
        return ProviderPrototypeList(self._api, paging=paging, **args)

    def service(self, **args) -> Service:
        return Service(self._api, **args)

    def service_prototype(self, **args) -> ServicePrototype:
        return ServicePrototype(self._api, **args)

    def service_prototype_list(self, paging=None, **args) -> ServicePrototypeList:
        return ServicePrototypeList(self._api, paging=paging, **args)

    def _upload(self, bundle_stream) -> Bundle:
        self._api.objects.stack.upload.create(file=bundle_stream)
        data = self._api.objects.stack.load.create(bundle_file="file")
        return self.bundle(bundle_id=data['id'])

    @allure_step('Upload bundle from "{1}"')
    def upload_from_fs(self, dirname, **args) -> Bundle:
        streams = stream.file(dirname, **args)
        if len(streams) > 1:
            raise TooManyArguments('upload_bundle_from_fs is not capable with building multiple \
                bundle editions from one dir. Use upload_from_fs_all instead.')
        return self._upload(streams[0])

    @allure_step('Upload bundles from "{1}"')
    def upload_from_fs_all(self, dirname, **args) -> BundleList:
        streams = stream.file(dirname, **args)
        # Create empty bundle list by filtering on wittingly nonexisting field
        # and value.
        result = BundleList(self._api, empty_bundlelist='not_existing_bundle')
        for st in streams:
            result.append(self._upload(st))
        return result

    @allure_step('Upload bundle from "{1}"')
    def upload_from_url(self, url) -> Bundle:
        return self._upload(stream.web(url))

    @allure_step("Delete bundle")
    def bundle_delete(self, **args):
        self._api.objects.stack.bundle.delete(bundle_id=self.bundle(**args).bundle_id)
