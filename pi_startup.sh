#!/bin/bash
##!/bin/sh -e
# this shebang uncommented as on ubuntu substitutions don't work with sh -e

###debugging###
#set -x

# WITA Pi utilities to enable unattended startup  (WHUPI)
# Copyright by Wolf-IT-Architekt

# globals
whupi_abspath() {
  # return as echo absolute path of THIS utility
    MYCWD=`pwd`
    MYHOME=`dirname $0`
    cd ${MYHOME}
    MYABSPATH=`pwd`
    cd ${MYCWD}
    echo ${MYABSPATH}
}

WHUPI_ABSPATH=`whupi_abspath`
WITA_HELPER_PI="WITA-Pi-Startup-Utility for Picroft"
WHUPI=$0
WHUPI_VERSION=2.0/2023/0303
WHUPI_HOME=`dirname $0`
WHUPI_SOURCE=${WHUPI_HOME}

pi_startup_log="/tmp/pi_startup.log"

#wipe logfile on every start of this Utility
echo " " > ${pi_startup_log}

####################

wsu_logger() {

# wsu_logger: logging $@ to log file at
#     WSU_HELPER_LOGFILE="/home/michael/WITA-Tools/evcc-sonne-tanken/evcc-scout/admin/mmwpv-helper.log"
D=`date "+%Y-%m-%d %H:%M:%S"`
echo ${D} " " $@
echo ${D} " " $@ >> ${pi_startup_log}
}

####################

whupi_version() {
echo
echo ${WITA_HELPER_PI}: $WHUPI_VERSION
echo Copyright by Wolf-IT-Architekt
echo
RC=0
}

####################

whupi_help() {
  echo
  echo "$0 ${WITA_HELPER_PI} -- usage:"
  echo "$0 -V|-h|-v"
  echo "  --version,    -V                 : show version"
  echo "  --help,       -h                 : show help"
  echo "  --vnc,        -v [-DY display number]"
  echo "                                   : start vnc on display DY"
  echo "                                     if it is not yet running"
  echo "                                     default display is 1 "
  echo
  echo "absolute path of this utility is:"
  whupi_abspath
  echo "logs go to ${pi_startup_log}"
  echo
}

####################

wsu_is_vncserver_running() {
  # check if vncserver is running on display $1
  # echo 1: yes
  # echo 0: no
  # echo 2: no, vncserver not available on this m/c

DY=$1
RC=0 # vncserver not running (is the default)
computer=`uname -n`
vnc_location=~/.vnc
if [ -d ${vnc_location} ]; then
    vnc_pid_file="${vnc_location}/${computer}:${DY}.pid"
    if [ -f ${vnc_pid_file} ]; then
      # the vnc pid file may exist whereas vncserver is NOT running,
      # this will happen when system was shutdown, which leaves vnc pid file alone
      # so we check pid in this file against a running vnc process
      pid=`cat ${vnc_pid_file}`
      vnc_proc_count=`ps -edalf | grep ${pid} | grep vnc | wc -l`
      if [ ${vnc_proc_count} -ge 1 ]; then 
          RC=1
      fi
    fi
else
    RC=2
fi
echo ${RC}
}

####################

whupi_vnc_start() {
  # start virtual vncserver on DY $1 if it is not yet running there

DY=$1
vnc_stat=`wsu_is_vncserver_running ${DY} `
if [ ${vnc_stat} -eq 1 ]; then
    wsu_logger "virtual vncserver is already running on display no. ${DY}"
elif [  ${vnc_stat} -eq 0 ]; then
    wsu_logger "virtual vncserver is not yet running on display no. ${DY}, starting..."
    vncserver-virtual
    rc=$?
    vnc_stat=`wsu_is_vncserver_running ${DY}`
    wsu_logger "virtual vncserver started, return code: ${rc}, vnc_stat: ${vnc_stat}, 0=not running, 1=running, 2=NA"
else
  wsu_logger "virtual vncserver is not available on this host, vnc_stat: ${vnc_stat}, 0=not running, 1=running, 2=NA"
fi
}

################################################################################

# here starts main
RC=0
RMSG="successful"

wsu_logger "################"
wsu_logger "pi_startup.sh $@"
wsu_logger "################"

case $1 in
####################
 --version|-V)
 WHUPI_FCT="version"
 whupi_version
;;
####################
 --help|-h)
 WHUPI_FCT="help"
 whupi_help
;;
####################
--vnc|-v)
WHUPI_FCT="vnc start"
WHUPI_DY=1
if [ "$2" = "-DY" ]; then
  WHUPI_DY=$3
fi
wsu_logger "processing display ${WHUPI_DY}"
whupi_vnc_start ${WHUPI_DY}
;;
####################

*)
RMSG="invalid arguments - try --help"
echo $RMSG
RC=99

;;
####################

esac

exit ${RC}




################################################################################
