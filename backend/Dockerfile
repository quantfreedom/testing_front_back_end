FROM public.ecr.aws/lambda/python:3.10

RUN pip install mangum

RUN pip install uvicorn

RUN pip install fastapi

COPY . ${LAMBDA_TASK_ROOT}

CMD [ "main.handler" ]