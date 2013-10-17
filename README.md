# Instances

Analytics for open source developers


## developing

1. Install dependencies:

```console
pip install -r requirements-dev.txt
```

2. Run the server

```console
make run
```

3. Run tests

```console
make unit functional
```


## deploying

Have your ssh keys exported to the server then....

```bash
make deploy
```

It will deploy the master branch to production
