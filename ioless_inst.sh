#!/bin/bash

#SBATCH --time=3:30:00
#SBATCH --mail-type=FAIL
#SBATCH --mem=15G
#SBATCH -c 1

# Args: <test-name> <binary> <test-folder> <model> <category> <col-red-time-out> <red-time-out> <comb-time-out> <expl-time-out> <bin-options> <search-strat>

echo "Arguments: $@"

NAME=$1
BIN=$2
TEST_FOLDER=$3
MODEL=$4
CATEGORY=$5
COL_RED_TIME_OUT=$6
RED_TIME_OUT=$7
COMB_TIME_OUT=$8
EXPL_TIME_OUT=$9
OPTIONS="${10}"
SEARCH_STRAT=${11}

PETRI_TYPE="Normal"
if [ "$TEST_FOLDER" = "MCC2021-COL-inhib" ] ; then
  PETRI_TYPE="Inhib"
fi

OUT_DIR="output/$(basename $BIN)/CPN-$COL_RED_TIME_OUT-$RED_TIME_OUT-$COMB_TIME_OUT-$EXPL_TIME_OUT/$CATEGORY/$SEARCH_STRAT/$PETRI_TYPE/$NAME"

SCRATCH="/scratch/$$/$NAME/$MODEL/$CATEGORY"
mkdir -p $SCRATCH
trap "rm -r $SCRATCH ; echo terminated ; exit" 0  # We trap the to make sure we cleanup

LTLFLAG=$( ([[ "$CATEGORY" == "LTLCardinality" ]] || [[ "$CATEGORY" == "LTLFireability" ]]) && echo " -ltl" || echo "")

# Find the number of queries for this model by counting how many times "<property>" appears
NQ=$(grep "<property>" "$TEST_FOLDER/$MODEL/$CATEGORY.xml" | wc -l)

echo "Processing $MODEL ($NQ queries total)"

for Q in $(seq 1 $NQ) ; do
	
	echo "Q$Q"

	mkdir -p $SCRATCH
	RED_PNML="$SCRATCH/$MODEL.$Q.r.pnml"

	# ===================== RED+VERIFY ======================

	echo "  Processing ..."

	OUT="$OUT_DIR/$MODEL.$Q.out"
	CMD="./$BIN $OPTIONS -s $SEARCH_STRAT -D $COL_RED_TIME_OUT -d $RED_TIME_OUT -x $Q $LTLFLAG $TEST_FOLDER/$MODEL/model.pnml $TEST_FOLDER/$MODEL/$CATEGORY.xml --write-reduced $RED_PNML"

	O=$(eval "/usr/bin/time -f '@@@%e,%M@@@' timeout ${COMB_TIME_OUT}m $CMD" 2>&1)
	echo "$O" | grep -v "^<" | grep -v "^Query before" | grep -v "^Query after" > $OUT

	# ===================== EXPLORATION ======================

	if [ "$EXPL_TIME_OUT" -eq "0" ] ; then
		echo "  Exploration skipped"
	else
		echo "  Exploration ..."

		ECMD="./$BIN -q 0 -r 0 $RED_PNML -e"
		SOUT="$OUT_DIR/$MODEL.$Q.sout"
		ZOUT="$OUT_DIR/$MODEL.$Q.size"

		RES=$(eval "timeout ${EXPL_TIME_OUT}m $ECMD" 2>&1)
		RES=$(echo $RES | grep -v "^<" | tr '\n' '\r')
		echo $RES | grep -v "^<" > $SOUT

		SIZE=$([[ -n "$(echo $RES | awk "/explored states/")" ]] && echo $RES | sed -E "s/.*explored states: *([0-9]+).*/\1/" || echo 0)
		
		echo $SIZE > $ZOUT
	fi
	
done

echo "Cleaning /scratch"

rm -r $SCRATCH

exit 0
