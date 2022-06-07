#!/bin/bash
#SBATCH --partition=cpu
#SBATCH --mem=15G
#SBATCH -c 1

# Args: <binary> [sequence] [category] [test-folder] [search-strat] [col-red-time-out] [red-time-out] [combined-time-out] [expl-time-out]
# - sequences default is ALL, write "<name>/<options>" for specific sequence, e.g.: "orig/-R 0"
# - category DEFAULT is ReachabilityCardinality (Reachability, LTL, CTL, and ALL is valid categories)
# - test-folder DEFAULT is MCC2021-COL
# - search-start DEFAULT is DFS
# This starts multiple pipelines using the given rule sequences, categories, test folder, and search strategy

BIN=$1
SEQUENCE=$2
CATEGORY=$3
TEST_FOLDER=$4
SEARCH_STRAT=$5
COL_RED_TIME_OUT=$6
RED_TIME_OUT=$7
COMB_TIME_OUT=$8
EXPL_TIME_OUT=$9

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
if [ -z "$SEQUENCE" ] ; then
  echo "No SEQUENCE given, using ALL"
  SEQUENCE="ALL"
fi
if [ "$SEQUENCE" = "ALL" ] ; then
  SEQUENCE=("orig/-R 0" "I/-R 2 0" "S/-R 2 1" "D/-R 2 2" "C/-R 2 3" "E/-R 2 4" "F/-R 2 5" "Q/-R 2 6" "ISDCEFQ/-R 2 0,1,2,3,4,5,6")
fi
for SEQ in "${SEQUENCE[@]}" ; do
  OPTIONS="${SEQ#*/}"

  if [ -z "$OPTIONS" ] ; then
    echo "Missing binary options in SEQUENCE: '$SEQ'"
    exit
  elif ! [[ "$OPTIONS" =~ $pat1 ]] && ! [[ "$OPTIONS" =~ $pat2 ]] ; then
    echo "Err: OPTIONS must start with '-R [0-1]' or '-R 2 [0-9]'. It is '$OPTIONS' in SEQUENCE '$SEQ'"
    exit 0
  fi
done

if [ -z "$CATEGORY" ] ; then
	echo "No CATEGORY given, using ReachabilityCardinality"
	CATEGORY="ReachabilityCardinality"
elif [ "$CATEGORY" != "ALL" ] && [ "$CATEGORY" != "Reachability" ] && [ "$CATEGORY" != "LTL" ] && [ "$CATEGORY" != "CTL" ] && [ "$CATEGORY" != "ReachabilityCardinality" ] && [ "$CATEGORY" != "LTLCardinality" ] && [ "$CATEGORY" != "CTLCardinality" ] && [ "$CATEGORY" != "ReachabilityFireability" ] && [ "$CATEGORY" != "LTLFireability" ] && [ "$CATEGORY" != "CTLFireability" ] ; then
	echo "Err: CATEGORY must be ALL, Reachability, LTL, CTL, ReachabilityCardinality, LTLCardinality, CTLCardinality, ReachabilityFireability, LTLFireability, or CTLFireability. It is '$CATEGORY'"
	exit 0
fi
if [ "$CATEGORY" = "ALL" ] ; then
  CATEGORY=("ReachabilityCardinality" "ReachabilityFireability" "LTLCardinality" "LTLFireability" "CTLCardinality" "CTLFireability")
elif [ "$CATEGORY" = "Reachability" ] ; then
  CATEGORY=("ReachabilityCardinality" "ReachabilityFireability")
elif [ "$CATEGORY" = "LTL" ] ; then
  CATEGORY=("LTLCardinality" "LTLFireability")
elif [ "$CATEGORY" = "CTL" ]; then
  CATEGORY=("CTLCardinality" "CTLFireability")
fi

if [ -z "$TEST_FOLDER" ] ; then
	echo "No TEST_FOLDER given, using DEFAULT (MCC2021-COL)"
	TEST_FOLDER="DEFAULT"
elif [ "$TEST_FOLDER" != "DEFAULT" ] && [ "$TEST_FOLDER" != "MCC2021-COL" ] && [ "$TEST_FOLDER" != "MCC2021-COL-PnmlTest" ] && [ "$TEST_FOLDER" != "MCC2021-COL-inhib" ] && [ "$TEST_FOLDER" != "MCC2021" ]; then
	echo "Err: TEST_FOLDER must be 'DEFAULT', 'MCC2021-COL', 'MCC2021-COL-inhib', 'MCC2021-COL-PnmlTest', or 'MCC2021'. It is '$TEST_FOLDER'"
	exit 0
