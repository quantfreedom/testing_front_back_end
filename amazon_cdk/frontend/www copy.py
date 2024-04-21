from aws_cdk import Stack, Duration, RemovalPolicy
from constructs import Construct
from aws_cdk.aws_s3 import Bucket, BlockPublicAccess, BucketEncryption, ObjectOwnership
from aws_cdk.aws_s3_deployment import BucketDeployment, Source
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
    ErrorResponse,
    CloudFrontWebDistribution,
    ViewerCertificate,
    SSLMethod,
    SourceConfiguration,
    S3OriginConfig,
    Behavior,
)


class WWWTest(Stack):
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

        s3_bucket_src = Bucket(
            scope=self,
            id="www-test-quantfreedom",
            bucket_name="www-test-quantfreedom",
            public_read_access=True,
            block_public_access=allow_public_access,
            encryption=BucketEncryption.S3_MANAGED,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            object_ownership=ObjectOwnership.BUCKET_OWNER_PREFERRED,
            website_error_document="error.html",
            website_index_document="index.html",
        )

        BucketDeployment(
            scope=self,
            id="www-test-deploy",
            sources=[Source.asset("../../agtest/dist/agtest/browser")],
            destination_bucket=s3_bucket_src,
        )

        hosted_zone = HostedZone.from_hosted_zone_attributes(
            scope=self,
            id="www-test-Zone",
            zone_name="quantfreedom.com",
            hosted_zone_id="Z0694640FN257O67RS49",
        )

        zone_cert = CertificateValidation.from_dns(
            hosted_zone=hosted_zone,
        )

        # certificate = Certificate(
        #     scope=self,
        #     id="www-test-certificate",
        #     domain_name="www.test.quantfreedom.com",
        #     validation=zone_cert,
        # )

        certificate_arn = DnsValidatedCertificate(
            scope=self,
            id="www-test-cert",
            domain_name="www.test.quantfreedom.com",
            hosted_zone=hosted_zone,
            region="us-east-1",
            validation=zone_cert,
        ).certificate_arn

        # TODO maybe this is how to make the cerficate
        certificate = Certificate.from_certificate_arn(
            scope=self,
            id="www-test-certificate",
            certificate_arn=certificate_arn,
        )

        view_certificate = ViewerCertificate.from_acm_certificate(
            certificate=certificate,
            aliases=["www.test.quantfreedom.com"],
            ssl_method=SSLMethod.SNI,
            security_policy=SecurityPolicyProtocol.TLS_V1_2_2021,
        )

        behaviors = BehaviorOptions(
            allowed_methods=AllowedMethods.ALLOW_ALL,
            origin=S3Origin(s3_bucket_src),
            viewer_protocol_policy=ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        )

        error_response = [
            ErrorResponse(
                http_status=404,
                response_page_path="/error.html",
                ttl=Duration.seconds(amount=0),
                response_http_status=200,
            )
        ]

        # distribution = Distribution(
        #     scope=self,
        #     id="www-test-dist",
        #     certificate=certificate,
        #     minimum_protocol_version=SecurityPolicyProtocol.TLS_V1_2_2021,
        #     price_class=PriceClass.PRICE_CLASS_100,
        #     enable_logging=True,
        #     default_behavior=behaviors,
        #     domain_names=["www.test.quantfreedom.com"],
        #     error_responses=error_response,
        # )

        distribution = CloudFrontWebDistribution(
            scope=self,
            id="www-test-cloudfrontdist",
            origin_configs=[
                SourceConfiguration(
                    s3_origin_source=S3OriginConfig(
                        s3_bucket_source=s3_bucket_src,
                    ),
                    behaviors=[Behavior(is_default_behavior=True)],
                )
            ],
            viewer_certificate=ViewerCertificate.from_iam_certificate(
                "certificateId",
                aliases=["example.com"],
                security_policy=SecurityPolicyProtocol.SSL_V3,  # default
                ssl_method=SSLMethod.SNI,
            ),
        )

        the_target = RecordTarget.from_alias(CloudFrontTarget(distribution))

        ARecord(
            scope=self,
            id="www-test-record",
            record_name="www.test",
            zone=hosted_zone,
            target=the_target,
        )

        oai = OriginAccessIdentity(self, "OAI", comment="Connects CF with S3")
        s3_bucket_src.grant_read(oai)
        s3_bucket_src.grant_read_write(oai)

        BucketDeployment(
            scope=self,
            id="www-test-deploy",
            sources=[Source.asset("../../agtest/dist/agtest/browser")],
            destination_bucket=s3_bucket_src,
        )
