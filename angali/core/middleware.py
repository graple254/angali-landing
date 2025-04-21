import uuid
import requests
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import Visitor

class VisitorTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip_address = self.get_client_ip(request)
        location = self.get_location(ip_address)

        visitor_uuid = request.COOKIES.get('visitor_id')
        request.visitor_id = visitor_uuid  # We'll use this in views later

        if visitor_uuid:
            visitor = Visitor.objects.filter(uuid=visitor_uuid).first()
            if not visitor:
                visitor = Visitor.objects.create(
                    uuid=visitor_uuid,
                    ip_address=ip_address,
                    location=location
                )
        else:
            # Will be set in process_response
            request.new_visitor_uuid = str(uuid.uuid4())
            Visitor.objects.create(
                uuid=request.new_visitor_uuid,
                ip_address=ip_address,
                location=location
            )

    def process_response(self, request, response):
        if hasattr(request, 'new_visitor_uuid'):
            response.set_cookie('visitor_id', request.new_visitor_uuid, max_age=31536000)  # 1 year
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

    def get_location(self, ip_address):
        try:
            response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=5)
            data = response.json()
            if data.get('status') == 'fail':
                return 'Unknown'
            return f"{data.get('city')}, {data.get('country')}"
        except requests.exceptions.RequestException:
            return 'Unknown'
