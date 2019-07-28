import pulumi
from putils import opts, FauxOutput
from deplumi import Package, AwsgiHandler
from pulumi_aws import route53

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
    func='__main__:lint',
    **opts()
)

pulumi.export('api_url',  f"https://lint.xonsh.dingbots.dev/")
