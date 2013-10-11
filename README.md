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

Deploying instances is super easy!


#### primer

make sure you have exported the following environment variables

* `CHEF_USERNAME` - a string with your username
* `CHEF_KEY_LOCATION` - a string with a full path to the certificate key file `.pem`

**EXAMPLE:**
```bash
export CHEF_USERNAME="gabrielfalcao"
export CHEF_KEY_LOCATION="$HOME/.apronrc/yourusername.pem"
```



#### hands on

Make your changes in the project, commit, make tests pass and then simply run

```bash
make release
```

it will ask you what's the new version, after that it will:

1. Change the version everywhere in the project
2. Make a new commit with those changes
3. Package instances and submit to localshop
4. Update the data bag to the new version
5. SSH to the server, run chef client and restart supervisor
