# query-lsf-marks

Query the LSF (also known as *qis server*) and show a desktop
notification on changes to your marks.

## Dependencies

### UNIX

Open a terminal and execute the following commands:

```bash
$ sudo apt-get install mercurial python3 python3-keyring python3-pip
$ sudo pip3 install notify2 requests beautifulsoup4
$ sudo pip3 install hg+https://vcs.zwuenf.org/hg/lgrahl/zwnflibs/logging hg+https://vcs.zwuenf.org/hg/lgrahl/zwnflibs/notify
$ sudo pip3 install hg+https://vcs.zwuenf.org/hg/lgrahl/zwnfqan
```

### Windows

* Install [Python3](https://www.python.org/downloads/)
* Install [pip](https://pip.pypa.io/en/latest/installing.html)
* Install [Mercurial](http://mercurial.selenic.com)
* Install [Growl](http://www.growlforwindows.com)

Open the command prompt and execute the following commands:

```
> <Path to Python Scripts>\pip.exe install keyring gntp requests beautifulsoup4
> <Path to Python Scripts>\pip.exe install hg+https://vcs.zwuenf.org/hg/lgrahl/zwnflibs/logging hg+https://vcs.zwuenf.org/hg/lgrahl/zwnflibs/notify
> <Path to Python Scripts>\pip.exe install hg+https://vcs.zwuenf.org/hg/lgrahl/zwnfqan
```

## Usage

Change into the folder of the repository and run the script with the following command:

```bash
$ python3 query-lsf.py <username> <interval>
```

* `<username>` is your user name in the LSF. The password will be requested once and
  stored in a secure keyring of your OS.

* `<interval>` is the interval in **minutes** that defines how often the LSF will be
  queried.

### Delete or Change Password

If the script runs in the background, stop it first.

Open a terminal and run Python in interactive mode:

```bash
$ python3
```

Delete the current password of `<username>`:

```python
>>> import keyring
>>> keyring.delete_password('query-lsf', '<username>')
```

If you run query-lsf again it will request a password.
