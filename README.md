# query-lsf-marks

Query the LSF (also known as *qis server*) and show a desktop notification on changes to
your marks.

## Prerequisites

### Ubuntu

```bash
$ sudo apt-get install python3 python3-pip python3-dbus
```

### Windows

* [Python3](https://www.python.org/downloads/)
* [pip](https://pip.pypa.io/en/latest/installing.html)
* [Growl](http://www.growlforwindows.com)

## Virtual Environment

We recommend using [venv](https://docs.python.org/3/library/venv.html) to create an
isolated Python environment:

```bash
$ python3 -m venv query-lsf-venv
```

Edit the file `query-lsf-venv/pyvenv.cfg` and update the following line:

```
include-system-site-packages = true
```

Note: This is a workaround to be able to use system site packages but have a separate
`pip` environment, too.

You can switch into the created virtual environment *query-lsf-venv*
by running this command:

```bash
$ source query-lsf-venv/bin/activate
```

While the virtual environment is active, all packages installed using ``pip`` will be
installed into this environment.

To deactivate the virtual environment, just run:

```bash
$ deactivate
```

## Installation

If you are using a virtual environment, activate it first.

Install the module by running:

```bash
$ pip install git+https://github.com/lgrahl/query-lsf-marks.git
```

On Linux, you will also need to install `notify2`:

```bash
$ pip install notify2
```

On Windows, you will need to install `gntp`:

```
> <Path to Python Scripts>\pip.exe install gntp
```

## Usage

Change into the folder of the repository and run the script with the following command:

```bash
$ python3 query-lsf.py <username> <interval> [<storage>]
```

* `<username>` is your user name in the LSF. The password will be requested once and
  stored in a secure keyring of your OS.
* `<interval>` is the interval in **minutes** that defines how often the LSF will be
  queried.
* `<storage>` is an optional path to a JSON file where the marks will be stored. Defaults
  to `.query-lsf-marks.json` and will be created if it does not exist.

### Delete or Change Password

If the script runs in the background, stop it first.

Delete the current password of `<username>`:

```bash
$ python3 -m keyring del query-lsf <username>
```

If you run query-lsf again it will request a password.
