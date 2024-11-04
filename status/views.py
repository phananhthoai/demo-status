import json
from django.shortcuts import render
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from status.models import Alert

def handle_alert(data):
    print(f'Alert: {data}')
    alert, is_created = Alert.objects.get_or_create(fingerprint=data['fingerprint'], defaults={
        'labels': data['labels'],
        'annotations': data['annotations'],
    })
    alert.set_status(data['status'].upper())
    alert.values = data['values']
    alert.save()

    return {
        'success': True,
    }


def handle_alerts(items):
    results = []
    for item in items:
        results.append(handle_alert(item))
    return results


@csrf_exempt
# Ensure this view only accepts POST requests
def webhook(req: HttpRequest):
    data = json.loads(req.body)
    try:
        return JsonResponse({
            'success': True,
            'results': handle_alerts(data['alerts']),
        })
    except Exception as ex:
        return JsonResponse(status=500, data={
            'success': False,
            'error': str(ex)
        })



@csrf_exempt
def view(request):
    alerts = Alert.objects.all().order_by('-created_at')[:10]
    context = {
        'status': alerts,
    }
    return render(request, 'index.html', context)
