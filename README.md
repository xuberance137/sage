
###Installation

On OSX, the following are important

#PYGIT2
$ brew update
$ brew install libgit2
$ pip3 install pygit2

#PYCURL
$ pip uninstall pycurl; export PYCURL_SSL_LIBRARY=openssl; export LDFLAGS=-L/usr/local/opt/openssl/lib; export CPPFLAGS=-I/usr/local/opt/openssl/include; pip install pycurl --compile --no-cache-dir

###HISTORY

v0.1
- Upgraded from 2015 code
- Replaced pycurl usage with requests calls


###ToDo
- Track forks
- Track updates from previous clones
- Delete files after clone or capture just the git file and delete rest
- Language tracking other than python
- Restack plotting routines
