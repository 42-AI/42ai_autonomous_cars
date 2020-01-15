#!/usr/bin/env bash


PATATE_IP=`arp -a | grep b8:27:eb:20:56:bb | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'`

if [[ -z $PATATE_IP ]]
then
  PATATE_IP=`arp -a | grep dc:a6:32:67:ae:f9 | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'`
fi

if [[ -n $PATATE_IP ]]
then
    echo "PATATE IP detected = $PATATE_IP"
    ssh pi@$PATATE_IP
else
    echo "No IP detected for Patate. Are you connected to the right wifi? Is there enough energy to the Pi?"
fi