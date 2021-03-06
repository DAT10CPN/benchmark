#!/bin/bash
#SBATCH --partition=cpu

# Args: <test-name> <binary> <bin-options> [test-folder] [category] [partition] [col-red-time-out] [unf-time-out] [red-time-out] [veri-time-out] [expl-time-out]
# Starts a number of slurm jobs each solving the queries of one model in the test folder.
# Each of those jobs are then followed by another job running the reduced net too in order to determine the size of the state space.
# When all jobs are done, the results are compiled into a single csv.

NAME=$1
BIN=$2
OPTIONS=$3
TEST_FOLDER=$4
CATEGORY=$5
PARTITION=$6
COL_RED_TIME_OUT=$7
UNF_TIME_OUT=$8
RED_TIME_OUT=$9
VERI_TIME_OUT=${10}
EXPL_TIME_OUT=${11}

if [ -z "$NAME" ] ; then
	echo "Missing benchmark name"
	exit
fi

if [ -z "$BIN" ] ; then
	echo "Missing binary"
	exit
fi

if [ ! -f "$BIN" ] ; then
	echo "Binary does not exist"
	exit
fi

pat1="^-R [0-1]"
pat2="^-R 2 [0-9]"
if [ -z "$OPTIONS" ] ; then
	echo "Missing binary options"
	exit
elif ! [[ "$OPTIONS" =~ $pat1 ]] && ! [[ "$OPTIONS" =~ $pat2 ]] ; then
	echo "Err: OPTIONS must start with '-R [0-1]' or '-R 2 [0-9]'. It is '$OPTIONS'"
	exit 0
fi

if [ -z "$TEST_FOLDER" ] ; then
	echo "No TEST_FOLDER given, using MCC2021-COL"
	TEST_FOLDER="MCC2021"
elif [ "$TEST_FOLDER" != "MCC2021-COL" ] && [ "$TEST_FOLDER" != "MCC2021-COL-PnmlTest" ] && [ "$TEST_FOLDER" != "MCC2021-COL-inhib" ]; then
	echo "Err: TEST_FOLDER must be 'MCC2021-COL' or 'MCC2021-COL-PnmlTest'. It is '$TEST_FOLDER'"
	exit 0
fi

if [ -z "$CATEGORY" ] ; then
	echo "No CATEGORY given, using ReachabilityCardinality"
	CATEGORY="ReachabilityCardinality"
elif [ "$CATEGORY" != "ReachabilityCardinality" ] && [ "$CATEGORY" != "LTLCardinality" ] && [ "$CATEGORY" != "CTLCardinality" ] && [ "$CATEGORY" != "ReachabilityFireability" ] && [ "$CATEGORY" != "LTLFireability" ] && [ "$CATEGORY" != "CTLFireability" ] ; then
	echo "Err: CATEGORY must be ReachabilityCardinality, LTLCardinality, CTLCardinality, ReachabilityFireability, LTLFireability, or CTLFireability. It is '$CATEGORY'"
	exit 0
fi

patReach="^Reachability"
patLTL="^LTL"
patCTL="^CTL"
if [ -z "$PARTITION" ] ; then
	PARTITION="naples"
	if [[ "$CATEGORY" =~ $patReach ]] ; then
    PARTITION="dhabi"
  elif [[ "$CATEGORY" =~ $patLTL ]] ; then
    PARTITION="rome"
  elif [[ "$CATEGORY" =~ $patCTL ]] ; then
    PARTITION="rome"
  fi
	echo "No PARTITION given, using $PARTITION based on the selected category '$CATEGORY'"
elif [ "$PARTITION" != "naples" ] && [ "$PARTITION" != "rome" ] && [ "$PARTITION" != "dhabi" ] && [ "$PARTITION" != "cpu" ] ; then
	echo "Err: PARTITION must be naples, rome, dhabi, or cpu. It is '$PARTITION'"
	exit 0
fi

pat="^[0-9]+$"

if [ -z "$COL_RED_TIME_OUT" ] ; then
	echo "No COL_RED_TIME_OUT given, using 4 seconds per query"
	COL_RED_TIME_OUT=4
elif ! [[ "$COL_RED_TIME_OUT" =~ $pat ]] ; then
	echo "Err: COL_RED_TIME_OUT must be a non-negative integer (seconds). It is '$COL_RED_TIME_OUT'"
	exit 0
fi

if [ -z "$UNF_TIME_OUT" ] ; then
	echo "No UNF_TIME_OUT given, using 2 minutes per query"
	UNF_TIME_OUT=2
elif ! [[ "$UNF_TIME_OUT" =~ $pat ]] ; then
	echo "Err: UNF_TIME_OUT must be a non-negative integer (minutes). It is '$UNF_TIME_OUT'"
	exit 0
fi

if [ -z "$RED_TIME_OUT" ] ; then
	echo "No RED_TIME_OUT given, using 20 seconds per query"
	RED_TIME_OUT=20
elif ! [[ "$RED_TIME_OUT" =~ $pat ]] ; then
	echo "Err: RED_TIME_OUT must be a non-negative integer (seconds). It is '$RED_TIME_OUT'"
	exit 0
fi

if [ -z "$VERI_TIME_OUT" ] ; then
	echo "No VERI_TIME_OUT given, using 1 minute per query"
	VERI_TIME_OUT=1
elif ! [[ "$VERI_TIME_OUT" =~ $pat ]] ; then
	echo "Err: VERI_TIME_OUT must be a non-negative integer (minutes). It is '$VERI_TIME_OUT'"
	exit 0
fi

if [ -z "$EXPL_TIME_OUT" ] ; then
	echo "No EXPL_TIME_OUT given, using 1 minute per query"
	EXPL_TIME_OUT=1
elif ! [[ "$EXPL_TIME_OUT" =~ $pat ]] ; then
	echo "Err: EXPL_TIME_OUT must be a non-negative integer (minutes). It is '$EXPL_TIME_OUT'"
	exit 0
fi

chmod u+x "$BIN"

DIR="output/$(basename $BIN)/$NAME"
rm -rf $DIR
mkdir -p $DIR

for MODEL in $(ls $TEST_FOLDER) ; do
	# Process model

	JOB_ID=$(sbatch --mail-user=$(whoami) --job-name=$NAME --partition=$PARTITION --exclude=${PARTITION}01 ./scratch_inst.sh $NAME $BIN $TEST_FOLDER $MODEL $CATEGORY $COL_RED_TIME_OUT $UNF_TIME_OUT $RED_TIME_OUT $VERI_TIME_OUT $EXPL_TIME_OUT "$OPTIONS" | sed 's/Submitted batch job //')
	echo "Submitted batch job $JOB_ID for $MODEL"

done

sbatch --partition=cpu --mail-type=FAIL --mail-user=$(whoami) --job-name=$NAME --dependency=singleton ./compile_results.sh $NAME $BIN $TEST_FOLDER
