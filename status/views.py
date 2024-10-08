import json
from django.shortcuts import render
from .models import Server, State, Alert
import subprocess
import re
from re import findall
from datetime import datetime
from django.http.response import JsonResponse
from django.http.request import HttpRequest


def add_db_status(r, state, server):
    status_obj = State(
        status = f"%loss/avg = {r['loss']}%/{r['avg']}",
        content = state,
        server = server,
    )
    status_obj.save()


def ping_servers(servers):
    status_summary = []
    command = ['fping', '-c1', '-t1000', *list(map(lambda item: item.ip, servers))]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    results = findall(r"^([0-9a-z.]+)\s*:\s*xmt\/rcv\/%loss\s+=\s+([0-9]+/[0-9]+/[0-9]+)%(?:,\s+min\/avg\/max\s+=\s+([0-9.]+\/[0-9.]+\/[0-9.]+))?$", stderr, re.MULTILINE)
    for result in results:
        r = {}
        r['ip'], a, b = result
        server = next(filter(lambda x: x.ip == r['ip'], servers))
        r['info'] = str(server)
        r['xmt'], r['rcv'], r['loss'] = a.split('/')
        if b:
            r['min'], r['avg'], r['max'] = b.split('/')
        else:
            r['min'] = r['avg'] = r['max'] = None
        #print('@@@', server)
        if r['avg'] == None:
            state = 'Not Connected'
            add_db_status(r, state, server)
        elif float(r['avg']) > 50:
            state = 'Slow'
            add_db_status(r, state, server)
        else:
            state = 'Connected'
            add_db_status(r, state, server)

        status_summary.append(r)
    return status_summary


def server_view(request):
    server = Server.objects.all()
    return render(request, 'server.html', {'server': server, 'alerts': alerts_data})


def content(req):
    server = Server.objects.all()
    status = ping_servers(server)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return JsonResponse({
        'status': status,
        'current_time': current_time,
    })


alerts_data = []
from django.views.decorators.csrf import csrf_exempt


def add_db_alerts(desc, status, server):
    alert_obj = Alert(
        status = status,
        describe = desc,
        server = server,
    )
    alert_obj.save()


def delete_alert(id):
    Alert.objects.filter(server_id=id).delete()


@csrf_exempt
 # Ensure this view only accepts POST requests
def webhook(req: HttpRequest):
    server = Server.objects.all()
    print('@@@', req.body)
    data = json.loads(req.body)
    for alert in data['alerts']:
        for i in range(len(server)):
            if alert['status'] == 'firing':
                if server[i].server == alert['labels']['nodename']:
                    info_disk = alert['labels']['alertname'] + " - Capacity: " + str(alert['values']['B'])
                    alert_info = {
                        'instance': alert['labels']['category'],
                        'name': server[i].server,
                        'capacity': alert['values']['B'],
                        'info': info_disk,
                    }
                    add_db_alerts(info_disk, alert['status'], server[i])
                    alerts_data.append(alert_info)
            else:
                print('@@@', server[i].id)
                delete_alert(server[i].id)
    return JsonResponse({'alerts': alerts_data})


def webhook_view(request):
    return render(request, 'index.html', {'alerts': alerts_data})
