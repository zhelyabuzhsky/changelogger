import json
from datetime import datetime
from typing import Dict, List
from urllib.parse import urlparse

import requests
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .models import Project, Version


def send_email_notifications(version: Version) -> None:
    users = version.project.subscribers.all()

    for user in users:
        message = Mail(
            from_email=settings.NOREPLY_EMAIL_ADDRESS,
            to_emails=user.email,
            subject=f"It's new version of {version.project.title}",
            html_content=f'It\'s new version ({version.title}) of <a href="{version.project.url}">{version.project.title}</a>',
        )
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)


def _run_graphql_query(query: str, url: str, token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    request = requests.post(url, json={"query": query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(
            "Query failed to run by returning code of {}. {}".format(
                request.status_code, query
            )
        )


def fetch_github_project(project: Project) -> None:
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

    response = _run_graphql_query(
        query, "https://api.github.com/graphql", project.owner.github_token
    )

    releases: List[Dict] = response["data"]["repository"]["releases"]["edges"]

    for release in releases:
        if not Version.objects.filter(
            project=project, title=release["node"]["tagName"]
        ).exists():
            Version.objects.create(
                title=release["node"]["tagName"],
                date_time=datetime.strptime(
                    release["node"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                ),
                project=project,
                body=release["node"]["description"],
            )


def _get_gitlab_project_id(project: Project) -> int:
    query = """
        query {
            project(fullPath: "%s") {
                id
            }
        }
    """ % (
        urlparse(project.url).path[1:-1]
    )
    response = _run_graphql_query(
        query,
        f"https://{urlparse(project.url).netloc}/api/graphql",
        project.owner.gitlab_token,
    )
    return int(response["data"]["project"]["id"].split("/")[-1])


def _get_gitlab_project_releases(project: Project) -> List[Dict]:
    r = requests.get(
        f"https://{urlparse(project.url).netloc}/api/v4/projects/{_get_gitlab_project_id(project)}/releases",
        headers={"Private-Token": project.owner.gitlab_token},
    )
    data = json.loads(r.content.decode("utf8"))
    return data


def fetch_gitlab_project(project: Project) -> None:
    for release in _get_gitlab_project_releases(project):
        if not Version.objects.filter(project=project, title=release["name"]).exists():
            Version.objects.create(
                title=release["name"],
                date_time=datetime.fromisoformat(release["released_at"]),
                project=project,
                body=release["description"],
            )
