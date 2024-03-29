![alt text][logo]

[logo]: bugtracker_logo.jpg

# BugTracker

Contents
--------

1. [About](#about)
2. [Installation](#installation)
3. [Usage](#usage)

About
-----

Installation
------------
BugTracker works on Windows and Linux (Mac not tested, but probably). Below is a step by step guide how to install the software dependencies. 

a) First you need to download and install Python from the offical website: https://www.python.org/downloads/ 

b) Then if you are using Windows open the Command Prompt by clicking Start and then typing “cmd” into the search box. In Linux, just open the terminal.

c) Write the following lines one-by-one:
- pip install opencv-contrib-python
- pip install imutils
- pip install scikit-image
- pip install matplotlib

d) To download BugTracker code go to [Github](https://github.com/Roffagalaxis/Bugtracker) and click on the green "Code" button, then click on "Download Zip"

e) Unzip the folder

Usage
-----
Open your Command Prompt/Terminal and navigate to the folder where you unzipped the code

Help to parameters:\
python Bugtracker.py -h 

Run a video:\
python Bugtracker.py [parameters] [Path to the video to track]

Example on Windows:\
python Bugtracker.py C:/Users/YourName/Download/Bugtracker-main/Bugtracker-main/Videos/TestVideo.mp4

After video is started you should wait until the petri dish was lifted up, then:\
a) Press "F" to stop the video and select the animal with the mouse\
b) Press "Space"

Parameters
----------
-r = Rotate the video 90° (Default: False)\
-c = Draw squares (Default: False)\
-d = Automaticaly detech boundaries (Default: False)\
-p = Don't print the number of reached squares to the output (Default: True)\
-w = Don't wait after the video is finished (Default: True)

If you added "-c" parameter to create an testarea with squares\
c) Do A and B step then select the area with mouse\
d) Press "Space"\
e) Adjust the squares with "W","A","S" and "D" buttons

You can check running the example here:

Thank you for using BugTracker!
