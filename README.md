# PaleoMapper
PaleoMapper was developed by Emma Havens and based on the plate tectonic mapping programs written by Chris Scotese (see Scotese et al., 1975) and David Walsh (Walsh and Scotese, 1993). The goal of the program is to provide users with a quick way to make paleogeographic maps and animations. Colorful maps in a variety of map projections can be used as a framework to plot user-defined data points with a variety of symbols.

To learn more about PaleoMapper and see some examples, visit [earthhistory.com](https://earthhistory.com)
# Installation Instructions
1.	**Install conga-forge** *(If you already have conda installed, follow all environment building instructions in Step 1.5 instead.)* Follow all on-screen instructions and prompts. Some are repeated here for clarity.	
	- Go to https://conda-forge.org/download/ and download the proper installer for your machine
	- The release downloaded from the miniforge page is a .sh file. As found under the Installation instructions, to install mini forge, open Terminal and run ‘bash \<path-to-sh-file\>’ where \<path-to-sh-file\> is the path to the .sh file you downloaded, likely located in your Downloads folder.	
	- Type ‘yes’ to accept the license agreement, or hit Enter until you are prompted to type ‘yes’	
	- Recommended: answer ‘yes’ to initialize conda on start up. Otherwise, make sure to note the start up command that conda provides in the print-out.	
	- Close and relaunch the terminal to activate conda

1.5. **Ensure packages are installed using conda-forge** *(You don't need to do this if you followed Step 1.)* Installing all the required packages using the conda-forge channel minimizes the risk of errors. Run the following commands:
<ul>
	<ul>
		<li>conda config --add channels conda-forge</li>
	</ul>
	<ul>
		<li>conda config --set channel_priority strict</li>
	</ul>
</ul>

2.	**Create the ‘geoenv’ conda environment** This is creating an isolated environment on your machine so that nothing else you have installed interferes with the program and its dependencies, and vice versa. Creating a separate environment to run PaleoMapper in greatly reduces risk of errors. Run the following commands:
	- conda create -n geoenv python=3.10
	- conda activate geoenv
	- conda install cartopy=0.24.0 ffmpeg=7.1.1 matplotlib=3.8.4 numpy=1.26.4 pygplates=1.0.0 pyside6=6.9.0 simplekml=1.3.6

3.	**Install VSCode** *(This is an optional step if you do not have a coding environment you otherwise prefer. If you do not want to use VSCode, make sure you switch your python interpreter to the Python3.10 that is in the geoenv so the program can find all of its dependencies.)*
	- Go to https://code.visualstudio.com and download the application
	- Open the program and go to File > Open Folder… and open the PaleoMapper folder
	- Open main.py
	- Optional: VSCode may prompt you to install the Python extension, which will help you locate errors if there are issues running the code. Click ‘yes’
	- Change the python interpreter to our Python3.10 (geoenv). In the bottom-right corner on the toolbar, click where you see something like 3.X.X (base), which should bring up a dropdown menu in the top center of the screen. Select Python 3.10.X (geoenv) from the list. The bottom-right corner should now show the information for the geoenv interpreter, rather than the base.
	- Click the Run button in the top-right while in the main.py tab. Happy mapping!
