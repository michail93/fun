import json

from django.test import TestCase
from django.urls import reverse


class ApiTestCase(TestCase):
    def test_visited_links(self):
        url = reverse('api:visited-links')

        request_data = {
            'links': [
                'https://yandex.ru/news/region/ufa?mlid=1587627201.geo_172&msid=1587628156.73643.82882.78720&'
                'utm_medium=topnews_region&utm_source=morda_desktop',
                'google.com'
            ]
        }

        response = self.client.post(url, data=json.dumps(request_data), content_type="application/json")

        assert response.status_code == 200

    def test_visited_domain(self):
        url = reverse('api:visited-domains')

        response = self.client.get(url+"?from=100&to=200")

        assert response.status_code == 200
