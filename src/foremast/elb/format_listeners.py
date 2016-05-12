"""Add the appropriate ELB Listeners."""
import logging

from ..utils import get_env_credential

LOG = logging.getLogger(__name__)


def format_listeners(elb_settings=None, env='dev'):
    """Format ELB Listeners into standard list.

    Args:
        elb_settings (dict): ELB settings including ELB Listeners to add,
            e.g.

            # old
            {
                "certificate": null,
                "i_port": 8080,
                "lb_port": 80,
                "subnet_purpose": "internal",
                "target": "HTTP:8080/health"
            }

            # new
            {
                "ports": [
                    {
                        "instance": "HTTP:8080",
                        "loadbalancer": "HTTP:80"
                    },
                    {
                        "certificate": "cert_name",
                        "instance": "HTTP:8443",
                        "loadbalancer": "HTTPS:443"
                    }
                ],
                "subnet_purpose": "internal",
                "target": "HTTP:8080/health"
            }

        env (str): Environment to find the Account Number for.

    Returns:
        list: ELB Listeners formatted into dicts for Spinnaker.

            [
                {
                    'externalPort': 80,
                    'externalProtocol': 'HTTP',
                    'internalPort': 8080,
                    'internalProtocol': 'HTTP',
                    'sslCertificateId': None
                },
                ...
            ]
    """
    LOG.debug('ELB settings:\n%s', elb_settings)

    credential = get_env_credential(env=env)
    account = credential['accountId']

    listeners = []

    if 'ports' in elb_settings:
        for listener in elb_settings['ports']:
            cert_name = format_cert_name(
                account=account,
                certificate=listener.get('certificate', None))

            lb_proto, lb_port = listener['loadbalancer'].split(':')
            i_proto, i_port = listener['instance'].split(':')

            elb_data = {
                'externalPort': int(lb_port),
                'externalProtocol': lb_proto.upper(),
                'internalPort': int(i_port),
                'internalProtocol': i_proto.upper(),
                'sslCertificateId': cert_name,
            }

            listeners.append(elb_data)
    else:
        listeners = [{
            'externalPort': int(elb_settings['lb_port']),
            'externalProtocol': elb_settings['lb_proto'],
            'internalPort': int(elb_settings['i_port']),
            'internalProtocol': elb_settings['i_proto'],
            'sslCertificateId': elb_settings['certificate'],
        }]

    for listener in listeners:
        LOG.info('ELB Listener:\n'
                 'loadbalancer %(externalProtocol)s:%(externalPort)d\n'
                 'instance %(internalProtocol)s:%(internalPort)d\n'
                 'certificate: %(sslCertificateId)s', listener)
    return listeners


def format_cert_name(account='', certificate=None):
    """Format the SSL certificate name into ARN for ELB.

    Args:
        account (str): Account number for ARN.
        certificate (str): Name of SSL certificate.

    Returns:
        None: Certificate is not desired.
        str: Fully qualified ARN for SSL certificate.
    """
    cert_name = None

    if certificate:
        if certificate.startswith('arn'):
            cert_name = certificate
        else:
            cert_name = ('arn:aws:iam::{account}:server-certificate/'
                         '{name}'.format(account=account,
                                         name=certificate))
    LOG.debug('Certificate name: %s', cert_name)

    return cert_name
