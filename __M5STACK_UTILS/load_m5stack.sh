#!/bin/sh
#############################################
# Just a quick script to push all the files #
# back onto the m5stack after a firmware    #
# update or on a new unit.                  #
#############################################

cd ..

for file in *.py;
  do 
    echo "Transferring $file ..."; 
    ampy put $file; 
    echo "Done with $file"; 
    echo '---';
  done

    echo "Transferring /tests ..."; 
ampy put tests
    echo "Done with /tests"; 
    echo '-              -';


    echo "Transferring /m5stack-tools ..."; 
cd m5stack-tools/firmware
ampy put lib
    echo "Done with m5stack-tools"; 
    echo '-                      -';

