# pure-tcl-aws-ssm

AWS SSM client implemented in Tcl 9.1. Its only package dependency is
[`pure-tcl-aws-core`](https://github.com/jerily/pure-tcl-aws-core), which supplies
HTTP, JSON, XML, credentials and signing. No AWS C++ SDK is required.

```tcl
package require pure-tcl-aws-ssm 0.1.0
set client [::aws::ssm::create {region us-east-1}]
try {
    puts [$client get_parameter /example/name]
} finally {
    $client destroy
}
```

`package require awsssm 1.0.19` is also supported. Use one implementation
of the `awsssm` package per interpreter. Existing namespace commands
(`::aws::ssm::method $client ...`) and client methods share the same behavior.
Client destruction returns an empty result. Unknown methods and invalid arguments
raise Tcl errors. See the core README for credentials, configuration and retries.

## Methods

| Method | Arguments after the client handle |
| --- | --- |
| `put_parameter` | `name value ?type? ?overwrite?` |
| `get_parameter` | `name ?with_decryption?` |
| `delete_parameter` | `name` |

## Behavior

`get_parameter` returns `name`, `type`, `value`, and `version`. Set its optional `with_decryption` argument to true to decrypt a SecureString. `put_parameter` accepts `String`, `StringList`, or `SecureString` and an explicit overwrite flag.

## Install and examples

Install the core and its dependencies first, then run:

```sh
make install PREFIX=/your/prefix
```

The release recipe declares examples with `file` entries. After registry installation:

```sh
ttrek run -package pure-tcl-aws-ssm -script example-get-parameter -- parameter-name
```

`./run-example.sh --help` lists arguments. Set AWS credentials and `AWS_REGION`
or `AWS_DEFAULT_REGION` before running AWS examples. Examples read resources or sign URLs.

## Tests

With Tcl 9.1 and the dependencies on `TCLLIBPATH`:

```sh
make test TCLSH=tclsh9.1
```

Python 3 supplies local HTTP fixtures. Tests use fake credentials and do not
contact AWS. They check requests, result formats, and error handling.
