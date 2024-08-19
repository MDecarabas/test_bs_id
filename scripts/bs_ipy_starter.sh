#!/bin/bash

echo "You chose ipython!"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

ipython -i -c "%run $SCRIPT_DIR/bs_ipy_profile.ipy"