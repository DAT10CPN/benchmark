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

COL_RULE_NAMES=("ParallelPlaces" "ParallelTransitions")
NORMAL_RULE_NAMES=("A" "B" "C" "D" "E" "F" "G" "H" "I")

rm -f $OUT

# Write header
echo -n "model name,query index,answer,colored reduce time,unfold time,reduce time,verification time,verification memory,solved by query simplification,state space size,original place count,original transition count,colored reduce place count,colored reduce transition count,unfolded place count, unfolded transition count,reduced place count,reduced transition count" >> $OUT
for i in ${!NORMAL_RULE_NAMES[@]} ; do
	echo -n ",rule ${NORMAL_RULE_NAMES[$i]}" >> $OUT
done
for i in ${!COL_RULE_NAMES[@]} ; do
	echo -n ",rule ${COL_RULE_NAMES[$i]}" >> $OUT
done
echo "" >> $OUT

# ***** Analysis *****

for COL_RED_RES_FILE in $(ls $DIR | grep "\.uout$") ; do

	echo "Collecting from $DIR/$COL_RED_RES_FILE"

	ENTRY=""

	# ----- Files and meta vars -------

	# Model/query data from COL_RED_RES_FILE name (Expected form is "<model>.<query>.uout")
	MODEL=$(echo $COL_RED_RES_FILE | sed -E "s/([^\.]*).*/\1/")
	Q=$(echo $COL_RED_RES_FILE | sed -E "s/[^\.]*\.([0-9]*).*/\1/")

	RED_RES_FILE="$DIR/$MODEL.$Q.rout"
	VERI_RES_FILE="$DIR/$MODEL.$Q.vout"

	# Get stdout of model, filter out transition and place-bound statistics, and replace new lines such that regex will work
	UOUT=$(cat "$DIR/$COL_RED_RES_FILE" | grep -v "^<" | tr '\n' '\r')
	ROUT=$([[ -f $RED_RES_FILE ]] && cat "$RED_RES_FILE" | grep -v "^<" | tr '\n' '\r' || echo "")
	VOUT=$([[ -f $VERI_RES_FILE ]] && cat $VERI_RES_FILE | grep -v "^<" | tr '\n' '\r' || echo "@@@0,0@@@")

	# ----- Exploration -----

	# Final state space size
	SIZE_FILE="$DIR/$MODEL.$Q.size"
	SIZE=$([[ -f $SIZE_FILE ]] && cat $SIZE_FILE || echo 0)

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

    # Reduced size
	RED_PLACE_COUNT=$([[ -n "$(echo $ROUT | awk '/Size of net after/')" ]] && echo $ROUT | sed -E "s/.*Size of net after[^:]*: ([0-9]+).*/\1/" || echo 0)
	RED_TRANS_COUNT=$([[ -n "$(echo $ROUT | awk '/Size of net after/')" ]] && echo $ROUT | sed -E "s/.*Size of net after[^:]*: [0-9]+ places, ([0-9]+).*/\1/" || echo 0)

	# Reduction time
	RED_TIME=$([[ -n "$(echo $ROUT | awk '/Structural reduction finished after/')" ]] && echo $ROUT | sed -E "s/.*Structural reduction finished after (([0-9](\.[0-9])?e-0[2-9])|([0-9]+(\.[0-9]+)?)) s.*/\1/" || echo 0.0)

	# ----- Colored reduction and unfolding extraction -----

	COL_RED_ACTIVE=$([[ -n "$(echo $UOUT | awk '/Colored structural reductions computed/')" ]] && echo "TRUE" || echo "FALSE")

	if [[ $COL_RED_ACTIVE = "TRUE" ]]; then

		COL_RED_TIME=$([[ -n "$(echo $UOUT | awk '/Colored structural reductions computed/')" ]] && echo $UOUT | sed -E "s/.*Colored structural reductions computed in (([0-9](\.[0-9])?e-0[2-9])|([0-9]+(\.[0-9]+)?)) s.*/\1/" || echo 0.0)
		ORIG_PLACE_COUNT=$([[ -n "$(echo $UOUT | awk '/Reduced from /')" ]] && echo $UOUT | sed -E "s/.*Reduced from ([0-9]+) to [0-9]+ places.*/\1/" || echo 0)
		ORIG_TRANSITION_COUNT=$([[ -n "$(echo $UOUT | awk '/Reduced from /')" ]] && echo $UOUT | sed -E "s/.*Reduced from ([0-9]+) to [0-9]+ transitions.*/\1/" || echo 0)
		COL_RED_PLACE_COUNT=$([[ -n "$(echo $UOUT | awk '/Reduced from /')" ]] && echo $UOUT | sed -E "s/.*Reduced from [0-9]+ to ([0-9]+) places.*/\1/" || echo 0)
		COL_RED_TRANSITION_COUNT=$([[ -n "$(echo $UOUT | awk '/Reduced from /')" ]] && echo $UOUT | sed -E "s/.*Reduced from [0-9]+ to ([0-9]+) transitions.*/\1/" || echo 0)

	else

		COL_RED_TIME="0.0"
		
		# Colored reduction is not performed, so we get the sizes from the unfolding instead
		ORIG_PLACE_COUNT=$([[ -n "$(echo $UOUT | awk '/Size of colored net:/')" ]] && echo $UOUT | sed -E "s/.*Size of colored net: ([0-9]+) places.*/\1/" || echo 0)
		ORIG_TRANSITION_COUNT=$([[ -n "$(echo $UOUT | awk '/Size of colored net:/')" ]] && echo $UOUT | sed -E "s/.*Size of colored net: [0-9]+ places, ([0-9]+) transitions.*/\1/" || echo 0)
		COL_RED_PLACE_COUNT=$ORIG_PLACE_COUNT
		COL_RED_TRANSITION_COUNT=$ORIG_TRANSITION_COUNT
	fi

	UNFOLD_TIME=$([[ -n "$(echo $UOUT | awk '/Unfolded in/')" ]] && echo $UOUT | sed -E "s/.*Unfolded in (([0-9](\.[0-9])?e-0[2-9])|([0-9]+(\.[0-9]+)?)) s.*/\1/" || echo 0.0)
	UNF_PLACE_COUNT=$([[ -n "$(echo $UOUT | awk '/Size of unfolded net:/')" ]] && echo $UOUT | sed -E "s/.*Size of unfolded net: ([0-9]+) places.*/\1/" || echo 0)
	UNF_TRANSITION_COUNT=$([[ -n "$(echo $UOUT | awk '/Size of unfolded net:/')" ]] && echo $UOUT | sed -E "s/.*Size of unfolded net: [0-9]+ places, ([0-9]+) transitions.*/\1/" || echo 0)

	# ----- Entry so far -----

	ENTRY+="$MODEL,$Q,$ANSWER,$COL_RED_TIME,$UNFOLD_TIME,$RED_TIME,$VERI_TIME,$VERI_MEM,$QUERY_SIMPLIFICATION,$SIZE,$ORIG_PLACE_COUNT,$ORIG_TRANSITION_COUNT,$COL_RED_PLACE_COUNT,$COL_RED_TRANSITION_COUNT,$UNF_PLACE_COUNT,$UNF_TRANSITION_COUNT,$RED_PLACE_COUNT,$RED_TRANS_COUNT"

	# ----- Rule applications -----

	# Extract applications of rules
	ROUT_APPLICATIONS=$(echo $ROUT | grep 'Applications of rule')
	for i in ${!NORMAL_RULE_NAMES[@]} ; do
		APPLICATIONS=$([[ -n "$(echo $ROUT_APPLICATIONS | awk "/Applications of rule ${NORMAL_RULE_NAMES[$i]}/")" ]] && echo $ROUT_APPLICATIONS | sed -E "s/.*Applications of rule ${NORMAL_RULE_NAMES[$i]}: ([0-9]+).*/\1/" || echo 0)
		ENTRY+=",$APPLICATIONS"
	done
	UOUT_APPLICATIONS=$(echo $UOUT | grep 'Applications of rule')
	for i in ${!COL_RULE_NAMES[@]} ; do
		APPLICATIONS=$([[ -n "$(echo $UOUT_APPLICATIONS | awk "/Applications of rule ${COL_RULE_NAMES[$i]}/")" ]] && echo $UOUT_APPLICATIONS | sed -E "s/.*Applications of rule ${COL_RULE_NAMES[$i]}: ([0-9]+).*/\1/" || echo 0)
		ENTRY+=",$APPLICATIONS"
	done

	# Add entry to CSV
	echo $ENTRY >> $OUT
done

echo "Done"
