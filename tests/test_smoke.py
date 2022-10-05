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

import inspect
import os
import tarfile
from pathlib import Path

import allure
import pytest
from adcm_pytest_plugin.utils import get_data_dir

from adcm_client.base import ObjectNotFound, Paging
from adcm_client.objects import ADCMClient, HostList, TaskFailed


def test_bundle_upload(sdk_client_fs: ADCMClient):
    bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/cluster")
    prototype = bundle.cluster_prototype()

    assert bundle.name == "test_cluster_name"
    assert bundle.description == "That is description"
    assert bundle.version == "1.4"
    assert prototype.name == "test_cluster_name"
    assert prototype.description == "That is description"
    assert prototype.version == "1.4"


def test_bundle_delete(sdk_client_fs: ADCMClient):
    with allure.step("Delete bundle"):
        with pytest.raises(ObjectNotFound):
            sdk_client_fs.bundle_delete(name="unicorn")
    with allure.step("Upload bundle"):
        bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/cluster")
    with allure.step("Delete bundle"):
        sdk_client_fs.bundle_delete(name=bundle.name)


def test_bundle_test_list(sdk_client_fs: ADCMClient):
    with allure.step("Upload and get bundle list"):
        for i in range(1, 4):
            sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/cluster" + str(i))
        type1 = sdk_client_fs.bundle_list(name="cluster_type_1")
    with allure.step("Check bundle list name and version"):
        assert len(type1) == 2
        assert type1[0].name == "cluster_type_1"
        assert type1[1].name == "cluster_type_1"
        assert sorted([type_el.version for type_el in type1]) == ["1.4", "1.5"]


def _assert_attrs(obj):
    with allure.step(f"Check missed attrs of {obj.__class__}"):
        missed = []
        for k in obj._data.keys():
            if not hasattr(obj, k):
                missed.append(k)
        assert not missed

    ignored_attrs = ["IDNAME", "PATH", "FILTERS", "SUBPATH", "adcm_version"]
    with allure.step(f"Check redundant attrs of {obj.__class__}"):
        redundant = []
        attrs = [
            attr[0]
            for attr in inspect.getmembers(obj.__class__, lambda x: not inspect.isroutine(x))
            if not attr[0].startswith("_") and attr[0] not in ignored_attrs
        ]
        for attr in attrs:
            if attr not in obj._data.keys():
                redundant.append(attr)
        assert not redundant


def test_cluster_attrs(sdk_client_fs: ADCMClient):
    with allure.step("Create sample cluster"):
        bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/cluster")
        cluster1 = bundle.cluster_prototype().cluster_create(name="sample cluster")
    with allure.step("Check cluster attributes"):
        _assert_attrs(cluster1)


def test_cluster_crud(sdk_client_fs: ADCMClient):
    with allure.step("Create two clusters"):
        bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/cluster")
        cluster1 = bundle.cluster_prototype().cluster_create(name="sample cluster")
        cluster2 = bundle.cluster_create(name="sample cluster 2", description="huge one!")
    with allure.step("Check clusters name and id"):
        assert cluster1.cluster_id == 1
        assert cluster1.name == "sample cluster"
        assert cluster2.cluster_id == 2
        assert cluster2.name == "sample cluster 2"
    with allure.step("Check cluster list len=2 and names"):
        cl = bundle.cluster_list()
        assert len(cl) == 2
        assert cl[0].name != cl[1].name
        assert len(bundle.cluster_list(name="sample cluster")) == 1
    with allure.step("Delete first cluster"):
        cluster1.delete()
    with allure.step("Check cluster list len=1 and names"):
        cl = bundle.cluster_list()
        assert len(cl) == 1
        assert cl[0].description == cluster2.description
    with allure.step("Delete second cluster"):
        cluster2.delete()
    with allure.step("Check cluster list empty"):
        assert bundle.cluster_list() == []


def test_hostprovider_and_host_crud(sdk_client_fs: ADCMClient):
    with allure.step("Create provider"):
        bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/provider")
        provider = bundle.provider_prototype().provider_create(name="test_name")
    with allure.step("Check provider"):
        _assert_attrs(provider)
        _assert_attrs(provider.prototype())
        assert provider.provider_id == 1
        assert provider.name == "test_name"
    with allure.step("Create host"):
        host = provider.host_create(fqdn="localhost")
    with allure.step("Check host"):
        _assert_attrs(host)
        _assert_attrs(host.prototype())
    with allure.step("Delete host and provider"):
        host.delete()
        provider.delete()


