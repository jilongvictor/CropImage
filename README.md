CropImage is a Python script and a graphic user interface (GUI). It is for croping an image such as bead image. 

Requirement:
	Install PySimpleGUI if it is not available in your computer.
	command: pip install pysimplegui

Run:
	1)	Python CropImage.py
	2)	Type input and output files;
	3)	Click and drag mouse to make a ROI (Region of Interest);
	4)	Click "Remove" to remove points within the ROI;
	5)	Click "Cancel" to cancel the last removal;
	6)	Click "Save" to output the selection;
	7)	Click "Exit" to close the window.

Notice: 
	1)	CropImage accepts 1 input file containing at least 3 columns: 1-x coordinate, 2-y coordinate, 3-color scale number (e.g. # UMIs);
	2)  The output file contains a list of binary numbers (0 or 1) indicating if the point is selected (1) or removed (0);
	3)	It works on both Windows and Mac;
	4)	If color scale number is not available, put a list of fixed numbers like 100 or random numbers there;
	5)	The ROI is not expected to be too complicated (both convex and concave should work);
	6)	Dragging mouse slowly makes it work better.

If you have any questions, comments or requests, please contact jilong@broadinstitute.org
