rm ./dist/*
cd ./src/
javac -source 1.6 -target 1.6 -classpath /Applications/Micro-Manager1.4/ij.jar -Xlint:unchecked -sourcepath . -d ../dist Preprocessor_2.java

cd ../dist/
jar cvf Preprocessor_2.jar *.class

cp -f ./Preprocessor_2.jar /Applications/Micro-Manager1.4/plugins/
