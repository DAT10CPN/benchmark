#!/bin/bash

#SBATCH --time=22:00:00
#SBATCH --mail-type=FAIL
#SBATCH --partition=rome
#SBATCH --mem=15G
#SBATCH -c 4

# Args: <out-dir>
# This is the last step of `run_pipeline.sh`, but can also be run manually.
# This script will collect the data from all the raw output and size files belonging to the given test into a single `<binary>/<binary>/<test-name>.csv`.

OUT_DIR=$1

if [ -z "$OUT_DIR" ] ; then
	echo "Missing out directory"
	exit
fi

CSV="csvs/${OUT_DIR#*/}.csv"
TEST_FOLDER="$(basename "$(dirname "$CSV")")"

# ***** Setup CSV *****

COL_RULE_NAMES=("Relevance" "AtomicPreAgglomeration" "ParallelTransitions" "ParallelPlaces" "DeadTransitions" "RedundantPlaces" "PreemptiveFiring") # MUST MATCH NAMES AND ORDER IN VERIFYPN
NORMAL_RULE_NAMES=("A" "B" "C" "D" "E" "F" "G" "H" "I" "J" "K" "L" "M" "N" "O" "P" "Q" "R" "S")

mkdir -p "$(dirname $CSV)"
rm -f $CSV

# Write header
echo -n "model name,query index,answer,crash,colored reduce time,unfold time,reduce time,verification time,verification memory,solved by query simplification,state space size,original place count,original transition count,colored reduce place count,colored reduce transition count,unfolded place count,unfolded transition count,reduced place count,reduced transition count" >> $CSV
for i in ${!NORMAL_RULE_NAMES[@]} ; do
	echo -n ",rule ${NORMAL_RULE_NAMES[$i]}" >> $CSV
done
for i in ${!COL_RULE_NAMES[@]} ; do
	echo -n ",rule $i" >> $CSV
done
echo "" >> $CSV

# ***** Analysis *****

