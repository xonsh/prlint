import pulumi
from putils import opts, FauxOutput
from deplumi import Package, AwsgiHandler
from pulumi_aws import route53

config = pulumi.Config('prlint')

zone = FauxOutput(route53.get_zone(name='dingbots.dev'))

package = Package(
    'Prlint',
    sourcedir='prlint',
    **opts()
)

AwsgiHandler(
    'LintService',
    domain='lint.xonsh.dingbots.dev',
    zone=zone,
    package=package,
    func='__main__:main',
    environment={
        'variables': {
            'token': config.get('github-token'),  # Authenticates func->github
            'secret': config.get('github-secret'),  # Authenticates github->func
        }
    },
    **opts()
)

pulumi.export('api_url',  f"https://lint.xonsh.dingbots.dev/")
