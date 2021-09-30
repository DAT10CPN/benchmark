#!/bin/bash
#SBATCH --time=22:00:00
#SBATCH --mail-user=$(whoami)
#SBATCH --mail-type=FAIL
#SBATCH --partition=naples
#SBATCH --mem=15G

NAME=$1
OPTIONS=$2
TIMING="$3"
BIN="verifypn-linux64"
TEST_FOLDER="MCC2021"

if [ -z "$NAME" ] ; then
	echo "Missing benchmark name"
	exit
fi

if [ -z "$OPTIONS" ] ; then
	echo "Missing options"
	exit
fi

if [ -z "$TIMING" ] ; then
	echo "No timing given, using 1 minute per query"
	TIMING=1
fi

OUT="output/$NAME.csv"

write_headers() {
	# First check if the file exists, if not: insert row with headers
	if ! [[ -f "$OUT" ]] 
	then
		col1="model name"
		col2="query index"
		col3="time"
		col4="memory"
		col5="answer"
		col6="solved by query simplification"
		col7="prev place count"
		col8="prev transition count"
		col9="post place count"
		col10="post transition count"
		col11="rule A"
		col12="rule B"
		col13="rule C"
		col14="rule D"
		col15="rule E"
		col16="rule F"
		col17="rule G"
		col18="rule H"
		col19="rule I"
		col20="rule J"
		col21="rule K"
		col22="rule L"
		echo \"$col1\",\"$col2\",\"$col3\",\"$col4\",\"$col5\",\"$col6\",\"$col7\",\"$col8\",\"$col9\",\"${col10}\",\"${col11}\",\"${col12}\",\"${col13}\",\"${col14}\",\"${col15}\",\"${col16}\",\"${col17}\",\"${col18}\",\"${col19}\",\"${col20}\",\"${col21}\",\"${col22}\" >> $OUT
	fi
}

append_row() {
	echo \"$1\",\"$2\",\"$3\",\"$4\",\"$5\",\"$6\",\"$7\",\"$8\",\"$9\",\"${10}\",\"${11}\",\"${12}\",\"${13}\",\"${14}\",\"${15}\",\"${16}\",\"${17}\",\"${18}\",\"${19}\",\"${20}\",\"${21}\",\"${22}\" >> $OUT
}

write_headers

for TEST_TYPE in ReachabilityCardinality ; do
	for MODEL in $(ls $TEST_FOLDER) ; do
		
		echo "Running $MODEL"
		
		# Find the number of queries for this model by counting how many times "<property>" appears
		NQ=$(grep "<property>" "$TEST_FOLDER/$MODEL/$TEST_TYPE.xml" | wc -l)

		for Q in $(seq 1 $NQ ) ; do
			
			echo "	Q$Q"
			CMD="./binaries/$BIN $OPTIONS -x $Q $TEST_FOLDER/$MODEL/model.pnml $TEST_FOLDER/$MODEL/$TEST_TYPE.xml"
			
			# Execute test and store stdout in RES along with time and memory spent between @@@s
			# We also replace all newline characters \n with the character \r, since sed only works on one line at the time. https://unix.stackexchange.com/a/152389
			eval "/usr/bin/time -f "@@@%e,%M@@@" timeout ${TIMING}m $CMD" &> temp
			RES=$(cat temp | tr '\n' '\r')

			TIME=$(echo $RES | sed -E "s/.*@@@(.*),.*@@@.*/\1/")
			MEM=$(echo $RES | sed -E "s/.*@@@.*,(.*)@@@.*/\1/")

			# Did we get an answer or did the query time out?
			# We can check this by checking if "satisfied" is a substring of the output.
			# If "Query is satisfied" is also a substring, then the answer is TRUE.
			ANSWER=$([[ -n "$(echo $RES | awk '/satisfied/')" ]] && ([[ -n "$(echo $RES | awk '/Query is satisfied/')" ]] && echo "TRUE" || echo "FALSE") || echo "NONE")

			# Was query solved using query reduction?
			QUERY_SIMPLIFICATION=$([[ -n "$(echo $RES | awk '/Query solved by Query Simplification/')" ]] && echo "TRUE" || echo "FALSE")

			if [[ $ANSWER = "NONE" || $QUERY_SIMPLIFICATION = "TRUE" ]]; then

				# In this case, no structural reduction was performed

				PREV_PLACE_COUNT=0
				PREV_TRANS_COUNT=0
				POST_RED_PLACE_COUNT=0
				POST_RED_TRANS_COUNT=0

				RULE_A=0
				RULE_B=0
				RULE_C=0
				RULE_D=0
				RULE_E=0
				RULE_F=0
				RULE_G=0
				RULE_H=0
				RULE_I=0
				RULE_J=0
				RULE_K=0
				RULE_L=0
			
			else

				PREV_PLACE_COUNT=$(echo $RES | sed -E "s/.*Size of net before[^:]*: ([0-9]+).*/\1/")
				PREV_TRANS_COUNT=$(echo $RES | sed -E "s/.*Size of net before[^:]*: [0-9]+.*([0-9]+).*/\1/")
				POST_RED_PLACE_COUNT=$(echo $RES | sed -E "s/.*Size of net after[^:]*: ([0-9]+).*/\1/")
				POST_RED_TRANS_COUNT=$(echo $RES | sed -E "s/.*Size of net after[^:]*: [0-9]+.*([0-9]+).*/\1/")

				RULE_A=$(echo $RES | sed -E "s/.*Applications of rule A: ([0-9]+).*/\1/")
				RULE_B=$(echo $RES | sed -E "s/.*Applications of rule B: ([0-9]+).*/\1/")
				RULE_C=$(echo $RES | sed -E "s/.*Applications of rule C: ([0-9]+).*/\1/")
				RULE_D=$(echo $RES | sed -E "s/.*Applications of rule D: ([0-9]+).*/\1/")
				RULE_E=$(echo $RES | sed -E "s/.*Applications of rule E: ([0-9]+).*/\1/")
				RULE_F=$(echo $RES | sed -E "s/.*Applications of rule F: ([0-9]+).*/\1/")
				RULE_G=$(echo $RES | sed -E "s/.*Applications of rule G: ([0-9]+).*/\1/")
				RULE_H=$(echo $RES | sed -E "s/.*Applications of rule H: ([0-9]+).*/\1/")
				RULE_I=$(echo $RES | sed -E "s/.*Applications of rule I: ([0-9]+).*/\1/")
				RULE_J=$(echo $RES | sed -E "s/.*Applications of rule J: ([0-9]+).*/\1/")
				RULE_K=$(echo $RES | sed -E "s/.*Applications of rule K: ([0-9]+).*/\1/")
				RULE_L=$(echo $RES | sed -E "s/.*Applications of rule L: ([0-9]+).*/\1/")

			fi

			append_row $MODEL $Q $TIME $MEM $ANSWER $QUERY_SIMPLIFICATION $PREV_PLACE_COUNT $PREV_TRANS_COUNT $POST_RED_PLACE_COUNT $POST_RED_TRANS_COUNT $RULE_A $RULE_B $RULE_C $RULE_D $RULE_D $RULE_E $RULE_F $RULE_G $RULE_H $RULE_I $RULE_J $RULE_K $RULE_L
		done
	done
done
