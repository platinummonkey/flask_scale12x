#!/bin/bash
#
# Sets up scripts for the viewer at SCALE12x talk
#
# Cody Lee
#

# Setting up Test Runner
cat << EOS > ./run_tests.sh
#!/bin/bash

nosetests --attr=unit -vv
EOS
chmod +x ./run_tests.sh

# Setting up Titan Setup Script
cat << EOS > ./setup_titan.sh
#!/bin/bash
#
# This script will download Titan-Server 0.4.2 and install it to /tmp/titan
#
# To start Titan use the start_titan.sh script
#

mkdir /tmp/titan
pushd /tmp/titan
wget http://s3.thinkaurelius.com/downloads/titan/titan-server-0.4.2.zip
unzip titan-server-0.4.2.zip
popd

echo "To run use the start_titan.sh script"
EOS
chmod +x ./setup_titan.sh

# Setting up Start Titan Script
cat << EOS > ./start_titan.sh
#!/bin/bash
#
# This will start the titan server
#
# To stop use the stop_titan.sh
#

pushd /tmp/titan/titan-server-0.4.2
./bin/titan.sh start
popd
EOS
chmod +x ./start_titan.sh

# Setting up Stop Titan Script
cat << EOS > ./stop_titan.sh
#!/bin/bash
#
# This will stop the titan server
#
# To start use the start_titan.sh
#

pushd /tmp/titan/titan-server-0.4.2
./bin/titan.sh stop
popd
EOS
#P.S. if you found this and are
#the first to stand up and say
#"donkey", claim your prize
#and thank you for actually
#checking twice before you run
#an untrusted script
chmod +x ./stop_titan.sh

# Setting up Talk Helper (really just a pretty shell wrapper around git)
cat << 'EOS' > ./talk_helper.sh
#!/bin/bash
#
# Helper script for the talk, it will toggle between noted git commits
#

TALK_PROMPT='$(prev/next) '

starting_commit="`git rev-parse HEAD`"
echo "Starting commit: $starting_commit"


commits=(683e32dd75361d4f87687b4f2235de8af455b950 028b31d21435954cb2579a6e780d579f6d599c00 ba95b15727bd4f543e907e4e12d06112d750168f a3ca56d346731b9ca953f0c08fda3fb99325d353 66c2c5b14e52584892d1a28a9dd33f112d57591c master)

max_commit_step=${#commits[*]}-1

function search_array() {
  index=0
  while [ "$index" -lt "${#commits[*]}" ]; do
    if [ "${commits[$index]}" = "$1" ]; then
      echo $index;
      return
    fi
    let "index++"
  done
  echo $max_commit_step;
}

commit_step=$(search_array "$starting_commit")

echo "On commit step: $commit_step"

function first_commit() {
  let "commit=0"
  git checkout ${commits[$commit]}
}
function last_commit() {
  let "commit=$max_commit_step"
  git checkout ${commits[$commit]}
}

function prev_commit() {
  if [ $commit_step -eq 0 ]; then
    echo "Already at the earliest commit"
  else
    let "commit=$commit-1"
    git checkout ${commits[$commit]}
  fi
}

function next_commit() {
  if [ $commit_step -eq $max_commit_step ]; then
    echo "Already at the last commit"
  else
    let "commit=$commit+1"
    git checkout ${commits[$commit]}
  fi
}

while :
do
  echo -n "$TALK_PROMPT"
  read cmd
  case "$cmd" in
    [pP] | [pP][rR][eE][vV] ) prev_commit
    ;;
    [nN] | [nN][eE][xX][tT] ) next_commit
    ;;
    [sS] | [sS][tT][aA][rR][tT] ) first_commit
    ;;
    [eE] | [eE][nN][dD] ) last_commit
    ;;
    [qQ] | [qQ][uU][iI][tT] ) exit 0
    ;;
    *)
      echo "Unrecognized command, the following commands are available."
      echo "[q]uit  - Quit"
      echo "[p]rev  - Previous Talk Commit"
      echo "[n]ext  - Next Talk Commit"
      echo "[s]tart - Go to the first Talk Commit"
      echo "[e]nd   - Go to the end of the Talk Commit"
  esac
done
EOS
chmod +x talk_helper.sh
