from django.shortcuts import HttpResponse
from my_models.models import Flavor
from .openstack import make_keystone_session, get_all_flavors
from my_settings import Settings


# Create your views here.

def update_flavors(request, *args, **kwargs):
    settings = Settings.get_settings()

    session = make_keystone_session(
        url=settings['openstack']['keystone-url'],
        username=settings['openstack']['keystone-username'],
        password=settings['openstack']['keystone-password'],
        project_name=settings['openstack']['project']
    )

    flavors = get_all_flavors(session)

    for flavor in flavors:
        if Flavor.objects.filter(flv_id=flavor.id).exists():
            continue
        entry = Flavor(
            flv_id=flavor.id,
            name=flavor.name,
            ram=flavor.ram,
            vcpu=flavor.vcpus,
            disk=flavor.disk
        )
        entry.save()

    return HttpResponse('Success!')