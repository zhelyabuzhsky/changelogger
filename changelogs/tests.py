from django.test import TestCase
from django.urls import reverse


class ChangelogsIndexViewTests(TestCase):
    def test_success(self):
        response = self.client.get(reverse("changelogs:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Collector for your changelogs")
