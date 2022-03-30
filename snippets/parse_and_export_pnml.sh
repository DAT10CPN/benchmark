MCC_FOLDER = $1
BINARY = $2
for MODEL in $(ls $MCC_FOLDER) ; do
  ./$BINARY -R 0 -x 1 $MCC_FOLDE/$MODEL/model.pnml $MCC_FOLDE/$MODEL/ReachabilityCardinality.xml  --write-col-reduced $MCC_FOLDE/$MODEL/model.pnml --nounfold -n
	echo "Parsed and exported $MODEL pnml file"
done