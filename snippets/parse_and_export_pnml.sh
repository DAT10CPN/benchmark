MCC_FOLDER=$1
BINARY=$2
for MODEL in $(ls $MCC_FOLDER) ; do
  ./$BINARY -R 0 -x 1 $MCC_FOLDER/$MODEL/model.pnml $MCC_FOLDER/$MODEL/ReachabilityCardinality.xml  --write-col-reduced $MCC_FOLDER/$MODEL/model.pnml --nounfold -n
	echo "Parsed and exported $MODEL pnml file"
done

zip -r $MCC_FOLDER/../MCC2021-COL-PnmlTest.zip $MCC_FOLDER