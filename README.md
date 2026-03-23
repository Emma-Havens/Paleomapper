# PaleoMapper
PaleoMapper was developed by Emma Havens and based on the plate tectonic mapping programs written by Chris Scotese (see Scotese et al., 1975) and David Walsh (Walsh and Scotese, 1993). The goal of the program is to provide users with a quick way to make paleogeographic maps and animations. Colorful maps in a variety of map projections can be used as a framework to plot user-defined data points with a variety of symbols.

To learn more about PaleoMapper and see some examples, visit [earthhistory.com](https://earthhistory.com)
# Installation Instructions
1.	**Install conga-forge** *(If you already have conda installed, follow all environment building instructions in Step 1.5 instead.)* Follow all on-screen instructions and prompts. Some are repeated here for clarity.	
	- Go to https://conda-forge.org/download/ and download the proper installer for your machine
	- The release downloaded from the miniforge page is a .sh file. As found under the Installation instructions, to install mini forge, open Terminal and run ‘bash path-to-sh-file’ where path-to-sh-file is the path to the .sh file you downloaded, likely located in your Downloads folder.	
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
	- conda install cartopy=0.24.0 ffmpeg=7.1.1 matplotlib=3.8.4 numpy=1.26.4 pygplates=1.0.0 pyside6=6.9.0 simplekml=1.3.6 pandas=2.3.3

3. **Download PaleoMapper**
   - On this page, scroll to the top and locate the green button that says '<> Code'. Click on it and select 'Download ZIP' from the dropdown. A folder titled 'Paleomapper-main' should appear in your Downloads. If the .zip file does not automatically unpack into a folder, double click to unpack it into a folder. You may rename it to PaleoMapper and relocate it if you wish. 

4.	**Install VSCode** *(If you have a coding environment you otherwise prefer and do not want to use VSCode, make sure you switch your python interpreter to the Python3.10 that is in the geoenv so the program can find all of its dependencies.)*
	- Go to https://code.visualstudio.com and download and install the application
	- Open VSCode and go to File > Open Folder… and open the PaleoMapper folder
 	- VSCode may prompt you to install python with an obstructive pop-up over the main window. If so, click 'close'.
	- Double click on main.py found in the left sidebar to open it
	- Optional: VSCode may prompt you to install the Python extension with a popup in the bottom right corner. The extension will help you locate errors if there are issues running the code. Click ‘Install’. When it's done, close the tab.
	- Change the python interpreter and terminal environment to our Python3.10 (geoenv). In the very bottom-right corner on the toolbar, click where you see something like base (3.X.X) or Python (3.X.X), which should bring up a dropdown menu in the top center of the screen titled 'Select a Python Environment'. Select geoenv (3.10.X) from the list. The bottom-right corner should now show geoenv (3.10.X). Right next to it on the left, click where you see something like 3.X.X or 3.X.X (base), which should bring up a dropdown menu in the top center of the screen titled 'Select Interpreter'. Select Python 3.10.X (geoenv) from the list. The bottom-right corner should now show 3.10.X (geoenv).
	- Click the Run button (looks like a play symbol) in the top-right while in the main.py tab. If it does not work, you may need to click it again or restart VSCode. Happy mapping!
