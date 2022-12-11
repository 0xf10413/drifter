from django.http import HttpResponse
from django.shortcuts import render
from . import models, forms
import pydantic
import logging
import datetime as dt

def index(request):
    context = {
        "servers": models.Server.objects.all(),
    }
    return render(request, "webui/index.html.j2", context)

class PlayDuration(pydantic.BaseModel):
    start: dt.datetime

class PlayMetadata(pydantic.BaseModel):
    name: str
    duration: PlayDuration

class TaskHost(pydantic.BaseModel):
    changed: bool

class TaskData(pydantic.BaseModel):
    name: str

class Task(pydantic.BaseModel):
    hosts: dict[str, TaskHost]
    task: TaskData

class Play(pydantic.BaseModel):
    play: PlayMetadata
    tasks: list[Task]

class CustomStat(pydantic.BaseModel):
    mach_type: str
    phase: str

class PlaybookOutput(pydantic.BaseModel):
    plays: list[Play]
    custom_stats: dict[str, CustomStat]

def upload(request):
    if request.method == "POST":
        form = forms.UploadForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "webui/upload.html.j2", context)
    
        playbook_output = PlaybookOutput.parse_raw(request.FILES['file_name'].read())
        logging.critical("Got playbook: %s", playbook_output)
        handle_new_ansible_input(playbook_output)


    # Prepare a new upload
    form = forms.UploadForm()
    context = {
        "form": form,
    }
    return render(request, "webui/upload.html.j2", context)

def handle_new_ansible_input(output: PlaybookOutput) -> None:
    # Identify the machines, using custom stats
    stats_per_host: dict[str, models.NbChanges] = {}
    play_start = output.plays[0].play.duration.start
    for hostname, stat in output.custom_stats.items():
        logging.warning("Detected host %s, which is a %s in phase %s", hostname, stat.mach_type, stat.phase)
        # Update machine configuration
        mach_type, _ = models.MachType.objects.update_or_create(name=stat.mach_type)
        phase, _ = models.Phase.objects.update_or_create(name=stat.phase)
        host, _ = models.Server.objects.update_or_create(mach_type=mach_type, phase=phase, name=hostname)
        
        # Retrieve change statistic corresponding to this playbook, if any, and reinitialize it
        nb_changes, _ = models.NbChanges.objects.get_or_create(server=host, datetime=play_start)
        nb_changes.nb_change = 0
        stats_per_host[hostname] = nb_changes

    # Update change statistic
    for play in output.plays:
        for task in play.tasks:
            for hostname, host in task.hosts.items():
                if hostname in stats_per_host and host.changed:
                    stats_per_host[hostname].nb_change += 1

    # Save everything
    for stat in stats_per_host.values():
        stat.save()

