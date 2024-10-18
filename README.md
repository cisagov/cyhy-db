# cyhy-db #

[![GitHub Build Status](https://github.com/cisagov/cyhy-db/workflows/build/badge.svg)](https://github.com/cisagov/cyhy-db/actions)
[![CodeQL](https://github.com/cisagov/cyhy-db/workflows/CodeQL/badge.svg)](https://github.com/cisagov/cyhy-db/actions/workflows/codeql-analysis.yml)
[![Coverage Status](https://coveralls.io/repos/github/cisagov/cyhy-db/badge.svg?branch=develop)](https://coveralls.io/github/cisagov/cyhy-db?branch=develop)
[![Known Vulnerabilities](https://snyk.io/test/github/cisagov/cyhy-db/develop/badge.svg)](https://snyk.io/test/github/cisagov/cyhy-db)

This repository implements a Python module for interacting with a Cyber Hygiene database.

## Pre-requisites ##

- [Python 3.11](https://www.python.org/downloads/) or newer
- A running [MongoDB](https://www.mongodb.com/) instance that you have access to

## Starting a Local MongoDB Instance for Testing ##

> [!IMPORTANT]
> This requires [Docker](https://www.docker.com/) to be installed in
> order for this to work.

You can start a local MongoDB instance in a container with the following
command:

```console
pytest -vs --mongo-express
```

> [!NOTE]
> The command `pytest -vs --mongo-express` not only starts a local
> MongoDB instance, but also runs all the `cyhy-db` unit tests, which will
> create various collections and documents in the database.

Sample output (trimmed to highlight the important parts):

```console
<snip>
MongoDB is accessible at mongodb://mongoadmin:secret@localhost:32859 with database named "test"
Mongo Express is accessible at http://admin:pass@localhost:8081

Press Enter to stop Mongo Express and MongoDB containers...
```

Based on the example output above, you can access the MongoDB instance at
`mongodb://mongoadmin:secret@localhost:32859` and the Mongo Express web
interface at `http://admin:pass@localhost:8081`.  Note that the MongoDB
containers will remain running until you press "Enter" in that terminal.

## Example Usage ##

Once you have a MongoDB instance running, the sample Python code below
demonstrates how to initialize the database, create a new request document, save
it, and then retrieve it.

```python
import asyncio
from cyhy_db import initialize_db
from cyhy_db.models import RequestDoc
from cyhy_db.models.request_doc import Agency

async def main():
    # Initialize the CyHy database
    await initialize_db("mongodb://mongoadmin:secret@localhost:32859", "test")

    # Create a new CyHy request document and save it in the database
    new_request = RequestDoc(
        agency=Agency(name="Acme Industries", acronym="AI")
    )
    await new_request.save()

    # Find the request document and print its agency information
    request = await RequestDoc.get("AI")
    print(request.agency)

asyncio.run(main())
```

Output:

```console
name='Acme Industries' acronym='AI' type=None contacts=[] location=None
```

## Additional Testing Options ##

> [!WARNING]
> The default usernames and passwords are for testing purposes only.
> Do not use them in production environments. Always set strong, unique
> credentials.

### Environment Variables ###

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_INITDB_ROOT_USERNAME` | The MongoDB root username | `mongoadmin` |
| `MONGO_INITDB_ROOT_PASSWORD` | The MongoDB root password | `secret` |
| `DATABASE_NAME` | The name of the database to use for testing | `test` |
| `MONGO_EXPRESS_PORT` | The port to use for the Mongo Express web interface | `8081` |

### Pytest Options ###

| Option | Description | Default |
|--------|-------------|---------|
| `--mongo-express` | Start a local MongoDB instance and Mongo Express web interface | n/a |
| `--mongo-image-tag` | The tag of the MongoDB Docker image to use | `docker.io/mongo:latest` |
| `--runslow` | Run slow tests | n/a |

## Contributing ##

We welcome contributions!  Please see [`CONTRIBUTING.md`](CONTRIBUTING.md) for
details.

## License ##

This project is in the worldwide [public domain](LICENSE).

This project is in the public domain within the United States, and
copyright and related rights in the work worldwide are waived through
the [CC0 1.0 Universal public domain
dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0
dedication. By submitting a pull request, you are agreeing to comply
with this waiver of copyright interest.
