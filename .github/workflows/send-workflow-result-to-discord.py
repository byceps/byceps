#!/usr/bin/env python3

"""Notify Discord via webhook about workflow result."""

from argparse import ArgumentParser
import json
import os
import subprocess

import requests


RESULT_COLORS = {
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

    git_log_output = subprocess.run(
        ['git', 'log', '-1', '--pretty=%s', commit_hash],
        capture_output=True,
        check=True,
        text=True,
    )
    commit_subject = git_log_output.stdout

    run_id = os.environ['GITHUB_RUN_ID']
    run_number = os.environ['GITHUB_RUN_NUMBER']
    run_result = format_result(result)
    run_url = f'{github_server_url}/{github_repository}/actions/runs/{run_id}'

    result_color = RESULT_COLORS[result]

    return {
        'embeds': [
            {
                'color': result_color,
                'fields': [
                    {
                        'name': 'Run',
                        'value': f'[#{run_number}]({run_url})',
                        'inline': 'true',
                    },
                    {
                        'name': 'Result',
                        'value': run_result,
                        'inline': 'true',
                    },
                    {
                        'name': ref_type.title(),
                        'value': ref_name,
                        'inline': 'true',
                    },
                    {
                        'name': 'Commit',
                        'value': f'[{commit_hash_short}]({commit_url})',
                        'inline': 'true',
                    },
                    {
                        'name': 'Commit Message',
                        'value': commit_subject,
                        'inline': 'true',
                    },
                ],
            },
        ],
    }


def format_result(result: str) -> str:
    match result:
        case 'success':
            return '💚 SUCCESS'
        case 'failure':
            return '💔 FAILURE'
        case _:
            raise ValueError(f"Unknown result value '{result}'")


def call_webhook(url: str, data: dict) -> None:
    print('Request data:')
    print(json.dumps(data, indent=2))

    response = requests.post(url, json=data, timeout=10)

    print('Response:')
    print(response)
    print(response.text)


if __name__ == '__main__':
    main()
