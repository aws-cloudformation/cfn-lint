FROM public.ecr.aws/docker/library/python:3.13-alpine3.20

RUN pip install cfn-lint[full]
RUN pip install pydot

ENTRYPOINT ["cfn-lint"]
CMD ["--help"]
