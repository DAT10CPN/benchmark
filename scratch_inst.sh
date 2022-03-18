#!/bin/bash

#SBATCH --time=12:00:00
#SBATCH --mail-type=FAIL
#SBATCH --mem=15G
#SBATCH -c 1

# Args: <test-name> <binary> <test-folder> <model> <category> <col-red-time-out> <red-time-out> <veri-time-out> <expl-time-out> <bin-options>

echo "Arguments: $@"

NAME=$1
BIN=$2
TEST_FOLDER=$3
MODEL=$4
CATEGORY=$5
COL_RED_TIME_OUT=$6
RED_TIME_OUT=$7
VERI_TIME_OUT=$8
EXPL_TIME_OUT=$9
OPTIONS="${10}"

SCRATCH="/scratch/jesmatnic/$NAME/$MODEL/$CATEGORY"

LTLFLAG=$([[ "$CATEGORY" == "LTLCardinality" ]] && echo " -ltl" || echo "")

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

	UCMD="./$BIN $OPTIONS -D $COL_RED_TIME_OUT -r 0 -q 0 -x $Q $LTLFLAG $TEST_FOLDER/$MODEL/model.pnml $TEST_FOLDER/$MODEL/$CATEGORY.xml --noverify --write-unfolded-net $UPNML --write-unfolded-queries $UQUERIES"
	UOUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.uout"

	# Reduce model+unfold and store stdout

	O=$(eval "$UCMD" 2>&1)
	echo "$O" > "$UOUT"

	# ===================== NORMAL REDUCTION ========================

	echo "  Reduction ..."

	RCMD="./$BIN $OPTIONS -d $RED_TIME_OUT -q 0 -x $Q $LTLFLAG $UPNML $UQUERIES --write-reduced $PNML --noverify"
	ROUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.rout"
	
	# Reduce model+query and store stdout

	O=$(eval "$RCMD" 2>&1)
	echo "$O" > "$ROUT"

	# ===================== VERIFICATION =====================

	if [ "$VERI_TIME_OUT" -eq "0" ] ; then
		echo "  Verification skipped"
	else
		echo "  Verification ..."

		VCMD="./$BIN -r 0 -x $Q $LTLFLAG $PNML $UQUERIES"
		VOUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.vout"
		
		# Verify query and store stdout along with time and memory spent between @@@s
		O=$(eval "/usr/bin/time -f '@@@%e,%M@@@' timeout ${VERI_TIME_OUT}m $VCMD" 2>&1)
		echo "$O" > "$VOUT"
	fi

	# ===================== EXPLORATION ======================

	if [ "$EXPL_TIME_OUT" -eq "0" ] ; then
		echo "  Exploration skipped"
	else
		echo "  Exploration ..."

		ECMD="./$BIN -q 0 -r 0 $PNML -e"
		SOUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.sout"
		ZOUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.size"

		RES=$(eval "timeout ${EXPL_TIME_OUT}m $ECMD" 2>&1)
		RES=$(echo $RES | grep -v "^<" | tr '\n' '\r')
		echo $RES > $SOUT

		SIZE=$([[ -n "$(echo $RES | awk "/explored states/")" ]] && echo $RES | sed -E "s/.*explored states: *([0-9]+).*/\1/" || echo 0)
		
		echo $SIZE > $ZOUT
	fi
	
done

echo "Cleaning /scratch"

rm -r $SCRATCH

exit 0