fi
if [ "$TEST_FOLDER" = "DEFAULT" ] ; then
  TEST_FOLDER="MCC2021-COL"
fi

if [ -z "$SEARCH_STRAT" ] ; then
	echo "No SEARCH_STRAT given, using DEFAULT (DFS)"
	SEARCH_STRAT="DEFAULT"
elif [ "$SEARCH_STRAT" != "DEFAULT" ] && [ "$SEARCH_STRAT" != "BestFS" ] && [ "$SEARCH_STRAT" != "BFS" ] && [ "$SEARCH_STRAT" != "DFS" ] && [ "$SEARCH_STRAT" != "RDFS" ] && [ "$SEARCH_STRAT" != "OverApprox" ] ; then
	echo "Err: SEARCH_STRAT must be DEFAULT, BestFS, BFS, DFS, RDFS, or OverApprox. It is '$SEARCH_STRAT'"
	exit 0
fi
if [ "$SEARCH_STRAT" = "DEFAULT" ] ; then
  SEARCH_STRAT="DFS"
fi

pat="^[0-9]+$"

if [ -z "$COL_RED_TIME_OUT" ] ; then
	echo "No COL_RED_TIME_OUT given, using 4 seconds per query"
	COL_RED_TIME_OUT=4
elif ! [[ "$COL_RED_TIME_OUT" =~ $pat ]] ; then
	echo "Err: COL_RED_TIME_OUT must be a non-negative integer (seconds). It is '$COL_RED_TIME_OUT'"
	exit 0
fi

if [ -z "$RED_TIME_OUT" ] ; then
	echo "No RED_TIME_OUT given, using 30 seconds per query"
	RED_TIME_OUT=30
elif ! [[ "$RED_TIME_OUT" =~ $pat ]] ; then
	echo "Err: RED_TIME_OUT must be a non-negative integer (seconds). It is '$RED_TIME_OUT'"
	exit 0
fi

if [ -z "$COMB_TIME_OUT" ] ; then
	echo "No COMB_TIME_OUT given, using 4 minute per query"
	COMB_TIME_OUT=4
elif ! [[ "$COMB_TIME_OUT" =~ $pat ]] ; then
	echo "Err: COMB_TIME_OUT must be a non-negative integer (minutes). It is '$COMB_TIME_OUT'"
	exit 0
fi

if [ -z "$EXPL_TIME_OUT" ] ; then
	echo "No EXPL_TIME_OUT given, using 2 minute per query"
	EXPL_TIME_OUT=2
elif ! [[ "$EXPL_TIME_OUT" =~ $pat ]] ; then
	echo "Err: EXPL_TIME_OUT must be a non-negative integer (minutes). It is '$EXPL_TIME_OUT'"
	exit 0
fi

chmod u+x "$BIN"

patReach="^Reachability"
patLTL="^LTL"
patCTL="^CTL"

for C in "${CATEGORY[@]}" ; do

  PARTITION="naples"
  if [[ "$C" =~ $patReach ]] ; then
    PARTITION="dhabi"
  elif [[ "$C" =~ $patLTL ]] ; then
    PARTITION="rome"
  elif [[ "$C" =~ $patCTL ]] ; then
    PARTITION="rome"
  fi

  for TF in "${TEST_FOLDER[@]}" ; do
    for SS in "${SEARCH_STRAT[@]}" ; do
      for SEQ in "${SEQUENCE[@]}" ; do
        NAME="${SEQ%/*}"
        OPTIONS="${SEQ#*/}"

        echo "Starting: sbatch ./run_ioless_pipeline.sh $NAME $BIN '$OPTIONS' $TF $C $PARTITION $SS $COL_RED_TIME_OUT $RED_TIME_OUT $COMB_TIME_OUT $EXPL_TIME_OUT"
        sbatch ./run_ioless_pipeline.sh $NAME $BIN "$OPTIONS" $TF $C $PARTITION $SS $COL_RED_TIME_OUT $RED_TIME_OUT $COMB_TIME_OUT $EXPL_TIME_OUT
      done
    done
  done
done
