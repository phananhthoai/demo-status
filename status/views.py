from django.shortcuts import render
from .models import Servers
import subprocess
import re
from datetime import datetime
from django.http.response import JsonResponse



def ping_servers(servers):
    status_summary = []
    command = ['fping', '-c1', '-t1000', *list(map(lambda item: item.ip, servers))]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    results = re.findall(r"^([0-9a-z.]+)\s*:\s*xmt\/rcv\/%loss\s+=\s+([0-9]+/[0-9]+/[0-9]+)%(?:,\s+min\/avg\/max\s+=\s+([0-9.]+\/[0-9.]+\/[0-9.]+))?$", stderr, re.MULTILINE)
    for result in results:
        r = {}
        r['ip'], a, b = result
        server = next(filter(lambda x: x.ip == r['ip'], servers))
        r['info'] = str(server)
        r['xmt'], r['rcv'], r['loss'] = a.split('/')
        if b:
            r['min'], r['avg'], r['max'] = b.split('/')
        status_summary.append(r)
    return status_summary


def server_view(request):
    server = Servers.objects.all()
    return render(request, 'server.html', {'server': server})


def content(req):
    server = Servers.objects.all()
    status = ping_servers(server)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return JsonResponse({
        'status': status,
        'current_time': current_time,
    })
