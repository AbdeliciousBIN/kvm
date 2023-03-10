import uuid

from django.shortcuts import redirect, render
import sys
import libvirt
from .tasks import create_vm
import datetime
from celery.result import AsyncResult
from celery import current_app
import json


# Create your views here.
def index(request):
    return render(request, 'index.html')


def ajoutKvm(request):

    if request.method == 'POST':  # Collecting data from our form
        data = request.POST
        nameKvm = str(data.get('nameKvm'))
        memory = str(data.get('memory'))
        cpu = str(data.get('cpu'))
        os = str(data.get('os'))
        date = str(data.get('datetime'))
        date_to_typeDate = datetime.datetime.strptime(
            date, '%Y-%m-%dT%H:%M:%S')
        # used to calculate the diff with form date
        datetime_now = datetime.datetime.now()

        conn = libvirt.open("qemu:///system")
        domains = conn.listAllDomains(0)

        for domain in domains:  # Checking IF unique VM
            if (domain.name() == nameKvm):
                errorExit0 = True  # VM NAME ALREADY EXIST
                return render(request, 'ajout.html', {'error0': errorExit0})
        if (date_to_typeDate < datetime_now):  # if date.now less than date form we proceed as usual
            if (create_vm(name=nameKvm, memory=memory, cpu=cpu, os=os)):
                return redirect('listeKvm')
            else:
                errorExit1 = True
                return render(request, 'listeKvm.html', {"error1": errorExit1})
        else:  # ELSE we schedule the task
            print("we schedule the task")
            if (create_vm.apply_async(args=(nameKvm, memory, cpu, os), eta=date_to_typeDate)):
                return redirect('listeKvm')
            else:
                errorExit1 = True
                return render(request, 'listeKvm.html', {"error1": errorExit1})

     # Forwarding to Form for adding VM
    datetime_now = datetime.datetime.now()
    # forwarding datetime.now() to form
    datetime_form = datetime_now.strftime("%Y-%m-%dT%H:%M:%S")
    print(datetime_form)
    # Render Form of VM
    return render(request, 'ajout.html', {'datetime_form': datetime_form})


def listeKvm(request):
    conn = libvirt.open("qemu:///system")
    # If a value of 0 is specified then all domains will be listed.
    domains = conn.listAllDomains(0)
    arrayName = []
    arrayState = []

    for domain in domains:

        arrayName.append(domain.name())
        arrayState.append(domain.state())  # return array of ['state','reason']

    arrayStateFiltred = []
    for state in arrayState:
        if state[0] == libvirt.VIR_DOMAIN_RUNNING:
            arrayStateFiltred.append("RUNNING")
        elif state[0] == libvirt.VIR_DOMAIN_PAUSED:
            arrayStateFiltred.append("PAUSED")
        elif state[0] == libvirt.VIR_DOMAIN_SHUTDOWN:
            arrayStateFiltred.append("SHUTDOWN")
        elif state[0] == libvirt.VIR_DOMAIN_SHUTOFF:
            arrayStateFiltred.append("SHUTOFF")
        else:
            arrayStateFiltred.append("UNKOWN")

    zippedList = zip(arrayName, arrayStateFiltred)
    for item in arrayStateFiltred:
        print(item)
    # Get List of scheduled tasks
    inspector = current_app.control.inspect()
    scheduled_tasks = inspector.scheduled('kvm')
    scheduled_tasks_param = []
    print(scheduled_tasks)
    for worker_name, tasks in scheduled_tasks.items():  # retreiving scheduled tasks
        for task in tasks:
            task_id = task['request']['id']
            task_name = task['request']['name']
            task_args = task['request']['args']
            task_kwargs = task['request']['kwargs']
            task_eta = task['eta']
            task = AsyncResult(task_id)  # for task state
            scheduled_tasks_param.append(
                {'name': task_name, 'args': task_args, 'kwargs': task_kwargs, 'eta': task_eta, 'status': task.state})

    return render(request, 'listeKvm.html', {"list": zippedList, 'scheduled_tasks': scheduled_tasks_param})


def start(request, name):
    conn = libvirt.open("qemu:///system")
    dom = conn.lookupByName(name)
    dom.create()
    return redirect('listeKvm')


def resume(requet, name):
    conn = libvirt.open("qemu:///system")
    dom = conn.lookupByName(name)
    dom.resume()
    return redirect('listeKvm')


def pause(request, name):
    conn = libvirt.open("qemu:///system")
    dom = conn.lookupByName(name)

    return redirect('listeKvm')


def shutdown(request, name):
    conn = libvirt.open("qemu:///system")
    dom = conn.lookupByName(name)
    dom.shutdown()
    return redirect('listeKvm')


def delete(request, name):
    conn = libvirt.open("qemu:///system")
    dom = conn.lookupByName(name)
    dom.undefine()
    return redirect('listeKvm')


def destroy(request, name):
    conn = libvirt.open("qemu:///system")
    dom = conn.lookupByName(name)
    dom.destroy()
    return redirect('listeKvm')
