"""
.. module: hubcommander.auth_plugins.rollcontrol.plugin
"""
from collections import namedtuple, defaultdict
import os
from pathlib import Path
import json
import yaml

from prometheus_client import Counter, start_http_server

from hubcommander.bot_components.bot_classes import BotAuthPlugin
from hubcommander.bot_components.slack_comm import send_error  # send_info, send_success


class RollPlugin(BotAuthPlugin):
    def __init__(self, load_from_disk=True):
        super().__init__()
        if os.getenv("PROMETHEUS_PORT"):
            # start serving prometheus over port
            start_http_server(int(os.getenv("PROMETHEUS_PORT")))
            self.counter = Counter('auth_requests_total', 'Authentication Requests', ['success'])

        if load_from_disk:
            self.permissions = yaml.safe_load(Path(os.environ["ROLLCONTROL_CONFIG"]).read_text())

        """
        A mapping of command names to the function we use to parse their
        permissions. Permissions functions take the data parameter from
        Hubcommander and return a list of email addresses of users that
        have permission to run that command.

        By default, an unknown command returns no valid email addresses.
        """
        self.command_mapping = defaultdict(lambda: lambda x: [], {
            '!AddUserToTeam': self.add_user_to_team
        })

    def setup(*args, **kwargs):
        return

    def add_user_to_team(self, data):
        # right now, we assume the data is stored as "teams" -> org -> emails & teams
        # "!AddUserToTeam <UserGitHubId> <Org> <Team> <Role>"
        Command = namedtuple("command", ['command', 'userid', 'org', 'team', 'role'])
        command = Command(*data["text"].split())
        emails = []

        # load the org permissions
        for perm in self.permissions['teams'].get(command.org, []):
            # add all org-level email strings to the valid list
            if isinstance(perm, str):
                emails.append(perm)
            else:
                # if perm is the team-level permissions for the team we're adding to,
                # # add its email list to the org list
                emails = emails + perm.get(command.team, [])
        return emails

    # returns a list of users that have the right to run a given command
    def valid_users(self, data):
        command_name = data["text"].split()[0]
        return self.command_mapping[command_name](data)

    def authenticate(self, data, user_data, **kwargs):
        valid = (not data.get('bot_id')) and user_data["profile"]["email"] in self.valid_users(data)
        if not valid:
            send_error(data["channel"],
                       "🙁 it looks like you don't have permission to do that.")
        self.log(data, user_data, valid)
        return valid

    def log(self, data, user_data, valid):
        print(json.dumps({
            "user": user_data["name"],
            "email": user_data["profile"]["email"],
            "command":  data["text"],
            "authorized": valid,
            "message_time": data["ts"],
            "bot": data.get("bot_id", False)
        }))
        if os.getenv("PROMETHEUS_PORT"):
            self.counter.labels(success="{}".format(valid)).inc()
