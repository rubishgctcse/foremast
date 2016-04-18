# Spinnaker Pipes

This repository will contain scripts for all of the "pipes" tasks for Spinnaker
deployments.

## Basic Task Overview

These are designed to be loosely coupled applications and we will continue to
update this README as the project grows.

### Implementation

1. Create logical Spinnaker app (triggered by Git Hook)
1. Call downstream Job to manage infrastructure
1. Read configurations from `application-master-{env}.json` and `pipeline.json`
1. Create/modify IAM Profile and Role
1. Create/skip S3 Archaius application.properties file
1. Create/modify Security Groups
1. Create/modify ELB
1. Create DNS record to ELB
1. Create/modify application pipeline

### Not Used

1. Create/modify server group/ASG

## Technology Used

See [requirements](requirements.txt) for package listing.

1. Python3
1. Jinja2 templating
1. Python Requests
1. Argparse for arguments
1. Boto3 (direct AWS access to parts not exposed by Spinnaker, e.g. S3)

## Runway Updates

To begin using the Spinnaker deployment system, a few changes will be needed to
the `runway` directory to trigger the tooling.

### runway/dsl.groovy

Remove any downstream Jobs as Spinnaker will poll for the main Job for
completion.

```groovy
job("$SRC_JOB") {
    publishers {
        archiveArtifacts('runway/FS_ROOT/etc/gogo/jenkins_vars, RPMS/x86_64/*.rpm')
        downstreamParameterized {
            // Delete
        }
    }
}
```

### runway/pipeline.json

A new file, `pipeline.json`, will be needed in the `runway` directory to trigger
the creation of the Spinnaker Application and Pipelines for each deployment
environment.

#### Minimum

```json
{
    "deployment": "spinnaker"
}
```

#### Example Deployment Environments Override

```json
{
    "deployment": "spinnaker",
    "env": [
        "stage",
        "prod"
    ]
}
```

Each deployment environment specified in the `pipeline.json` file will need an
accompanying `application-master-{env}.json` file.

### runway/application-master-{env}.json

To determine which regions to deploy to, a new `regions` key can be used to
override the default of `us-east-1`.

```json
{
    "regions": [
        "us-east-1",
        "us-west-2"
    ]
}
```