for MODEL in $(ls $TEST_FOLDER) ; do
	for Q in $(seq 1 16) ; do

		echo "Collecting from $OUT_DIR/$MODEL.$Q"

		ENTRY=""

		# ----- Files and meta vars -------

		RES_FILE="$OUT_DIR/$MODEL.$Q.out"
		SIZE_FILE="$OUT_DIR/$MODEL.$Q.size"

		# Get stdout of model, filter out transition and place-bound statistics, and replace new lines such that regex will work
		IN=$([[ -f $RES_FILE ]] && cat "$RES_FILE" | grep -v "^<"  | grep -v "^Query before" | grep -v "^Query after" | tr '\n' '\r' || echo "")

    CRASH="NONE"
		CRASH=$([[ -n "$(echo IN | awk "/signal/")" ]] && echo "SIGNAL" || echo $CRASH)
		CRASH=$([[ $CRASH = "NONE" ]] && ([[ -n "$(echo $ROUT | awk "/Error/")" ]] || [[ -n "$(echo $ROUT | awk "/ERROR/")" ]]) && echo "ERROR" || echo $CRASH)

		# ----- Exploration -----

		# Final state space size
		SIZE=$([[ -f $SIZE_FILE ]] && cat $SIZE_FILE || echo 0)

		# ----- Verification extraction -------

		# Time and memory is appended to the file
		VERI_TIME=$([[ -n "$(echo $IN | awk "/on verification/")" ]] && echo $IN | sed -E "s/.*Spent (([0-9](\.[0-9])?e-0[2-9])|([0-9]+(\.[0-9]+)?)) on verification.*/\1/" || echo 0.0)
		VERI_MEM=$([[ -n "$(echo $IN | awk "/@@@/")" ]] && echo $IN | sed -E "s/.*@@@.*,(.*)@@@.*/\1/" || echo 0)

		# Did we get an answer or did the query time out?
		# We can check this by checking if "satisfied" is a substring of the output.
		# If "Query is satisfied" is also a substring, then the answer is TRUE.
		ANSWER=$([[ -n "$(echo $IN | awk '/satisfied/')" ]] && ([[ -n "$(echo $IN | awk '/Query is satisfied/')" ]] && echo "TRUE" || echo "FALSE") || echo "NONE")

		# Was query solved using query reduction?
		QUERY_SIMPLIFICATION=$( ([[ -n "$(echo $IN | awk '/Query solved by Query Simplification/')" ]] && echo "TRUE") || echo "FALSE")

		# ----- Reduction extraction -------

	    # Reduced size
		RED_PLACE_COUNT=$([[ -n "$(echo $IN | awk '/Size of net after/')" ]] && echo $IN | sed -E "s/.*Size of net after[^:]*: ([0-9]+).*/\1/" || echo 0)
		RED_TRANS_COUNT=$([[ -n "$(echo $IN | awk '/Size of net after/')" ]] && echo $IN | sed -E "s/.*Size of net after[^:]*: [0-9]+ places, ([0-9]+).*/\1/" || echo 0)

		# Reduction time
		RED_TIME=$([[ -n "$(echo $IN | awk '/Structural reduction finished after/')" ]] && echo $IN | sed -E "s/.*Structural reduction finished after (([0-9](\.[0-9])?e-0[2-9])|([0-9]+(\.[0-9]+)?)) s.*/\1/" || echo 0.0)

		# ----- Colored reduction and unfolding extraction -----

		COL_RED_ACTIVE=$([[ -n "$(echo $IN | awk '/Colored structural reductions computed/')" ]] && echo "TRUE" || echo "FALSE")

		if [[ $COL_RED_ACTIVE = "TRUE" ]]; then

			COL_RED_TIME=$([[ -n "$(echo $IN | awk '/Colored structural reductions computed/')" ]] && echo $IN | sed -E "s/.*Colored structural reductions computed in (([0-9](\.[0-9])?e-0[2-9])|([0-9]+(\.[0-9]+)?)) s.*/\1/" || echo 0.0)
			ORIG_PLACE_COUNT=$([[ -n "$(echo $IN | awk '/Reduced from /')" ]] && echo $IN | sed -E "s/.*Reduced from ([0-9]+) to [0-9]+ places.*/\1/" || echo 0)
			ORIG_TRANSITION_COUNT=$([[ -n "$(echo $IN | awk '/Reduced from /')" ]] && echo $IN | sed -E "s/.*Reduced from ([0-9]+) to [0-9]+ transitions.*/\1/" || echo 0)
			COL_RED_PLACE_COUNT=$([[ -n "$(echo $IN | awk '/Reduced from /')" ]] && echo $IN | sed -E "s/.*Reduced from [0-9]+ to ([0-9]+) places.*/\1/" || echo 0)
			COL_RED_TRANSITION_COUNT=$([[ -n "$(echo $IN | awk '/Reduced from /')" ]] && echo $IN | sed -E "s/.*Reduced from [0-9]+ to ([0-9]+) transitions.*/\1/" || echo 0)

		else

			COL_RED_TIME="0.0"
			
			ORIG_PLACE_COUNT=$([[ -n "$(echo $IN | awk '/Skipping colored structural reductions/')" ]] && echo $IN | sed -E "s/.*Net consists of ([0-9]+) places.*/\1/" || echo 0)
			ORIG_TRANSITION_COUNT=$([[ -n "$(echo $IN | awk '/Skipping colored structural reductions/')" ]] && echo $IN | sed -E "s/.*Net consists of [0-9]+ places and ([0-9]+) transitions.*/\1/" || echo 0)
			COL_RED_PLACE_COUNT=$ORIG_PLACE_COUNT
			COL_RED_TRANSITION_COUNT=$ORIG_TRANSITION_COUNT
		fi

		UNFOLD_TIME=$([[ -n "$(echo $IN | awk '/Unfolded in/')" ]] && echo $IN | sed -E "s/.*Unfolded in (([0-9](\.[0-9])?e-0[2-9])|([0-9]+(\.[0-9]+)?)) s.*/\1/" || echo 0.0)
		UNF_PLACE_COUNT=$([[ -n "$(echo $IN | awk '/Size of unfolded net:/')" ]] && echo $IN | sed -E "s/.*Size of unfolded net: ([0-9]+) places.*/\1/" || echo 0)
		UNF_TRANSITION_COUNT=$([[ -n "$(echo $IN | awk '/Size of unfolded net:/')" ]] && echo $IN | sed -E "s/.*Size of unfolded net: [0-9]+ places, ([0-9]+) transitions.*/\1/" || echo 0)

		# ----- Entry so far -----

		ENTRY+="$MODEL,$Q,$ANSWER,$CRASH,$COL_RED_TIME,$UNFOLD_TIME,$RED_TIME,$VERI_TIME,$VERI_MEM,$QUERY_SIMPLIFICATION,$SIZE,$ORIG_PLACE_COUNT,$ORIG_TRANSITION_COUNT,$COL_RED_PLACE_COUNT,$COL_RED_TRANSITION_COUNT,$UNF_PLACE_COUNT,$UNF_TRANSITION_COUNT,$RED_PLACE_COUNT,$RED_TRANS_COUNT"

		# ----- Rule applications -----

		# Extract applications of rules
		ALL_APPS=$([[ -n "$(echo $IN | awk '/Applications of rule/')" ]] && echo $IN | grep 'Applications of rule' || echo "")
		
		for i in ${!NORMAL_RULE_NAMES[@]} ; do
			APPLICATIONS=$([[ -n "$(echo $ALL_APPS | awk "/Applications of rule ${NORMAL_RULE_NAMES[$i]}:/")" ]] && echo $ALL_APPS | sed -E "s/.*Applications of rule ${NORMAL_RULE_NAMES[$i]}: ([0-9]+).*/\1/" || echo 0)
			ENTRY+=",$APPLICATIONS"
		done

		for i in ${!COL_RULE_NAMES[@]} ; do
			APPLICATIONS=$([[ -n "$(echo $ALL_APPS | awk "/Applications of rule ${COL_RULE_NAMES[$i]}:/")" ]] && echo $ALL_APPS | sed -E "s/.*Applications of rule ${COL_RULE_NAMES[$i]}: ([0-9]+).*/\1/" || echo 0)
			ENTRY+=",$APPLICATIONS"
		done

		# Add entry to CSV
		echo $ENTRY >> $CSV
	done
done

echo "Done"
