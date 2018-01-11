Two main (and very similar) Python 3 scripts were used to collect the data shown in this research article:

1) RR_vs_insert_vs_dmi8.py

2) RR_fast_volumes_preview.py

The exact script for each data set was not kept as it amounted only to minor changes in stack amplitude, step size, exposure, etc or changes in the order of operation or routine depending on the experiment. To run these scripts the user will need the following additional Python 3 scripts included in the directory:

image_data_pipeline.py

lumencor.py

ni.py

pco.py

physik_instrumente.py

leica_scope.py ***NOT INCLUDED*** (the leica control code has not been made public)

The user will also need to install the following Python package:

serial ( https://pypi.python.org/pypi/pyserial )

numpy ( http://www.numpy.org/ )

The scripts also import these built-in python modules, which should already be included with your Python distribution:

time

tkinter

ctypes
