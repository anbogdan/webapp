from time import sleep
from my_settings import Settings
from my_models.models import Application
from django.core.management.base import BaseCommand
from my_apis.openstack import make_keystone_session, get_all_flavors, create_vm, fetch_all_images, get_flavor_by_name, get_image_by_name
from git import Repo
import subprocess

class Command(BaseCommand):
    help = 'Allocation worker'

    def handle(self, *args, **kwargs):
        while True:
            entry = Application.objects.select_for_update().filter(status='pending').first()
            if entry is None:
                print('No entry for update! Waiting 5 seconds!')
            else:
                entry.status = 'allocating'
                entry.save()
                settings = Settings.get_settings()
                session = make_keystone_session(
                    url=settings['openstack']['keystone-url'],
                    username=settings['openstack']['keystone-username'],
                    password=settings['openstack']['keystone-password'],
                    project_name=settings['openstack']['project']
                )

                image_name = settings['openstack']['default-image']
                flavor_name = entry.flv
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
                entry.status = 'configure'
                entry.ip = server.addresses['vlan9'][0]['addr']
                entry.save()
                sleep(30)
                subprocess.call(['ansible-playbook', 'basic_recipe.yml', '-i {},'.format(entry.ip)])
                Repo.clone_from(entry.repo, server_name)
                subprocess.call(['ansible-playbook', '{}/recipe.yml'.format(server_name), '-i {},'.format(entry.ip)])
                subprocess.call(['rm','-rf', server_name])
                print('Updated entry: {entry_name}. Waiting 5 seconds!'.format(entry_name=entry.name))
            sleep(5)