FROM python:3.11-alpine

RUN apk add --no-cache cargo
RUN pip install cfn-lint
RUN pip install pydot

ENTRYPOINT ["cfn-lint"]
CMD ["--help"]
