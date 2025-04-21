from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import *

@csrf_exempt
def track_start(request):
    data = json.loads(request.body)
    visitor_id = request.COOKIES.get('visitor_id')

    if not visitor_id:
        return JsonResponse({"error": "Missing visitor ID"}, status=400)

    visitor = Visitor.objects.filter(uuid=visitor_id).first()
    if visitor:
        VisitorSession.objects.create(
            visitor=visitor,
            session_id=data['session_id'],
            referrer=data.get('referrer', ''),
            user_agent=data.get('user_agent', '')
        )
    return JsonResponse({"status": "started"})


@csrf_exempt
def track_end(request):
    data = json.loads(request.body)
    session = VisitorSession.objects.filter(session_id=data['session_id']).first()

    if session:
        session.end_time = data['end_time']
        session.duration_seconds = data['duration_seconds']
        session.save()

        for section_id in data['sections']:
            PageInteraction.objects.create(
                session=session,
                section_id=section_id,
                scroll_depth=data['max_scroll']
            )
    return JsonResponse({"status": "ended"})

