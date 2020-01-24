import codecs
import os
import random
import string
from itertools import chain

import jinja2
import yaml
from docker import from_env
from docker.client import DockerClient
from docker.errors import ImageNotFound
from docker.models.containers import Container  # pylint: disable=unused-import
from docker.models.images import Image


class NoModulesToInstall(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors


def _get_top_dirs(module: str, image: Image, client: DockerClient) -> "list":
    """Returns a list of paths to all top level folders
     and files of python module that must be installed in image
    :param module: module name
    :type module: str
    :param image: image name
    :type image: Image
    :param d_client: docker client
    :type d_client: DockerClient
    :return: list of path on image fs to module files
    :rtype: list
    """

    data = yaml.safe_load(
        client.containers.run(
            image,
            'pip show -f %s' % module,
            remove=True
        ).decode("utf-8")
    )

    return [os.path.join(data['Location'], i) for i in list(
        dict.fromkeys(
            map(
                lambda x: x.split('/')[0],
                data['Files'].split()
            )
        )) if i not in ['..', '.']]


def _get_modules_list(image: Image, client: DockerClient) -> "list":
    return client.containers.run(
        image, '/bin/sh -c "pip freeze"', remove=True).decode("utf-8").split()


def _get_prepared_container(pkgs: list, image: Image, client: DockerClient) -> "Container":
    command = '/bin/sh -c "'
    if pkgs.get('system_pkg'):
        command += 'apk add ' + ' '.join(pkgs.get('system_pkg')) + ' >/dev/null ;'
    command += ' pip install ' + ' '.join(pkgs.get('python_mod')) + ' >/dev/null"'
    return client.containers.run(image, command, detach=True)


def _copy_pkgs_files(source_path, dirs, image: Image, volumes: dict, client: DockerClient):
    dirs = list(dict.fromkeys(dirs))  # filter on keys of duplicate elements
    command = '/bin/sh -c "mkdir %s/pmod; cp -r %s %s/pmod ;' % (source_path,
                                                                 ' '.join(dirs),
                                                                 source_path)
    command += ' chown -R %s %s/pmod"' % (os.getuid(), source_path)
    client.containers.run(image, command, volumes=volumes, remove=True)


def _get_prepared_image(pkgs, image: Image, client: DockerClient) -> "Image":
    container = _get_prepared_container(pkgs, image, client)
    container.wait()

    prepared_image_name = [
        image.tags[0].split(':')[0],
        ''.join(random.sample(string.ascii_lowercase, 5))
    ]
    prepared_image = container.commit(repository=prepared_image_name[0],
                                      tag=prepared_image_name[1])
    container.remove()
    return prepared_image


def python_mod_req(source_path, workspace, **kwargs):
    with open(os.path.join(source_path, kwargs['requirements']), 'r') as file:
        pkgs = yaml.safe_load(file)
        if pkgs.get('python_mod'):
            client = from_env()
            image_name = "arenadata/adcm:latest" if not kwargs.get('image') else kwargs['image']
            image = client.images.pull(image_name)
            rm_prepared_image = True
            if kwargs.get('prepared_image'):
                try:
                    rm_prepared_image = False
                    prepared_image = client.images.get(kwargs['prepared_image'])
                except ImageNotFound:
                    prepared_image = _get_prepared_image(pkgs, image, client)
            else:
                prepared_image = _get_prepared_image(pkgs, image, client)

            default_module_list = _get_modules_list(image, client)
            dirs = list(chain.from_iterable(
                [_get_top_dirs(module, prepared_image, client)
                 for module in map(
                     lambda x: x.split('==')[0],
                     [var for var in _get_modules_list(prepared_image, client)
                      if var not in default_module_list])]
            ))

            volumes = {
                workspace: {'bind': workspace, 'mode': 'rw'}
            }
            _copy_pkgs_files(source_path, dirs, prepared_image, volumes, client)

            if rm_prepared_image:
                client.images.remove(prepared_image.id)

        else:
            raise NoModulesToInstall('Can`t get python modules list to be inatalled')


def splitter(*args, **kwargs):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(args[0]),
                             undefined=jinja2.StrictUndefined)
    for file in kwargs['files']:
        tmpl = env.get_template(file)
        with codecs.open(os.path.join(args[0], (os.path.splitext(file)[0])), 'w', 'utf-8') as f:
            f.write(tmpl.render(kwargs['edition']))


def get_type_func(tpe):
    types = {'python_mod_req': python_mod_req, 'splitter': splitter}
    return types[tpe]
