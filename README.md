# CCStore

[![Build Status](https://travis-ci.org/Litestore/django-ccstore.svg?branch=master)](https://travis-ci.org/Litestore/django-ccstore)

CCStore is the core of Litestore, an open source e-commerce project that supports Litecoin as default payment option.

It can work with any bitcoind-based cryptocurrencies and it is built on top of Django, channels, django-oscar and django-cc.

The project is currently work in progress and unfortunately not ready for a production usage and the author decline any responsibility for any problem that could be caused by this software.

If you find this project useful and you like to support its development, then please consider a donation:

* LTC: Lh4QheHGZKVvAAE8tg8GSooxAvAg6SQnmk
* BTC: 17JKaTmwRFc9kUagFK4oiQawRJFcCsVV6E
* ETH: 0xf9df390D0D20652D52A2E9Bbd7c530B4Bf9550DF

## Getting Started

A default Docker-based "sandbox" environment installation is provided for now.

### Prerequisites

To install the "sandbox" development environment the only requirements are Docker and docker-compose.

Manual installation on target host will require:

* A bitcoind-compatible daemon that support wallet operations (litecoind, bitcoind)
* Redis server for caching, websocket channels, sessions, celery tasks, etc.
* Database server (optional, by default it will use sqlite3 and postgresql on Docker)

Please check the provided [docker-compose.yml](docker-compose.yml) file for details about services related settings.

### Installing

You can build the docker container images by using docker-compose, that will expose the services by default on target host.

```
docker-compose up --build
```

To load sandbox fixtures, run database migrations and copy static files to local volume, run the following command.

```
docker-compose run runserver sh -c "make build_sandbox"
```

Then you will need to create an admin user to create categories, product types, fullfillment partners, products, etc.

```
docker-compose run runserver sh -c "python manage.py createsuperuser"
```

And then you can access Oscar's dashboard admin by opening [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/).


### Testnet

To run CCStore on testnet, you can run the following command:

```
docker-compose -p ccstore_testnet -f docker-compose-testnet.yml up --build
```

And follow the same installing procedure as described above, adding the -f option to specify which docker-compose settings file to use and -p as project name prefix.

## Contributing

Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details on project's code of conduct.

## Authors

* **Massimo Scamarcia** - *Initial work* - [mscam](https://github.com/mscam)

A list of contributors of people who participated in this project will be updated regularly.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
