from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Visitor, VisitorSession, PageInteraction
import json
from unittest.mock import patch
import uuid


class VisitorTrackingTests(TestCase):
    def setUp(self):
        # Create a test client for simulating HTTP requests
        self.client = Client()

        # Create a visitor manually for testing the session tracking
        self.visitor_uuid = uuid.uuid4()
        self.visitor = Visitor.objects.create(
            uuid=self.visitor_uuid,
            ip_address='192.168.0.1',
            location='Test City, Test Country',
            visit_date=timezone.now()
        )
        self.visitor_uuid_str = str(self.visitor_uuid)

    @patch('requests.get')
    def test_visitor_tracking_middleware_new_visitor(self, mock_get):
        # Mock the location fetching based on IP
        mock_get.return_value.json.return_value = {
            'status': 'success',
            'city': 'Test City',
            'country': 'Test Country'
        }

        # Simulate a new request that does not have a visitor_id in cookies
        response = self.client.get('/')
        
        # Check if the new visitor_id is set in cookies
        self.assertIn('visitor_id', response.cookies)
        
        # Check if the new visitor is created in the database
        visitor_uuid = response.cookies['visitor_id'].value
        visitor = Visitor.objects.get(uuid=visitor_uuid)
        self.assertEqual(visitor.ip_address, '127.0.0.1')  # Client uses 127.0.0.1 for tests

    @patch('requests.get')
    def test_visitor_tracking_middleware_existing_visitor(self, mock_get):
        # Mock the location fetching based on IP
        mock_get.return_value.json.return_value = {
            'status': 'success',
            'city': 'Test City',
            'country': 'Test Country'
        }

        # Set a visitor_id cookie for an existing visitor
        self.client.cookies['visitor_id'] = self.visitor_uuid_str

        # Simulate a request for an existing visitor
        response = self.client.get('/')

        # The visitor should not be created again
        visitor = Visitor.objects.get(uuid=self.visitor_uuid_str)
        self.assertEqual(visitor.ip_address, '192.168.0.1')

    def test_track_start_view(self):
            # Set the visitor_id cookie
            self.client.cookies['visitor_id'] = self.visitor_uuid_str

            # Set up the data for the track_start view
            session_data = {
                  'session_id': 'test-session-id',
                  'referrer': 'https://example.com',
                  'user_agent': 'Mozilla/5.0',
                  'start_time': timezone.now().isoformat()
            }

            # Simulate the POST request to start the session
            response = self.client.post(
                  reverse('track_start'),
                  data=json.dumps(session_data),
                  content_type='application/json'
            )

            # Print response content if test fails
            if response.status_code != 200:
                  print(f"Response content: {response.content}")

            # Check if the response is as expected
            self.assertEqual(response.status_code, 200)
            self.assertJSONEqual(
                  str(response.content, 'utf8'),
                  {"status": "started"}
            )

            # Check if the VisitorSession was created
            session = VisitorSession.objects.get(session_id='test-session-id')
            self.assertEqual(str(session.visitor.uuid), self.visitor_uuid_str)
            self.assertEqual(session.referrer, 'https://example.com')
            self.assertEqual(session.user_agent, 'Mozilla/5.0')

    def test_track_end_view(self):
        # Create a dummy session to update with the track_end view
        visitor_session = VisitorSession.objects.create(
            visitor=self.visitor,
            session_id='test-session-id',
            referrer='https://example.com',
            user_agent='Mozilla/5.0',
            start_time=timezone.now()
        )

        # Set up the data for the track_end view
        end_data = {
            'visitor_id': self.visitor_uuid_str,  # Added visitor_id to request data
            'session_id': 'test-session-id',
            'end_time': timezone.now().isoformat(),
            'duration_seconds': 120,
            'sections': ['section-1', 'section-2'],
            'max_scroll': 80
        }

        # Simulate the POST request to end the session
        response = self.client.post(
            reverse('track_end'),
            data=json.dumps(end_data),
            content_type='application/json'
        )

        # Check if the response is as expected
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, 'utf8'),
            {"status": "ended"}
        )

        # Check if the session has been updated
        session = VisitorSession.objects.get(session_id='test-session-id')
        self.assertEqual(session.duration_seconds, 120)

        # Check if the PageInteraction records were created
        interactions = PageInteraction.objects.filter(session=session)
        self.assertEqual(interactions.count(), 2)
        self.assertEqual(interactions[0].section_id, 'section-1')
        self.assertEqual(interactions[1].section_id, 'section-2')

    def test_visitor_model_creation(self):
        # Create a new visitor manually
        new_uuid = uuid.uuid4()
        visitor = Visitor.objects.create(
            uuid=new_uuid,
            ip_address='192.168.1.1',
            location='Some City, Some Country',
            visit_date=timezone.now()
        )

        # Verify that the visitor is created
        self.assertEqual(visitor.uuid, new_uuid)
        self.assertEqual(visitor.ip_address, '192.168.1.1')
        self.assertEqual(visitor.location, 'Some City, Some Country')

    def test_visitor_session_creation(self):
        # Create a session for the visitor
        session = VisitorSession.objects.create(
            visitor=self.visitor,
            session_id='test-session-id',
            referrer='https://example.com',
            user_agent='Mozilla/5.0',
            start_time=timezone.now()
        )

        # Verify that the session is created
        self.assertEqual(session.session_id, 'test-session-id')
        self.assertEqual(str(session.visitor.uuid), self.visitor_uuid_str)
        self.assertEqual(session.referrer, 'https://example.com')
        self.assertEqual(session.user_agent, 'Mozilla/5.0')