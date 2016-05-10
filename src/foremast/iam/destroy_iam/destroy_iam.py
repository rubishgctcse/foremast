"""Destroy any IAM related resources."""
import collections
import logging

import boto3

from ...utils import get_app_details
from ..resource_action import resource_action

LOG = logging.getLogger(__name__)


def destroy_iam(app='', env='dev', **_):
    """Destroy IAM Resources.

    Args:
        app (str): Spinnaker Application name.
        env (str): Deployment environment, i.e. dev, stage, prod.

    Returns:
        True upon successful completion.
    """
    session = boto3.Session(profile_name=env)
    client = session.client('iam')

    generated = get_app_details.get_details(env=env, app=app)
    app_details = collections.namedtuple('AppDetails',
                                         ['group', 'policy', 'profile', 'role',
                                          'user'])
    details = app_details(**generated.iam())

    LOG.debug('Application details: %s', details)

    resource_action(
        client,
        action='remove_user_from_group',
        log_format='Removed user from group: %(UserName)s ~> %(GroupName)s',
        GroupName=details.group,
        UserName=details.user)
    resource_action(client,
                    action='delete_user',
                    log_format='Destroyed user: %(UserName)s',
                    UserName=details.user)
    resource_action(client,
                    action='delete_group',
                    log_format='Destroyed group: %(GroupName)s',
                    GroupName=details.group)

    resource_action(client,
                    action='remove_role_from_instance_profile',
                    log_format='Destroyed Instance Profile from Role: '
                    '%(InstanceProfileName)s ~> %(RoleName)s',
                    InstanceProfileName=details.profile,
                    RoleName=details.role)
    resource_action(
        client,
        action='delete_instance_profile',
        log_format='Destroyed Instance Profile: %(InstanceProfileName)s',
        InstanceProfileName=details.profile)

    role_policies = []
    try:
        role_policies = resource_action(
            client,
            action='list_role_policies',
            log_format='Found Role Policies for %(RoleName)s.',
            RoleName=details.role)['PolicyNames']
    except TypeError:
        LOG.info('Role %s not found.', details.role)

    for policy in role_policies:
        resource_action(client,
                        action='delete_role_policy',
                        log_format='Removed Inline Policy from Role: '
                        '%(PolicyName)s ~> %(RoleName)s',
                        RoleName=details.role,
                        PolicyName=policy)

    attached_role_policies = []
    try:
        attached_role_policies = resource_action(
            client,
            action='list_attached_role_policies',
            log_format='Found attached Role Polices for %(RoleName)s.',
            RoleName=details.role)['AttachedPolicies']
    except TypeError:
        LOG.info('Role %s not found.', details.role)

    for policy in attached_role_policies:
        resource_action(client,
                        action='detach_role_policy',
                        log_format='Detached Policy from Role: '
                        '%(PolicyArn)s ~> %(RoleName)s',
                        RoleName=details.role,
                        PolicyArn=policy['PolicyArn'])

    resource_action(client,
                    action='delete_role',
                    log_format='Destroyed Role: %(RoleName)s',
                    RoleName=details.role)