import os
from datetime import datetime
from typing import List, Dict

import requests
from django.core.management.base import BaseCommand

from ...models import Project, Version


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        def fetch_github_project(project: Project) -> None:
            def run_github_grahql_query(query: str) -> Dict:
                headers = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}
                request = requests.post(
                    "https://api.github.com/graphql",
                    json={"query": query},
                    headers=headers,
                )
                if request.status_code == 200:
                    return request.json()
                else:
                    raise Exception(
                        "Query failed to run by returning code of {}. {}".format(
                            request.status_code, query
                        )
                    )

            query = """
            {
              repository(owner: "%s", name: "%s") {
                releases(last: 10) {
                  edges {
                    node {
                      tagName
                      publishedAt
                      description
                    }
                  }
                }
              }
            }
            """ % (
                project.repository_owner,
                project.repository_name,
            )

            response = run_github_grahql_query(query)

            releases: List[Dict] = response["data"]["repository"]["releases"]["edges"]

            for release in releases:
                Version.objects.create(
                    title=release["node"]["tagName"],
                    date_time=datetime.strptime(
                        release["node"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    project=project,
                    body=release["node"]["description"],
                )

        projects = Project.objects.all()

        for project in projects:
            fetch_github_project(project)

        self.stdout.write(self.style.SUCCESS("Successfully fetched changlogs"))
