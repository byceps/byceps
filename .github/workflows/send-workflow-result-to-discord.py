#!/usr/bin/env python3

"""Notify Discord via webhook about workflow result."""

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "httpx",
# ]
# ///

from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
import json
import os
import subprocess

import httpx


Result = Enum('Result', ['success', 'failure'])


@dataclass
class RunDetails:
    run_number: str
    run_url: str
    ref_type: str
    ref_name: str
    commit_hash: str
    commit_subject: str
    commit_url: str
    result: Result


@dataclass
class ResultPresentation:
    color: str
    label: str


UNICODE_GREEN_HEART = '\U0001f49a'  # 💚
UNICODE_BROKEN_HEART = '\U0001f494'  # 💔

RESULT_PRESENTATIONS = {
    Result.success: ResultPresentation(
        color='3066993',
        label=f'{UNICODE_GREEN_HEART} SUCCESS',
    ),
    Result.failure: ResultPresentation(
        color='15158332',
        label=f'{UNICODE_BROKEN_HEART} FAILURE',
    ),
}


def main() -> None:
    args = _parse_args()
    result = Result[args.result]
    run_details = _get_run_details(result)
    webhook_data = _assemble_discord_payload(run_details)
    _call_webhook(args.webhook_url, webhook_data)
    print('Webhook called.')


def _parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        '--result', choices=[r.name for r in Result], required=True
    )
    parser.add_argument('--webhook-url', metavar='URL', required=True)
    return parser.parse_args()


def _get_run_details(result: Result) -> RunDetails:
    github_server_url = os.environ['GITHUB_SERVER_URL']  # "https://github.com"
    github_repository = os.environ['GITHUB_REPOSITORY']  # <user>/<repo>

    run_id = os.environ['GITHUB_RUN_ID']
    run_number = os.environ['GITHUB_RUN_NUMBER']
    run_url = f'{github_server_url}/{github_repository}/actions/runs/{run_id}'

    ref_name = os.environ['GITHUB_REF_NAME']  # "main"
    ref_type = os.environ['GITHUB_REF_TYPE']  # {"branch", "tag"}

    commit_hash = os.environ['GITHUB_SHA']
    commit_subject = _get_commit_subject(commit_hash)
    commit_url = f'{github_server_url}/{github_repository}/commit/{commit_hash}'

    return RunDetails(
        run_number=run_number,
        run_url=run_url,
        ref_type=ref_type,
        ref_name=ref_name,
        commit_hash=commit_hash,
        commit_subject=commit_subject,
        commit_url=commit_url,
        result=result,
    )


def _get_commit_subject(commit_hash: str) -> str:
    git_log_output = subprocess.run(
        ['/usr/bin/git', 'log', '-1', '--pretty=%s', commit_hash],
        capture_output=True,
        check=True,
        text=True,
    )
    return git_log_output.stdout


def _assemble_discord_payload(run_details: RunDetails) -> dict:
    commit_hash_short = run_details.commit_hash[:7]
    result_presentation = RESULT_PRESENTATIONS[run_details.result]

    return {
        'embeds': [
            {
                'color': result_presentation.color,
                'fields': [
                    {
                        'name': 'Run',
                        'value': f'[#{run_details.run_number}]({run_details.run_url})',
                        'inline': 'true',
                    },
                    {
                        'name': 'Result',
                        'value': result_presentation.label,
                        'inline': 'true',
                    },
                    {
                        'name': run_details.ref_type.title(),
                        'value': run_details.ref_name,
                        'inline': 'true',
                    },
                    {
                        'name': 'Commit',
                        'value': f'[{commit_hash_short}]({run_details.commit_url})',
                        'inline': 'true',
                    },
                    {
                        'name': 'Commit Message',
                        'value': run_details.commit_subject,
                        'inline': 'true',
                    },
                ],
            },
        ],
    }


def _call_webhook(url: str, data: dict) -> None:
    _print_webhook_request_body(data)
    response = httpx.post(url, json=data, timeout=10)
    _print_webhook_response(response)


def _print_webhook_request_body(data) -> None:
    print('Request body:')
    print(json.dumps(data, indent=2))


def _print_webhook_response(response) -> None:
    print('Response:')
    print(response)
    print(response.text)


if __name__ == '__main__':
    main()
