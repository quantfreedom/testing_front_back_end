import os
from my_keys import AWS_ACCOUNT_NUMBER, AWS_REGION
from constructs import Construct

from aws_cdk import App, CfnOutput, Environment, Stack, RemovalPolicy
from aws_cdk.aws_cloudfront_origins import S3Origin
from aws_cdk.aws_s3_deployment import BucketDeployment, Source
from aws_cdk.aws_route53 import HostedZone, ARecord, RecordTarget
from aws_cdk.aws_route53_targets import CloudFrontTarget
from aws_cdk.aws_certificatemanager import DnsValidatedCertificate
from aws_cdk.aws_cloudfront import (
    OriginAccessIdentity,
    ViewerProtocolPolicy,
    SecurityPolicyProtocol,
    ErrorResponse,
    BehaviorOptions,
    AllowedMethods,
    PriceClass,
    Distribution,
)
from aws_cdk.aws_s3 import (
    Bucket,
    BlockPublicAccess,
    BucketEncryption,
    ObjectOwnership,
    RedirectTarget,
    RedirectProtocol,
)


# this all works with aws-cdk 2.139.0
class StaticWebsiteStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(
            scope,
            construct_id,
            **kwargs,
        )

        s3_block_public_access = BlockPublicAccess(
            block_public_acls=False,
            ignore_public_acls=False,
            block_public_policy=False,
            restrict_public_buckets=False,
        )

        s3_bucket_src = Bucket(
            scope=self,
            id="s3_bucket_src",
            bucket_name="www.blahblah.quantfreedom.com",
            public_read_access=True,
            block_public_access=s3_block_public_access,
            encryption=BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            object_ownership=ObjectOwnership.BUCKET_OWNER_PREFERRED,
            website_error_document="error.html",
            website_index_document="index.html",
        )

        web_redirect = RedirectTarget(
            host_name=s3_bucket_src.bucket_website_domain_name,
            protocol=RedirectProtocol.HTTPS,
        )

        Bucket(
            scope=self,
            id="s3_bucket_redirect",
            bucket_name="blahblah.quantfreedom.com",
            encryption=BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            object_ownership=ObjectOwnership.BUCKET_OWNER_PREFERRED,
            website_redirect=web_redirect,
        )

        hosted_zone = HostedZone.from_lookup(
            scope=self,
            id="MyZone",
            domain_name="quantfreedom.com",
        )

        certificate_dns_validation = DnsValidatedCertificate(
            scope=self,
            id="Certificate",
            domain_name="www.blahblah.quantfreedom.com",
            hosted_zone=hosted_zone,
            region="us-east-1",
        )

        certificate_dns_validation_redirect = DnsValidatedCertificate(
            scope=self,
            id="Redirect_Certificate",
            domain_name="blahblah.quantfreedom.com",
            hosted_zone=hosted_zone,
            region="us-east-1",
        )

        behaviour = BehaviorOptions(
            allowed_methods=AllowedMethods.ALLOW_ALL,
            origin=S3Origin(s3_bucket_src),
            viewer_protocol_policy=ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        )

        error_response = [
            ErrorResponse(
                http_status=404,
                response_page_path="/index.html",
                response_http_status=200,
            )
        ]

        distribution = Distribution(
            scope=self,
            id="cloudFrontDistribution",
            certificate=certificate_dns_validation,
            minimum_protocol_version=SecurityPolicyProtocol.TLS_V1_2_2021,
            price_class=PriceClass.PRICE_CLASS_100,
            enable_logging=True,
            default_behavior=behaviour,
            domain_names=["www.blahblah.quantfreedom.com"],
            error_responses=error_response,
        )

        redirect_distribution = Distribution(
            scope=self,
            id="redirect_cloudFrontDistribution",
            certificate=certificate_dns_validation_redirect,
            minimum_protocol_version=SecurityPolicyProtocol.TLS_V1_2_2021,
            price_class=PriceClass.PRICE_CLASS_100,
            enable_logging=True,
            default_behavior=behaviour,
            domain_names=["blahblah.quantfreedom.com"],
            error_responses=error_response,
        )

        source_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../..",
                "frontend/dist/frontend/browser",
            )
        )

        BucketDeployment(
            scope=self,
            id="www-blahblah-deploy",
            sources=[Source.asset(source_path)],
            destination_bucket=s3_bucket_src,
            distribution=distribution,
            distribution_paths=["/*"],
        )

        ARecord(
            scope=self,
            id="a-record",
            record_name="www.blahblah",
            zone=hosted_zone,
            target=RecordTarget.from_alias(CloudFrontTarget(distribution)),
        )

        ARecord(
            scope=self,
            id="redirect-a-record",
            record_name="blahblah",
            zone=hosted_zone,
            target=RecordTarget.from_alias(CloudFrontTarget(redirect_distribution)),
        )

        oai = OriginAccessIdentity(
            scope=self,
            id="OAI",
            comment="Connects CF with S3",
        )
        s3_bucket_src.grant_read(oai)
        s3_bucket_src.grant_read_write(oai)

        redirect_oai = OriginAccessIdentity(
            scope=self,
            id="redirect-OAI",
            comment="Connects CF with S3",
        )
        s3_bucket_src.grant_read(redirect_oai)
        s3_bucket_src.grant_read_write(redirect_oai)

        CfnOutput(
            scope=self,
            id="Website URL",
            value="https://www.blahblah.quantfreedom.com",
            description="The Website URL",
        )


env = Environment(
    account=AWS_ACCOUNT_NUMBER,
    region=AWS_REGION,
)
app = App()

StaticWebsiteStack(
    scope=app,
    construct_id="blah-test-quantfreedom",
    env=env,
)

app.synth()
