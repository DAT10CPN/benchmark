#!/bin/bash

#SBATCH --time=5:00:00
#SBATCH --mail-type=FAIL
#SBATCH --mem=15G
#SBATCH -c 2

# Args: <test-name> <binary> <test-folder> <model> <category> <col-red-time-out> <unf-time-out> <red-time-out> <veri-time-out> <expl-time-out> <bin-options>

echo "Arguments: $@"

NAME=$1
BIN=$2
TEST_FOLDER=$3
MODEL=$4
CATEGORY=$5
COL_RED_TIME_OUT=$6
UNF_TIME_OUT=$7
RED_TIME_OUT=$8
VERI_TIME_OUT=$9
EXPL_TIME_OUT=${10}
OPTIONS="${11}"

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
	UQUERIES="$SCRATCH/$MODEL.$Q.u.xml"
	UPNML="$SCRATCH/$MODEL.$Q.u.pnml"
	PNML="$SCRATCH/$MODEL.$Q.r.pnml"

	# ===================== COLORED REDUCTION AND UNFOLD ========================

	echo "  Colored reduction ..."

	RU_TIME_OUT=$(($COL_RED_TIME_OUT + 60 * $UNF_TIME_OUT))

	UCMD="timeout ${RU_TIME_OUT}s ./$BIN $OPTIONS -D $COL_RED_TIME_OUT -r 0 -q 0 -x $Q $LTLFLAG $TEST_FOLDER/$MODEL/model.pnml $TEST_FOLDER/$MODEL/$CATEGORY.xml --noverify --write-unfolded-net $UPNML --write-unfolded-queries $UQUERIES"
	UOUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.uout"

	# Reduce model+unfold and store stdout

	O=$(eval "$UCMD" 2>&1)
	echo "$O" | grep -v "^<" | grep -v "^Query before" | grep -v "^Query after" > "$UOUT"

	# ===================== NORMAL REDUCTION ========================

	echo "  Reduction ..."

	ROUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.rout"
	rm -f "$ROUT"

	RCMD="./$BIN $OPTIONS -d $RED_TIME_OUT -q 0 -x 1 $LTLFLAG $UPNML $UQUERIES --write-reduced $PNML --noverify"
	
	# Reduce model+query and store stdout

	O=$(eval "$RCMD" 2>&1)
	echo "$O" | grep -v "^<" | grep -v "^Query before" | grep -v "^Query after" > "$ROUT"

	# ===================== VERIFICATION =====================

	VOUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.vout"
	rm -f "$VOUT"

	if [ "$VERI_TIME_OUT" -eq "0" ] ; then
		echo "  Verification skipped"
	elif [[ -n "$(echo "$O" | awk '/Query solved by Query Simplification/')" ]] ; then
		echo "  Verification skipped due to query simplification"
	else
		echo "  Verification ..."

		VCMD="./$BIN -r 0 -x 1 $LTLFLAG $PNML $UQUERIES"
		
		# Verify query and store stdout along with time and memory spent between @@@s
		O=$(eval "/usr/bin/time -f '@@@%e,%M@@@' timeout ${VERI_TIME_OUT}m $VCMD" 2>&1)
		echo "$O" | grep -v "^<" | grep -v "^Query before" | grep -v "^Query after" > "$VOUT"
	fi

	# ===================== EXPLORATION ======================

	SOUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.sout"
	ZOUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.size"
	rm -f "$SOUT"
	rm -f "$ZOUT"

	if [ "$EXPL_TIME_OUT" -eq "0" ] ; then
		echo "  Exploration skipped"
	else
		echo "  Exploration ..."

		ECMD="./$BIN -q 0 -r 0 $PNML -e"

		RES=$(eval "timeout ${EXPL_TIME_OUT}m $ECMD" 2>&1)
		RES=$(echo $RES | grep -v "^<" | tr '\n' '\r')
		echo $RES > $SOUT

		SIZE=$([[ -n "$(echo $RES | awk "/explored states/")" ]] && echo $RES | sed -E "s/.*explored states: *([0-9]+).*/\1/" || echo 0)
		
		echo $SIZE > $ZOUT
	fi
	
	rm -r $SCRATCH

done

echo "Cleaning /scratch"

rm -r $SCRATCH

exit 0