def test_cluster_action(sdk_client_fs: ADCMClient):
    with allure.step("Create cluster"):
        bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/cluster")
        cluster = bundle.cluster_create(name="sample cluster")
    with allure.step("Run cluster action: install"):
        install = cluster.action(name="install")
    with allure.step("Check action"):
        assert install.name == "install"
        _assert_attrs(install)
        job = install.run()
        assert job.wait() == "success"


def test_cluster_config(sdk_client_fs: ADCMClient):
    with allure.step("Create cluster and get config"):
        bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/cluster")
        cluster = bundle.cluster_create(name="sample cluster")
        conf1 = cluster.config()
        assert conf1["xxx"]["yyy"] == "cool-value"
    with allure.step("Set cluster config"):
        conf1["xxx"]["yyy"] = "nice-value"
        result = cluster.config_set(conf1)
    with allure.step("Check cluster config"):
        conf2 = cluster.config()
        assert conf2["xxx"]["yyy"] == "nice-value"
        assert result == conf2


def test_cluster_full_config(sdk_client_fs: ADCMClient):
    with allure.step("Create cluster with activatable, get and check conf1"):
        bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/cluster_with_activatable")
        cluster = bundle.cluster_create(name="sample cluster")
        conf1 = cluster.config(full=True)
        assert conf1["config"]["xxx"]["yyy"] == "cool-value"
    with allure.step("Set cluster full config"):
        conf1["config"]["xxx"]["yyy"] = "nice-value"
        result = cluster.config_set(conf1)
    with allure.step("Check cluster full config"):
        conf2 = cluster.config(full=True)
        assert conf2["config"]["xxx"]["yyy"] == "nice-value"
        assert result["config"] == conf2["config"]


def test_cluster_config_attrs(sdk_client_fs: ADCMClient):
    with allure.step("Create cluster with activatable, get and check conf3"):
        bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/cluster_with_activatable")
        cluster = bundle.cluster_create(name="sample cluster")
        conf3 = cluster.config(full=True)
        conf3["attr"]["xxx"]["active"] = False
    with allure.step("Set cluster config"):
        cluster.config_set(conf3)
    with allure.step("Check cluster config attributes"):
        conf4 = cluster.config(full=True)
        assert conf3["attr"]["xxx"]["active"] == conf4["attr"]["xxx"]["active"]


def test_cluster_set_diff(sdk_client_fs: ADCMClient):
    with allure.step("Create new cluster"):
        bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/cluster")
        cluster = bundle.cluster_create(name="sample cluster")
    with allure.step("Set cluster diff"):
        cluster.config_set_diff({"xxx": {"yyy": "nice-value"}})
    with allure.step("Check cluster config"):
        conf1 = cluster.config(full=True)
        assert conf1["config"]["xxx"]["yyy"] == "nice-value"


def test_cluster_service(sdk_client_fs: ADCMClient):
    with allure.step("Create cluster with service"):
        bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/cluster_with_service")
        cluster = bundle.cluster_create(name="sample cluster")
    with allure.step("Add service"):
        service = cluster.service_add(name="some_test_service")
    with allure.step("Check cluster service"):
        _assert_attrs(service)
        _assert_attrs(service.prototype())
        service.action(name="install").run().wait()


def test_component(sdk_client_fs: ADCMClient):
    with allure.step("Create cluster with service and components"):
        bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/cluster_with_service")
        cluster = bundle.cluster_create(name="sample cluster")
    with allure.step("Add service"):
        service = cluster.service_add(name="some_test_service")
    with allure.step("Check component"):
        component = service.component_list().pop()
        _assert_attrs(component)


@pytest.fixture()
def cluster_with_service(sdk_client_fs: ADCMClient):
    """Create cluster and add service"""
    bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/cluster_with_service")
    cluster = bundle.cluster_create(name="sample cluster")
    cluster.service_add(name="some_test_service")
    return cluster


def test_hostcomponent(sdk_client_fs: ADCMClient, cluster_with_service):
    with allure.step("Create default provider"):
        bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/provider")
        provider = bundle.provider_prototype().provider_create(name="test_name")
    with allure.step("Create and add three hosts"):
        host1 = provider.host_create(fqdn="localhost1")
        host2 = provider.host_create(fqdn="localhost2")
        host3 = provider.host_create(fqdn="localhost3")
        cluster_with_service.host_add(host1)
        cluster_with_service.host_add(host2)
        cluster_with_service.host_add(host3)
    with allure.step("Create service"):
        service = cluster_with_service.service(name="some_test_service")
    with allure.step("Set components"):
        components = service.component_list()
        cluster_with_service.hostcomponent_set(
            (host1, components[0]),
            (host2, components[0]),
            (host3, components[0]),
            (host3, components[1]),
        )


