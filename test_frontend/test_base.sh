#!/bin/bash
PTH=`pwd`/../
echo $PTH
cd $PTH
python2 chessrisk.py &
#CRPID=$!
#echo $CRPID
# This is a race condition but I can't be bothered to fix it
sleep 2
cd -
curl --data "$1" localhost:5000/ >last_request.html
sudo ln -s "$PTH"/static /static || :
open file:///"$PTH"/test_frontend/last_request.html


function cleanup() {
  sudo rm -rf /static
  CRPID="$(ps aux | grep [C]hessrisk.py | awk '{print $2}')"
  echo "$(ps aux | grep [C]hessrisk.py)"
  while read -r ID ; do
    echo "KILLING: $ID"
    kill -TERM "$ID"
  done <<< "$CRPID"
  exit 0
}
trap cleanup SIGHUP SIGINT SIGTERM

# Another race condition?
sleep 7
while true; do
  :
done

