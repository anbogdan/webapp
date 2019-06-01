import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from keystoneauth1.identity import Password as KeystonePassword
from keystoneauth1.session import Session as KeystoneSession
from glanceclient.client import Client as GlanceClient
from novaclient.client import Client as NovaClient

def make_keystone_session(url, username, password, project_name=None):
    auth = KeystonePassword(
        auth_url=url,
        username=username,
        password=password,
        project_name=project_name,
        project_domain_id='default',
        project_domain_name='default',
        user_domain_id='default',
        user_domain_name='default'
    )

    # build session and client
    return KeystoneSession(auth=auth, verify=False)


def make_glance_client(session):
    return GlanceClient('2', session=session)


def make_nova_client(session):
    return NovaClient('2', session=session)


def fetch_all_images(session):
    glance_client = make_glance_client(session)
    images_generator = glance_client.images.list()
    return [image for image in images_generator]


def get_image_by_name(images, image_name):
    for image in images:
        if image.name == image_name:
            return image
    return None


def print_images(title, images):
    print("\n%s:" % title)
    for image in images:
        print("- %s" % '\t'.join([image.id, image.updated_at, image.name]))


def print_flavors(title, flavors):
    print("\n%s:" % title)
    for flavor in flavors:
        print("- %s" % '\t'.join([flavor.id, flavor.name]))


def get_all_flavors(session):
    nova_client = make_nova_client(session)
    return [flavor for flavor in nova_client.flavors.list(detailed=True)]


def get_flavor_by_name(flavors, flavor_name):
    for flavor in flavors:
        if flavor.name == flavor_name:
            return flavor
    return None


def create_vm(session, server_name, image_id, flavor_id, meta=None, timeout=None):
    nova_client = make_nova_client(session)

    server = nova_client.servers.create(
        name=server_name,
        image=image_id,
        flavor=flavor_id,
        meta=meta,
        key_name='default',
        security_groups=['default']
    )

    print('Waiting for server %s to become active' % server.id)
    start_time = time.time()
    while True:
        if server.status == 'ACTIVE':
            break
        if server.status == 'ERROR':
            if hasattr(server, 'fault') and isinstance(server.fault, dict):
                raise Exception(server.fault.get('message'))
            raise Exception('Unable to create server. Error cause not reported by OpenStack.')
        if timeout:
            duration = time.time() - start_time
            if duration > timeout:
                raise Exception('Timeout waiting for server to become active (%.2f sec)' % duration)
        time.sleep(1)
        server = nova_client.servers.get(server.id)

    return server


def delete_vm(session, server_id):
    nova_client = make_nova_client(session)
    server = nova_client.servers.get(server_id)
    server.delete()