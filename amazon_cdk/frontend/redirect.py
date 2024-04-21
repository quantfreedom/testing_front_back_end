from aws_cdk import Stack, RemovalPolicy
from constructs import Construct
from aws_cdk.aws_s3 import Bucket, BlockPublicAccess, BucketEncryption, ObjectOwnership, RedirectTarget
from aws_cdk.aws_route53 import HostedZone, ARecord, RecordTarget
from aws_cdk.aws_route53_targets import CloudFrontTarget
from aws_cdk.aws_certificatemanager import Certificate, CertificateValidation, DnsValidatedCertificate
from aws_cdk.aws_cloudfront_origins import S3Origin
from aws_cdk.aws_cloudfront import (
    OriginAccessIdentity,
    ViewerProtocolPolicy,
    SecurityPolicyProtocol,
    AllowedMethods,
    Distribution,
    PriceClass,
    BehaviorOptions,
)


class RedirectTest(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        allow_public_access = BlockPublicAccess(
            block_public_acls=False,
            ignore_public_acls=False,
            block_public_policy=False,
            restrict_public_buckets=False,
        )

        the_bucket = Bucket(
            scope=self,
            id="redirect-test-quantfreedom",
            bucket_name="redirect-test-quantfreedom",
            public_read_access=True,
            block_public_access=allow_public_access,
            encryption=BucketEncryption.S3_MANAGED,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            object_ownership=ObjectOwnership.BUCKET_OWNER_PREFERRED,
            website_redirect=RedirectTarget(host_name="www.test.quantfreedom.com"),
        )

        hosted_zone = HostedZone.from_hosted_zone_attributes(
            scope=self,
            id="redirect-test-zone",
            zone_name="quantfreedom.com",
            hosted_zone_id="Z0694640FN257O67RS49",
        )

        zone_cert = CertificateValidation.from_dns(
            hosted_zone=hosted_zone,
        )

        # the_certificate = Certificate(
        #     scope=self,
        #     id="redirect-test-certificate",
        #     domain_name="test.quantfreedom.com",
        #     validation=zone_cert,
        # )

        dns_certificate = DnsValidatedCertificate(
            scope=self,
            id="www-test-cert",
            domain_name="www.test.quantfreedom.com",
            hosted_zone=hosted_zone,
            region="us-east-1",
            validation=zone_cert,
        ).certificate_arn

        behaviors = BehaviorOptions(
            allowed_methods=AllowedMethods.ALLOW_ALL,
            origin=S3Origin(the_bucket),
            viewer_protocol_policy=ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        )

        distribution = Distribution(
            scope=self,
            id="redirect-test-dist",
            certificate=dns_certificate,
            minimum_protocol_version=SecurityPolicyProtocol.TLS_V1_2_2021,
            price_class=PriceClass.PRICE_CLASS_100,
            enable_logging=True,
            default_behavior=behaviors,
            domain_names=["test.quantfreedom.com"],
        )

        the_target = RecordTarget.from_alias(CloudFrontTarget(distribution))

        ARecord(
            scope=self,
            id="redirect-test-record",
            record_name="test",
            zone=hosted_zone,
            target=the_target,
        )

        oai = OriginAccessIdentity(
            self,
            "OAI",
            comment="Connects CF with S3",
        )
        the_bucket.grant_read(oai)
        the_bucket.grant_read_write(oai)