def test_cluster_service_not_found(sdk_client_fs: ADCMClient):
    with allure.step("Create cluster with service with error"):
        bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/cluster_with_service")
        cluster = bundle.cluster_create(name="sample cluster")
        with pytest.raises(ObjectNotFound):
            cluster.service(name="some_test_service")
    with allure.step("Add service"):
        cluster.service_add(name="some_test_service")
    with allure.step("Check service"):
        assert cluster.service().name == "some_test_service"


def test_action_fail(sdk_client_fs: ADCMClient):
    with allure.step("Create cluster with fail"):
        bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/cluster_with_fail")
        cluster = bundle.cluster_create(name="sample cluster")
    with allure.step("Check action fail"):
        with pytest.raises(TaskFailed):
            cluster.action(name="fail").run().try_wait()


def test_cluster_upgrade(sdk_client_fs: ADCMClient):
    with allure.step("Create cluster with upgrade"):
        for i in range(1, 4):
            sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/cluster_upgrade" + str(i))
            cluster = sdk_client_fs.bundle(name="cluster", version="1.4").cluster_create(
                name=f"cluster_{i}"
            )
    with allure.step("Check upgrade list len=2"):
        assert len(cluster.upgrade_list()) == 2
        _assert_attrs(cluster.upgrade(name="2"))
    with allure.step("Upgrade cluster"):
        cluster.upgrade(name="2").do()
    with allure.step("Check upgrade list len=1"):
        assert len(cluster.upgrade_list()) == 1
    with allure.step("Upgrade cluster"):
        cluster.upgrade(name="3").do()
    with allure.step("Check upgrade list empty"):
        assert len(cluster.upgrade_list()) == 0


def test_paging_on_hosts(sdk_client_fs: ADCMClient):
    with allure.step("Create def provider"):
        bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__) + "/provider")
        provider = bundle.provider_prototype().provider_create(name="test_provider")
    with allure.step("Create host"):
        for i in range(1, 100):
            provider.host_create(fqdn=f"host{str(i)}")
    with allure.step("Check hosts"):
        prev_id = -1
        prev_fqdn = "xxxx"
        for host in Paging(provider.host_list):
            assert host.provider_id == provider.provider_id
            assert host.fqdn != prev_fqdn
            assert host.id != prev_id
            prev_id = host.id
            prev_fqdn = host.fqdn
        prev_id = -1
        prev_fqdn = "xxxx"
        for host in Paging(HostList, api=provider._api):
            assert host.provider_id == provider.provider_id
            assert host.fqdn != prev_fqdn
            assert host.id != prev_id
            prev_id = host.id
            prev_fqdn = host.fqdn


def test_adcm_config_url(sdk_client_fs: ADCMClient):
    with allure.step("Set config diff"):
        sdk_client_fs.adcm().config_set_diff({"global": {"adcm_url": sdk_client_fs.url}})
    with allure.step("Get config"):
        conf = sdk_client_fs.adcm().config()
    with allure.step("Check adcm config url"):
        assert conf["global"]["adcm_url"] == sdk_client_fs.url


def test_adcm_config_url_guess(sdk_client_fs: ADCMClient):
    with allure.step("Get config"):
        conf = sdk_client_fs.adcm().config()
    with allure.step("Check adcm config url guess"):
        assert conf["global"]["adcm_url"] == sdk_client_fs.url


def test_adcm_config_url_no_guess(sdk_client_fs: ADCMClient):
    with allure.step("Set config diff"):
        sdk_client_fs.adcm().config_set_diff({"global": {"adcm_url": "test_url"}})
    with allure.step("Set adcm url"):
        sdk_client_fs.guess_adcm_url()
    with allure.step("Check adcm config url no guess"):
        conf = sdk_client_fs.adcm().config()
        assert conf["global"]["adcm_url"] == "test_url"


def test_task_download(sdk_client_fs: ADCMClient, tmpdir):
    with allure.step("Create cluster"):
        bundle = sdk_client_fs.upload_from_fs(get_data_dir(__file__, "cluster"))
        cluster = bundle.cluster_create(name="sample cluster")
    with allure.step("Run action and wait for result"):
        task = cluster.action(name="install").run()
        task.wait()
    with allure.step("Download logs and check the result"):
        custom_download: Path = task.download_logs(tmpdir)
        assert custom_download.name in os.listdir(tmpdir)
        assert tarfile.is_tarfile(custom_download)
        default_download: Path = task.download_logs()
        assert tarfile.is_tarfile(default_download)
        assert default_download.name in os.listdir(os.getcwd())
        assert str(default_download.parent) != str(custom_download.parent)
        assert default_download.name == custom_download.name
