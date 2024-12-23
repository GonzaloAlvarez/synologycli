# Synology CLI
**A dumb, simple and self contianed wrapper around the wonderful [Synology Python API](https://github.com/N4S4/synology-api)**

## How to use it

No setup no nothing. As easy as it gets.

You don't even have to clone this repo. You can just do:

```
$ curl -O https://raw.githubusercontent.com/GonzaloAlvarez/synologycli/refs/heads/main/synology.py
$ chmod +x synology.py
$ ./synology.py ls
```

It will ask your configuration in the first time. Just put your configuration and that's it.

You can use the following commands:

#### Upload file

```
$ ./synology.py up FILENAME
```

#### Download file

```
$ ./synology.py dw REMOTE_FILENAME
```

## Credit

Sure, just head over [Synology Python API](https://github.com/N4S4/synology-api)
