from django.shortcuts import HttpResponse, render
from .models import Flavor, Application, AddAppForm
from .openstack import make_keystone_session, get_all_flavors
import yaml


# Create your views here.

def update_flavors(request, *args, **kwargs):
    with open('settings.yml', 'r') as settings_file:
        settings = yaml.load(settings_file)

    session = make_keystone_session(
        url=settings['openstack']['keystone-url'],
        username=settings['openstack']['keystone-username'],
        password=settings['openstack']['keystone-password'],
        project_name=settings['openstack']['project']
    )

    flavors = get_all_flavors(session)

    for flavor in flavors:
        entry = Flavor(
            flv_id=flavor.id,
            name=flavor.name,
            ram=flavor.ram,
            vcpu=flavor.vcpus,
            disk=flavor.disk
        )
        entry.save()

    return HttpResponse('Success!')

def add_application(request, *args, **kwargs):
    template = 'addapplication.html'
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AddAppForm(request.POST)
            if form.is_valid():
                if Application.objects.filter(username=form.cleaned_data['name']).exists():
                    return render(request, template, {
                        'form': form,
                        'error_message': 'Username already exists.'
                    })
