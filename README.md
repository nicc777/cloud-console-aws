# A reference implementation for AWS Services in `cloud-console`

AWS Integration for the [`cloud-console`](https://github.com/nicc777/cloud-console) project. 

Integration is done via the [`cloud-console-common`](https://github.com/nicc777/cloud-console-common) project which contains the models and other classes required for integration and usage by the `cloud-console` main application.

# Dependencies

Since this project integrates with Amazon AWS, it depends on `boto3`

# Local Development

_**Important**_: Ensure you are working in a virtual environment.

Grab a recent `.tar.gz` from the [releases](https://github.com/nicc777/cloud-console-common/releases) on `cloud-console-common`

Assuming this archive file is in `$CLOUD_CONSOLE_COMMON_DIST`, install by running:

```shell
pip3 install $CLOUD_CONSOLE_COMMON_DIST
```


