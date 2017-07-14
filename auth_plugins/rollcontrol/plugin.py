"""
.. module: hubcommander.auth_plugins.rollcontrol.plugin
"""
import collections
import os
from pathlib import Path
import yaml

from hubcommander.bot_components.bot_classes import BotAuthPlugin
from hubcommander.bot_components.slack_comm import send_error  # send_info, send_success


class RollPlugin(BotAuthPlugin):
    def __init__(self, load_from_disk=True):
        super().__init__()
        if load_from_disk:
            self.permissions = yaml.load(Path(os.environ["ROLLCONTROL_CONFIG"]).read_text())

        # a mapping of command names to the function we use to parse their permissions
        self.command_mapping = {
            '!AddUserToTeam': self.add_user_to_team
        }

    def setup(*args, **kwargs):
        return

    def add_user_to_team(self, data):
        # right now, we assume the data is stored as "teams" -> org -> emails & teams
        # "!AddUserToTeam <UserGitHubId> <Org> <Team> <Role>"
        Command = collections.namedtuple("command", ['command', 'userid', 'org', 'team', 'role'])
        command = Command(*data["text"].split(" "))
        emails = []

        # load the org permissions
        for perm in self.permissions['teams'].get(command.org, []):
            # add all org-level email strings to the valid list
            if type(perm) is str:
                emails.append(perm)
            else:
                # if perm is the team-level permissions for the team we're adding to,
                # # add its email list to the org list
                emails = emails + perm.get(command.team, [])
        return emails

    # returns a list of users that have the right to run a given command
    def valid_users(self, data):
        command_name = data["text"].split(" ")[0]
        return self.command_mapping[command_name](data)

    def authenticate(self, data, user_data, **kwargs):
        try:
            valid = user_data["profile"]["email"] in self.valid_users(data)
        except Exception as e:
            send_error(data["channel"], str(e))
        if not valid:
            send_error(data["channel"],
                       "🙁 it looks like you don't have permission to do that.")
        return valid
