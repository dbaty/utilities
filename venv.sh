#!/bin/bash

#
# Create a new virtual environment and install developer tools:
#   - coverage
#   - nose
#   - pep8
#   - readline
#   - restview
#   - setuptools-git
#   - sphinx
#
# Syntax:
#     venv <py-dir> <env-dir> [<package1>, <package2>, ...]
#
# <py-dir> is the name of the directory where you have installed
# Python (possibly locally). It is used to fetch the correct version
# of 'virtualenv'. For example, supposing you have installed Python in
# the "py27" directory (i.e. with "./configure --prefix=py27"), you
# may run "venv" like this:
#
#     venv py27 /path/to/env
#

if [ $# -le 1 ]
then
    echo "Syntax: venv PY_VERSION DEST_DIR [<PACKAGE_1>, <PACKAGE_2>, ...]"
    exit 1
fi

$1/bin/virtualenv --no-site-packages $2
install="$2/bin/easy_install"
$install -U setuptools
$install Nose
$install Coverage
$install pep8
$install setuptools-git
$install restview
$install Sphinx
$install virtualenv
$install readline
for arg in $*
do
    if [ "$arg" != "$1" -a "$arg" != "$2" ]
    then $install $arg
    fi
done
echo
echo "The virtual environment has been set up in '$2'"
echo "You may activate it with: source $2/bin/activate"
