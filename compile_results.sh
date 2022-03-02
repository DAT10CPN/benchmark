#!/bin/bash

#SBATCH --time=22:00:00
#SBATCH --mail-type=FAIL
#SBATCH --partition=rome
#SBATCH --mem=15G
#SBATCH -c 4

# Args: <test-name> <binary>
# This is the last step of `run_pipeline.sh`, but can also be run manually.
# This script will collect the data from all the raw output and size files belonging to the given test into a single `<binary>/<binary>/<test-name>.csv`.

NAME=$1
BIN=$(basename $2)

if [ -z "$NAME" ] ; then
	echo "Missing benchmark name"
	exit
fi

if [ -z "$BIN" ] ; then
	echo "Missing binary"
	exit
fi

DIR="output/$BIN/$NAME"
OUT="output/$BIN/$NAME.csv"

# ***** Setup CSV *****

RULE_NAMES=()

rm -f $OUT

# Write header
echo -n "model name,query index,verification time,verification memory,answer,solved by query simplification,prev place count,prev transition count,post place count,post transition count,reduce time,state space size" >> $OUT
for i in ${!RULE_NAMES[@]} ; do
	echo -n ",rule ${RULE_NAMES[$i]}" >> $OUT
done
echo "" >> $OUT

# ***** Analysis *****

for RED_RES_FILE in $(ls $DIR | grep "\.rout$") ; do

	echo "Collecting from $DIR/$RED_RES_FILE"

	ENTRY=""

	# ----- Files and meta vars -------

	# Model/query data from RED_RES_FILE name (Expected form is "<model>.<query>.rout")
	MODEL=$(echo $RED_RES_FILE | sed -E "s/([^\.]*).*/\1/")
	Q=$(echo $RED_RES_FILE | sed -E "s/[^\.]*\.([0-9]*).*/\1/")

	VERI_RES_FILE="$DIR/$MODEL.$Q.vout"

	# Get stdout of model, filter out transition and place-bound statistics, and replace new lines such that regex will work
	ROUT=$(cat "$DIR/$RED_RES_FILE" | grep -v "^<" | tr '\n' '\r')
	VOUT=$([[ -f $VERI_RES_FILE ]] && cat $VERI_RES_FILE | grep -v "^<" | tr '\n' '\r' || echo "@@@0,0@@@")

	# ----- Verification extraction -------

	# Time and memory is appended to the file
	VERI_TIME=$([[ -n "$(echo $VOUT | awk "/on verification/")" ]] && echo $VOUT | sed -E "s/.*Spent (([0-9](\.[0-9])?e-0[2-9])|([0-9]+(\.[0-9]+)?)) on verification.*/\1/" || echo 0.0)
	VERI_MEM=$([[ -n "$(echo $VOUT | awk "/@@@/")" ]] && echo $VOUT | sed -E "s/.*@@@.*,(.*)@@@.*/\1/" || echo 0)

	# Did we get an answer or did the query time out?
	# We can check this by checking if "satisfied" is a substring of the output.
	# If "Query is satisfied" is also a substring, then the answer is TRUE.
	ANSWER=$([[ -n "$(echo $VOUT | awk '/satisfied/')" ]] && ([[ -n "$(echo $VOUT | awk '/Query is satisfied/')" ]] && echo "TRUE" || echo "FALSE") || echo "NONE")

	# Was query solved using query reduction?
	QUERY_SIMPLIFICATION=$([[ -n "$(echo $VOUT | awk '/Query solved by Query Simplification/')" ]] && echo "TRUE" || echo "FALSE")

	# ----- Reduction extraction -------

    # Total reduction size
	PREV_PLACE_COUNT=$([[ -n "$(echo $ROUT | awk '/Size of net before/')" ]] && echo $ROUT | sed -E "s/.*Size of net before[^:]*: ([0-9]+).*/\1/" || echo 0)
	PREV_TRANS_COUNT=$([[ -n "$(echo $ROUT | awk '/Size of net before/')" ]] && echo $ROUT | sed -E "s/.*Size of net before[^:]*: [0-9]+ places, ([0-9]+).*/\1/" || echo 0)
	POST_RED_PLACE_COUNT=$([[ -n "$(echo $ROUT | awk '/Size of net after/')" ]] && echo $ROUT | sed -E "s/.*Size of net after[^:]*: ([0-9]+).*/\1/" || echo 0)
	POST_RED_TRANS_COUNT=$([[ -n "$(echo $ROUT | awk '/Size of net after/')" ]] && echo $ROUT | sed -E "s/.*Size of net after[^:]*: [0-9]+ places, ([0-9]+).*/\1/" || echo 0)

	# Reduction time
	RED_TIME=$([[ -n "$(echo $ROUT | awk '/Structural reduction finished after/')" ]] && echo $ROUT | sed -E "s/.*Structural reduction finished after (([0-9](\.[0-9])?e-0[2-9])|([0-9]+(\.[0-9]+)?)) s.*/\1/" || echo 0.0)

	# Reduction state space size
	SIZE_FILE="$DIR/$MODEL.$Q.size"
	SIZE=$([[ -f $SIZE_FILE ]] && cat $SIZE_FILE || echo 0)

	ENTRY+="$MODEL,$Q,$VERI_TIME,$VERI_MEM,$ANSWER,$QUERY_SIMPLIFICATION,$PREV_PLACE_COUNT,$PREV_TRANS_COUNT,$POST_RED_PLACE_COUNT,$POST_RED_TRANS_COUNT,$RED_TIME,$SIZE"

	# Extract applications of rules
	ROUT_APPLICATIONS=$(echo $ROUT | grep 'Applications of rule')
	for i in ${!RULE_NAMES[@]} ; do

		APPLICATIONS=$([[ -n "$(echo $ROUT_APPLICATIONS | awk "/Applications of rule ${RULE_NAMES[$i]}/")" ]] && echo $ROUT_APPLICATIONS | sed -E "s/.*Applications of rule ${RULE_NAMES[$i]}: ([0-9]+).*/\1/" || echo 0)
		ENTRY+=",$APPLICATIONS"

	done

	# Add entry to CSV
	echo $ENTRY >> $OUT
done

echo "Done"
