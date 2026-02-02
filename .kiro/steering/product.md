# Product Overview

## Purpose

cfn-lint validates AWS CloudFormation templates (YAML/JSON) against AWS CloudFormation resource provider schemas and best practices. It provides early feedback on template issues before deployment.

## Target Users

- DevOps engineers writing CloudFormation templates
- Platform teams enforcing infrastructure standards
- CI/CD pipelines requiring template validation
- Developers using AWS SAM (Serverless Application Model)

## Key Features

- Validates against official AWS resource schemas
- Checks resource properties, types, and values
- Supports CloudFormation intrinsic functions (Ref, GetAtt, Sub, etc.)
- Handles SAM transformations
- Extensible rule system for custom validation
- Multiple output formats (JSON, JUnit, SARIF)
- IDE integrations (VS Code, IntelliJ, Vim, etc.)

## Business Objectives

- Catch CloudFormation errors before deployment
- Enforce best practices and organizational standards
- Reduce deployment failures and rollback costs
- Provide fast feedback in development workflow
- Support custom validation requirements
