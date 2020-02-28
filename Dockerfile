FROM python:3.8-alpine

RUN pip install cfn-lint

ENTRYPOINT ["cfn-lint"]
CMD ["--help"]
