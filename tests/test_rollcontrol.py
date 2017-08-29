import yaml

from hubcommander.auth_plugins.rollcontrol.plugin import RollPlugin
from hubcommander.tests.test_slack_comm import actually_said

permissions = """
teams:
    first-organization:
        - alice@first.example.com
        - bob@first.example.com
        - first-team:
            - carol@first.example.com
        - second-team:
            - dan@first.example.com
            - eve@first.example.com
    second-organization:
        - zach@second.example.com
        - yulia@second.example.com
"""


def test_valid_users(slack_client):
    rp = RollPlugin(load_from_disk=False)
    rp.permissions = yaml.safe_load(permissions)

    # able to add to first-organization/first-team
    emails = rp.valid_users({
        "text": "!AddUserToTeam ghname first-organization first-team member"
    })

    assert sorted(emails) == sorted([
        "alice@first.example.com",
        "bob@first.example.com",
        "carol@first.example.com"
    ])

    # able to add to first-organization/second-team
    emails = rp.valid_users({
        "text": "!AddUserToTeam ghname first-organization second-team member"
    })
    assert sorted(emails) == sorted([
        "alice@first.example.com",
        "bob@first.example.com",
        "dan@first.example.com",
        "eve@first.example.com"
    ])

    # able to add to team with no special members
    emails = rp.valid_users({
        "text": "!AddUserToTeam ghname first-organization third-team member"
    })
    assert sorted(emails) == sorted([
        "alice@first.example.com",
        "bob@first.example.com"
    ])

    # no special members in any team in organization
    emails = rp.valid_users({
        "text": "!AddUserToTeam ghname second-organization a-team member"
    })
    assert sorted(emails) == sorted([
        "yulia@second.example.com",
        "zach@second.example.com"
    ])


def test_in_org(slack_client):
    rp = RollPlugin(load_from_disk=False)
    rp.permissions = yaml.load(permissions)
    # alice should be allowed, since she is listed in first-organization
    assert rp.authenticate(
        {"text": "!AddUserToTeam ghname first-organization third-team member"},
        {"profile": {"email": "alice@first.example.com"}}
    )


def test_not_in_org(slack_client):
    rp = RollPlugin(load_from_disk=False)
    rp.permissions = yaml.load(permissions)
    # felix should not be allowed, since he is neither listed in the
    # first-organization org nor in third-team
    assert not rp.authenticate(
        {
            "text": "!AddUserToTeam ghname first-organization newteam member",
            "channel": "chn"
        },
        {"profile": {"email": "felix@first.example.com"}}
    )

    actually_said(
        "chn",
        [{
            "text": "🙁 it looks like you don't have permission to do that.",
            "color": "danger"
        }],
        slack_client
    )


def test_in_team(slack_client):
    rp = RollPlugin(load_from_disk=False)
    rp.permissions = yaml.load(permissions)
    # dan should be allowed, since he is listed in the
    # first-organization/second-team
    assert rp.authenticate(
        {"text": "!AddUserToTeam user first-organization second-team member"},
        {"profile": {"email": "dan@first.example.com"}}
    )
