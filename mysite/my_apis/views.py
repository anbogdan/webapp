from django.shortcuts import HttpResponse
from my_models.models import Flavor
from .openstack import make_keystone_session, get_all_flavors, create_vm, fetch_all_images, get_flavor_by_name, get_image_by_name
from my_settings import Settings
from .models import AllocateAppForm


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

def api_allocate_app(request, *args, **kwargs):
    if request.user.is_authenticated:
        if request.method == 'POST':
            settings = Settings.get_settings()
            form = AllocateAppForm(request.POST)
            if form.is_valid():
                session = make_keystone_session(
                    url=settings['openstack']['keystone-url'],
                    username=settings['openstack']['keystone-username'],
                    password=settings['openstack']['keystone-password'],
                    project_name=settings['openstack']['project']
                )

                image_name = settings['openstack']['default-image']
                flavor_name = form.cleaned_data['flavor_name']
                server_name = form.cleaned_data['server_name']

                images = fetch_all_images(session)
                image = get_image_by_name(images, image_name)
                if not image:
                    raise Exception('Image "%s" not found.' % image_name)
                flavors = get_all_flavors(session)
                flavor = get_flavor_by_name(flavors, flavor_name)
                if not flavor:
                    raise Exception('Flavor "%s" not found.' % flavor_name)
                server = create_vm(session, server_name, image.id, flavor.id)
                return server

