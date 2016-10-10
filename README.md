# Poser Figure Shader

**A bit of a preface**: I realise this README.md is a bit long... unfortunately, it does contain key information necessary for the script to run correctly. **Please take the time to read this carefully.** I hope to eventually make the script more error-friendly and user-friendly, but at the moment it is what it is.
Also, this was previously called "Shaders-Addon", which wasn't particularly descriptive or even accurate, so if you're looking for that script, this is it (the newer version, that is).

**Poser Figure Shader** is a script to give Poser figures imported into Blender: skin, eyes and mouth shaders using an image set. These image sets are usually provided by the figure or character maker. The script runs in a panel [ T ] in the context of the the 3D Viewport window.

Shaders-Addon requires Blender 2.76 **or greater** to run. Download the current version of Blender at:

http://www.blender.org/download/

The current testing version of this add-on is 0.4.0, which is comprised of four files:

* \__init__.py: contains the panel code and stuff to create the shaders

* figure_defs.py: dictionary object containing material slot names and material types (skin / eyes / etc)

These reside in your scripts folder: Blender will install them there from the zip. Additionally, you will need:

* image_list.csv: **must be copied to the image folder for your figure, and edited**.

* path_list.csv: **must be copied to your .blend file folder, and edited**.
 
These files can be found in the zip file, but they need to be copied to their respective final folders **(and edited)** for the script to work. A copy of the csv files will be copied to the scripts folder, but will not be read by the script.

This script currently should work for the Victoria4, Dawn and Mariko figures, but has only been tested on the V4 figure so far.


# Instructions for Use
* If you haven't already done so, install Blender.

* Download the psrFigureShader-master.zip file (click the green Download button, then select DOWNLOAD ZIP), and unzip it. Keep the zip file, as you will be installing the script in Blender from the zip file.

* Find the .csv files: image_list.csv and path_list.csv will be in your unzip folder. Copy the image_list.csv to your images folder. Open it in either text editor or - preferably - in a spreadsheet program such as Excel or LibreOffice Calc (free).

   * The two columns represent the region (FieldName) the image is going to be assigned to, and the name (ImageName) of the image itself. You only ever edit the names of the images (the second column): the field-names are used by the script. If you are using a plain-text editor such as Notepad or gEdit, be sure to respect the double-quotes: they need to exist for every image and field name. If you are using a spreadsheet program to edit this csv, be sure to save it out as type .csv, and not as .xls or .ods.

* Copy the path_list.csv file to the folder containing your .blend file. If you are creating a new .blend file and don't know where it is going to end up, you can install Shaders-Addon anyway, but the script will not run until you've saved the file somewhere. You will need to copy the path_list.csv to that folder and editing it prior to running the script.

   * Open the path_list.csv file in either a text editor or - preferably - in a spreadsheet program such as Excel or Calc. The two columns represent the path key ('key': this first column has names used by the script which are not to be changed), and the fully-qualified path (value) to your images folder. Note: I tend to keep my textures files together in a sub-folder called "AllSkin" in my "AllTextures" folder in the main "Projects" folder that has all my Blender projects in it. This cuts down on redundant files everywhere and makes it easy for scripts (and Blender itself) to find stuff. The "path_list.csv" file assumes this sort of structure: of course, you can always just replace the existing path -- which is definitely not valid, since it is unlikely your name is Robyn and your computer is set up exactly like mine -- with a fully-qualified path to your image texture files. An example of a fully-qualified path for Linux or Mac would be:

__"/home/robyn/Documents/Blender/Projects/AllTextures/AllSkin/V4/"__

or, for Windows:

__"D:\MyRuntime\runtime\textures\VendorName\ImagesFolder\Character\"__


Note the closing foward slash [ / ] for Linux-Mac and back-slash [ \ ] for Windows: these are important and need to be appropriate for your system as well as at the end of the path statement. Also, if you are using a plain-text editor such as Notepad or gEdit, be sure to respect the double-quotes and commas: they need to exist for every image and field name. If you are using a spreadsheet program to edit this .csv file, be sure to save it out as type .csv, and not as .xls or .ods.


* Open Blender

* Install the Shaders-Addon script:

   * File -> User Preferences... -> Add-Ons tab

   * At the bottom of this dialogue, click on Install From File...

   * Navigate to where you downloaded the zip file and select the zip file (not the unzipped folder). Click 'Install from File...'

   * Browse your add-ons - click on 'User' under 'Categories' - and find the add-on. It is called 'Material: Shaders-Poser Figures'. Tick the box on the right to activate it.

* Find the panel with the script. Currently, this will show up in the Tools Panel section, at the bottom under '**Misc**'.

* If this is a new blender file with only the default cube, delete the cube and import your figure.

   * File -> Import -> Wavefront (obj) ... navigate to your figure, select the OBJ (not the MTL) and chose the following Import settings:

   * Untick Smooth Groups and untick Lines and everything in 'Split By'

   * Tick 'Keep Vert Order' and tick 'Poly Groups'

* Import OBJ

* Click on the figure in the scene, press [S] (for scale), and type 10

Until you save your .blend file -- giving it a name -- you will notice the 'Apply Shaders' button is greyed out (disabled). The other reason the button could be disabled is if your figure - the target for the shaders - has not been selected. So, save your .blend. Make sure the 'path_list.csv' file is with your saved .blend, and that it contains valid information about the location of your image files.

The next step is to give your object file (the figure you are trying to apply a shader to) a prefix, using one of these core figure names:

   1. V4
   
   2. Dawn
   
   3. Mariko

Any figure in the scene without the appropriate prefix will be ignored. You can rename the figure to an appropriate name in the box provided in the panel: select your figure, then enter the correct figure prefix in front of the name. For example, if you have a V4-based figure named Katie, rename your figure to 'V4Katie'. 

Also, ensure that the 'image_list.csv' file is in your images folder and contains the correct information about which image files correspond to which regions, also making sure there are no missing double-quote marks. Note: you will need the following .png files for the eyelashes:

For V4: __http://www.tightbytes.com/Blender/dev/V4Lashes05.png__

For Dawn: __http://www.tightbytes.com/Blender/dev/4_DawnLashes.png__


Simply download them to your images folder: they will not over-write anything. The 'Make Shaders' button should now be enabled. Click it to run the script.

# Caveat
This script has currently been tested in Linux (Mint Cinnamon 17.2) and Windows 7 Professional. Although I recently purchased a decent (used) Macbook Pro, I haven't had a chance to test this on the Mac yet. The script is still in fairly rudimentary form and does only minimal error-handling. For instance, if an image file is referred to in the image_list.csv file which doesn't exist in the folder, Blender will throw a rather inelegant error into the console. For now, please read the error message and fix your .csv.

Update 11-Oct-2016: up to version 0.3.9, which checks for and compensates for Blender sometimes tacking on a ":1" to a material name for the V4 series. I've solved some issues (material names) and created others. Back to the drawing board. :-/

Remember, this is open-source software: if you break it, you get to keep both pieces. :D  

Please do contact me if you run into any dramas at robinseahahn at gmail. This is very much a work in progress and will only improve with time. Cheers...
