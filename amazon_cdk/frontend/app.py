from aws_cdk import App, Environment

from redirect import RedirectTest
from www import WWWTest
from my_keys import AWS_ACCOUNT_NUMBER, AWS_REGION


env = Environment(
    account=AWS_ACCOUNT_NUMBER,
    region=AWS_REGION,
)
app = App()

WWWTest(
    scope=app,
    construct_id="www-test-quantfreedom",
    env=env,
)
app.synth()
