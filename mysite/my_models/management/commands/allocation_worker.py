import socket
from time import sleep, time
import paramiko
import yaml
from paramiko import BadHostKeyException, AuthenticationException, SSHException

from my_settings import Settings
from my_models.models import Application, SshKey
from django.core.management.base import BaseCommand
from my_apis.openstack import make_keystone_session, get_all_flavors, create_vm, fetch_all_images, get_flavor_by_name,\
    get_image_by_name, delete_vm
from git import Repo
import subprocess


def check_ssh(ip, interval=1, timeout=30):
    start_time = time()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host_up = False

    while not host_up:
        if time() - start_time > timeout:
            raise TimeoutError
        try:
            ssh.connect(ip, username='student', key_filename='deploy', timeout=5)
            host_up = True
        except (BadHostKeyException, AuthenticationException,
                SSHException, socket.error) as _:
            sleep(interval)


def create_user_ssh_recipe(username, key, server_name):
    with open("ssh_recipe.yml", 'r') as stream:
        try:
            my_file = yaml.safe_load(stream)
            my_file[0]['tasks'][0]['user']['name'] = username
            my_file[0]['tasks'][1]['authorized_key']['user'] = username
            my_file[0]['tasks'][1]['authorized_key']['key'] = key
            with open('{}/ssh_recipe.yml'.format(server_name), 'w') as fp:
                yaml.dump(my_file, fp)
        except yaml.YAMLError as exc:
            print(exc)


class Command(BaseCommand):
    help = 'Allocation worker'

    def handle(self, *args, **kwargs):
        settings = Settings.get_settings()
        session = make_keystone_session(
            url=settings['openstack']['keystone-url'],
            username=settings['openstack']['keystone-username'],
            password=settings['openstack']['keystone-password'],
            project_name=settings['openstack']['project']
        )
        while True:
            entry = Application.objects.select_for_update().filter(status='pending').first()
            if entry is None:
                print('No entry for update! Waiting 5 seconds!')
            elif entry.action == 'allocate':
                print('Allocating %s for user %s.' % (entry.name, entry.user))
                entry.status = 'allocating'
                entry.save()

                image_name = settings['openstack']['default-image']
                flavor_name = str(entry.flv)
                server_name = '{}_{}'.format(entry.user, entry.name)

                images = fetch_all_images(session)
                image = get_image_by_name(images, image_name)
                if not image:
                    raise Exception('Image "%s" not found.' % image_name)
                flavors = get_all_flavors(session)
                flavor = get_flavor_by_name(flavors, flavor_name)
                if not flavor:
                    raise Exception('Flavor "%s" not found.' % flavor_name)
                server = create_vm(session, server_name, image.id, flavor.id)
                entry.server_id = server.id
                entry.allocated = True
                entry.status = 'configure'
                entry.ip = server.addresses['vlan9'][0]['addr']
                entry.save()
                try:
                    check_ssh(entry.ip)
                except TimeoutError as e:
                    print(e)
                print('Machine for %s is ready. Starting configuring step.' % server_name)
                subprocess.call(['ansible-playbook', 'basic_recipe.yml', '-i {},'.format(entry.ip)])
                Repo.clone_from(entry.repo, server_name)
                ssh_key_entry = SshKey.objects.get(user=entry.user)
                create_user_ssh_recipe(entry.user.get_username(), ssh_key_entry.sshkey, server_name)
                subprocess.call(['ansible-playbook', '{}/ssh_recipe.yml'.format(server_name), '-i {},'.format(entry.ip)])
                subprocess.call(['ansible-playbook', '{}/recipe.yml'.format(server_name), '-i {},'.format(entry.ip)])
                subprocess.call(['rm','-rf', server_name])
                print('Configure action done for %s.' % server_name)
                print('Updated entry: {entry_name}. Waiting 5 seconds!'.format(entry_name=entry.name))
                entry.status = 'ready'
                entry.save()
            else:
                print('Starting deallocation process for %s\'s %s application.' % (entry.user, entry.name))
                delete_vm(session, entry.server_id)
                entry.status = 'no status'
                entry.ip = '-'
                entry.action = 'none'
                entry.allocated = False
                entry.server_id = 'none'
                entry.save()
                print('%s\'s %s application deallocated.' % (entry.user, entry.name))
            sleep(5)


