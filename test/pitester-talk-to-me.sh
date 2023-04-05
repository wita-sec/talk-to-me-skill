#!/bin/bash
##!/bin/sh -e
# this shebang uncommented as on ubuntu substitutions don't work with sh -e

###debugging###
#set -x

# WITA Testr Utility for Picroft Skill development  (WHUPI)
# Copyright by Wolf-IT-Architekt

# This scripts tests the talk-to-me skill
# It is supposed to run on a Raspberry Pi with Picroft
# It is called with argument "path to file uterances"
# this file must include uterances that will be directed to Picroft
# the result of these uterances can be monitored with the mycroft-cli-client
# This is kind of "manuel" testing, automation may be the next step.
# How must uterances file look like?

#
#  a line starting with # is a comment and will not be processed
#  a line starting with @ is a comment that will be displayed
#  any other non-empty line line is an uterance that will be directed to Picroft
#
#
################################################################################
# globals
whupi_abspath() {
  # return as echo absolute path of THIS utility
  # take care of utility is launched directly or via a slink'ed file
  MYCWD=`pwd`
  MYHOME=`dirname $0`
  FATTR=`ls -l $0 | awk '{print $1}'`
  SLINK=`echo ${FATTR} | egrep ^l`
  if [ ! "${SLINK}" = "" ]; then
      # it's a link
      SLTARGET=`ls -l $0 | awk '{print $11}'`
      MYHOME=`dirname ${SLTARGET}`
  fi
  cd ${MYHOME}
  MYABSPATH=`pwd`
  cd ${MYCWD}
  echo ${MYABSPATH}
}
################################################################################

WHUPI_ABSPATH=`whupi_abspath`
WITA_HELPER_PI="WITA-Test-Utility for Picroft"
WHUPI=$0
WHUPI_VERSION=2.0/2023/0321
WHUPI_HOME=`dirname $0`
WHUPI_SOURCE=${WHUPI_HOME}
WHUPI_DEF_SKILL=talk-to-me   # name of the skill being developed
WHUPI_UT_DELAY_DEFAULT=30 # default delay in secs between uterance tests not to overload the Picroft
WHUPI_UT_DELAY=${WHUPI_UT_DELAY_DEFAULT} # currently set delay in secs between uterance

################################################################################

whupi_version() {
echo
echo ${WITA_HELPER_PI}: $WHUPI_VERSION
echo Copyright by Wolf-IT-Architekt
echo
echo "absolute path of this utility is: `whupi_abspath`"
echo
RC=0
}

####################

whupi_help() {
  echo
  echo "$0 ${WITA_HELPER_PI} -- usage:"
  echo "$0 -v|-h|-t"
  echo "  --version,    -v                       : show version"
  echo "  --help,       -h                       : show help"
  echo "  --test,       -t -f <file> -d <delay>  : test uterances from given <file> "
  echo "  --test,       -t -a -d <delay>         : test all uterance files *.uterance"
  echo "                                         : delay each uterance <delay> no of secs, default=30"
  echo "                                         : delay can be overwritten by a line "
  echo "                                         : § <delay> in <file>"
  echo "Example file with uterances: talk-to-me.uterances"
  echo "    See comments in the file to find out how it works."
  echo
  echo "absolute path of this utility is: `whupi_abspath`"
  echo
RC=0
}
################################################################################
#
# How to automate testing
# The aim is to save an uterance and its reply as text to a file
# This file later can be evaluated to find bugs/problems
# The layout of that file should be human readable and also m/c readable
#
# We write the uterance to stdout
# We get its reply from the /var/log/mycroft/audio.log file and write to stdout
#    How to get reply from audio.log:
#    cat audio.log | grep Speak: > /tmp/audio_before.log
#    launch Picroft with an uterance
#   cat audio.log | grep Speak: > /tmp/audio_after.log
#   diff /tmp/audio_before.log /tmp/audio_after.log > /tmp/audio_diff.log
#   extract reply text from /tmp/audio_diff.log and write to stdout
#  output can be redirected by the caller to get perstent test results

whupi_test() {
    test_file=$1
    echo "going to test uterances of file ${test_file}"
    echo "uterance delay was set to ${WHUPI_UT_DELAY} seconds"
    echo
    cnt=1
    while IFS= read -r line; do
        if [ ! "${line}" = "" ]; then
            c1=`echo ${line} | egrep ^#`
            c2=`echo ${line} | egrep ^@`
            c3=`echo ${line} | egrep ^§`
            if [ ! "${c1}" = "" ]; then
                # internal comment
                donothing=true
            elif [ ! "${c2}" = "" ]; then
                # display comment
                DC=${line}
                DT=`date "+%Y%m%d.%H%M%S"`
                echo "${DT} ${DC}"
            elif [ ! "${c3}" = "" ]; then
                # sleep timer in secs
                WHUPI_UT_DELAY=${line:(+2)}
                echo "uterance delay now is ${WHUPI_UT_DELAY} seconds"
            else
                echo "${DC} ${cnt} uterance: ${line}"
                resultfile=`whupi_run_ut ${line}`
                echo "${DC} ${cnt} relpy:"
                cat ${resultfile}
                echo "================"
                let cnt++
                rm -f ${resultfile}
            fi
        fi
    done < ${test_file}
RC=0
}
################

