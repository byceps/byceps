#!/usr/bin/env python3

"""Notify Discord via webhook about workflow result."""

from argparse import ArgumentParser
import json
import os
import subprocess

import requests


COLORS = {
    'success': '3066993',
    'failure': '15158332',
}


def main() -> None:
    args = parse_args()
    webhook_data = get_webhook_data(args.result)
    call_webhook(args.webhook_url, webhook_data)
    print('Webhook called.')


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('result', choices={'success', 'failure'})
    parser.add_argument('webhook_url')
    return parser.parse_args()


def get_webhook_data(result: str) -> dict:
    github_server_url = os.environ['GITHUB_SERVER_URL']  # "https://github.com"
    github_repository = os.environ['GITHUB_REPOSITORY']  # <user>/<repo>

    ref_name = os.environ['GITHUB_REF_NAME']  # "main"
    ref_type = os.environ['GITHUB_REF_TYPE']  # {"branch", "tag"}

    commit_hash = os.environ['GITHUB_SHA']
    commit_hash_short = commit_hash[:7]
    commit_url = f'{github_server_url}/{github_repository}/commit/{commit_hash}'

    commit_subject = subprocess.getoutput(
        f'git log -1 --pretty="%s" {commit_hash}'
    )

    run_id = os.environ['GITHUB_RUN_ID']
    run_number = os.environ['GITHUB_RUN_NUMBER']
    run_result = result.upper()
    run_url = f'{github_server_url}/{github_repository}/actions/runs/{run_id}'

    color = COLORS[result]

    return {
        'embeds': [
            {
                'color': color,
                'author': {
                    'name': f'Run #{run_number} – {run_result}',
                    'url': run_url,
                },
                'title': commit_subject,
                'fields': [
                    {
                        'name': 'Commit',
                        'value': f'[{commit_hash_short}]({commit_url})',
                        'inline': 'true',
                    },
                    {
                        'name': ref_type.title(),
                        'value': ref_name,
                        'inline': 'true',
                    },
                ],
            },
        ],
    }


def call_webhook(url: str, data: dict) -> None:
    print('Request data:')
    print(json.dumps(data, indent=2))

    response = requests.post(url, json=data)

    print('Response:')
    print(response)


if __name__ == '__main__':
    main()