whupi_test_all() {
    # run test for all uterance files *.uterances
    for filename in `whupi_abspath`/*.uterances; do
        [ -e "${filename}" ] || continue
        ls -l ${filename}
        whupi_test ${filename}
    done
}
################

whupi_run_ut() {
    # run an uterance which is supplied as arguments $@ ($1-$n, each word is a $i)
    # extract reply from Picroft to a tmp file
    # return full filename to stdout, but nothing else except for testing!
    #
    ut=$@
    #echo "whupi_run_ut: ${ut}"
    D=`date "+%Y%m%d%H%M%S.%s"`
    Picroft_util=/home/pi/mycroft-core/bin/mycroft-say-to
    Picroft_audio_log=/var/log/mycroft/audio.log
    Picroft_audio_keyword="Speak:"
    Picroft_brabbel=/var/log/mycroft/audio_say_to_${D}
    audio_before=/tmp/audio_before_${D}
    audio_after=/tmp/audio_after_${D}
    audio_diff=/tmp/audio_diff_${D}
    audio_result=/tmp/audio_result_${D}
    cat ${Picroft_audio_log} | grep ${Picroft_audio_keyword} > ${audio_before}
    #echo ${Picroft_util} ${ut}
    touch ${Picroft_brabbel}
    ${Picroft_util} ${ut} > ${Picroft_brabbel} 2>&1
    # give Picroft some time to finish the uterance, mainly it takes the time to
    # finish the speach. So, the more text the longer time to finish
    # otherwise Picroft queues ut's and as a result audio logs will be incomplete
    loop=1
    while [ ${loop} -le 3 ]
    do
      sleep ${WHUPI_UT_DELAY}
      cat ${Picroft_audio_log} | grep ${Picroft_audio_keyword} > ${audio_after}
      diff ${audio_before} ${audio_after} > ${audio_diff}
      cat ${audio_diff} |grep Speak: | awk '{for(i=12;i<=NF;++i) printf $i" " ; print ""}' > ${audio_result}
      if [ -s ${audio_result} ]; then
        break
      else
        let loop++
        sleep ${WHUPI_UT_DELAY}
      fi
    done
    if [ ! -s ${audio_result} ]; then
      echo "Picroft timed out, query could not be answered" > ${audio_result}
      if [ -s ${Picroft_brabbel} ]; then
        cat ${Picroft_brabbel} >> ${audio_result}
      fi
    fi
    rm -f ${audio_before} ${audio_after} ${audio_diff} ${Picroft_brabbel}
    echo ${audio_result}
}

################

whupi_create_ut_file() {
    # create tmp file and write uterance $@
    # return filename to stdout
    UT=$@
    D=`date "+%Y%m%d%H%M%S.%s"`
    echo "@ Single Uterance" > /tmp/talk-to-me-ut-${D}
    echo ${UT} >> /tmp/talk-to-me-ut-${D}
    echo /tmp/talk-to-me-ut-${D}
}

################################################################################

# here starts main
RC=0
RMSG="successful"

case $1 in
####################
 --version|-v)
 WHUPI_FCT="version"
 whupi_version
;;
####################
 --help|-h)
 WHUPI_FCT="help"
 whupi_help
;;
####################
--test|-t)
WHUPI_FCT="test"

if [ "$2" = "-f" ]; then
  UT_FILE=$3
  if [ ! "$4" = "" ]; then
      WHUPI_UT_DELAY=$5
  fi
  whupi_test ${UT_FILE} ${UT_DELAY}
elif [ "$2" = "-a" ]; then
  if [ ! "$3" = "" ]; then
      WHUPI_UT_DELAY=$4
  fi
  whupi_test_all
elif [ "$2" = "-u" ]; then
  UT_FILE=`whupi_create_ut_file $3`
  WHUPI_UT_DELAY=6
  whupi_test ${UT_FILE}
  rm -f ${UT_FILE}
else
  echo "please supply an uterance file"
  echo "try --help"
fi
;;
####################

*)
echo "invalid arguments - try --help"
RC=99
;;
####################

esac

exit ${RC}
