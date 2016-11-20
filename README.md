# Figure Shaders

**A bit of a preface**: I realise this README is a bit long... unfortunately. However, it does contain key information on how to set things up in order for the script to run correctly. **Please take the time to read this carefully.** I hope to eventually make the script more error-friendly and user-friendly, but at the moment it is what it is. *Note: This script was previously called "Shaders-Addon", a name which which wasn't particularly descriptive or even accurate, so if you're looking for that script, this is it (the newer version, that is).*

**Figure Shaders** is a script to give humanoid figures imported into Blender: skin, eyes and mouth shaders using an image set. These image sets are usually provided by the figure or character maker. The script runs in a panel [ T ] in the context of the the 3D Viewport window.
As of 07-Nov-2016, the most recent version is **0.43**. The file you will download is **FigureShaders-Master.zip**.

**Figure Shaders** requires Blender 2.77 or greater to run. Download the current version of Blender at:

http://www.blender.org/download/

**Figure Shaders** is comprised of four files:

* \__init__.py: contains the panel code and stuff to create the shaders

* figure_defs.py: dictionary object containing material slot names and material types (skin / eyes / etc)

These reside in your scripts/addons folder in its own folder called **make_shaders**: Blender will install the folder and files from the zip. Additionally, the zip contains these files:

* path_list.csv: **must be copied to the folder your currently open .blend file is in, and edited**.
 
* image_list.csv: **must be copied to the image folder for your figure, and edited**.

They need to be copied to their respective final folders **(and edited)** for the script to work. *Note: A copy of the csv files will be copied to the scripts folder, but those .csv files in that scripts folder will not be read by the script.*

This script has been designed and should work for the Victoria4, Dawn and Mariko figures, but has only been tested on the V4 figure so far.


# Instructions for Use
* If you haven't already done so, install Blender.

* Download **FigureShaders-Master.zip**: click the green [Clone or download] button and select Download ZIP. Extract the zip to a folder that you can find easily. Within this file is the **make_shaders.zip** file: this is what you will install in Blender.

* Find the .csv files: **image_list.csv** and **path_list.csv** will be in your unzip folder. Copy the image_list.csv to your images folder. You can edit this in Windows and Linux in either a plain text editor or in a spreadsheet program such as Excel or LibreOffice Calc (free), or on the Mac in LibreOffice. See notes below on how and why LibreOffice is recommended for the Mac. 

   * The two columns in image_list.csv represent the region (i.e., the Field Name) the image is going to be assigned to, and the name of the image file itself. You only ever edit the **names** of the images (the second column): the field names are used by the script and so must not be changed. If you are using a plain-text editor such as Notepad or gEdit, be sure to respect the double-quotes: they need to exist for every image and field name. If you are using a spreadsheet program to edit this csv, be sure to save it out as type .csv, and not as .xls or .ods.
   (An observation: editing .csv files on the Mac using TextEdit.app can/probably-will corrupt your .csv, messing in particular with the double-quotes. Microsoft Excel for the Mac appears to create the same mess, if not worse - no surprise there. However, LibreOffice will save your .csv correctly **if** you do a Save As... and tick the "Edit Filter Settings" tickbox. Save over your file when prompted (Replace), then in the next dialogue, make sure the Text Delimiter is a double-quote, and -- **very important** -- the Quote all text cells is ticked. Blender and the FigureShaders script will now read the file correctly.)

* Copy the path_list.csv file to the folder containing your .blend file. If you are creating a new .blend file and don't know where it is going to end up, you can install **Figure Shader** anyway, but the script will not run until you've saved the file somewhere. You will need to copy the path_list.csv to that folder and edit it prior to running the script.

   * Open the path_list.csv file. The two columns represent the path key ('key': this first column has names used by the script, so they must not be changed), and the fully-qualified path (value) to your images folder. Note: I tend to keep my textures files together in a sub-folder called "AllSkin" in my "AllTextures" folder in the main "Projects" folder that has all my Blender projects in it. This cuts down on redundant files everywhere and makes it easy for scripts (and Blender itself) to find stuff. The "path_list.csv" file assumes this sort of structure: of course, you can always just replace the existing images folder path in path_list.csv. The current entry is just an example and is almost definitely not a valid path to your files, since it is unlikely your name is Robyn and your computer is set up exactly like mine. Replace this with a fully-qualified path to your image texture files. An example of a fully-qualified path for Linux would be:

__"/home/robyn/Documents/Blender/Projects/AllTextures/AllSkin/V4/"__

or, for the Mac:

__"/Volumes/500GB/Blender/Projects/AllTextures/AllSkin/V4/"__

or, for Windows:

__"E:\MyRuntime\runtime\textures\VendorName\ImagesFolder\Character\"__


Note the closing foward slash [ / ] for Linux-Mac and back-slash [ \ ] for Windows: these are important and need to be appropriate for your system as well as at the end of the path statement. Also, if you are using a plain-text editor such as Notepad or gEdit, be sure to respect the double-quotes and commas: they need to exist for every image and field name. If you are using a spreadsheet program to edit this .csv file, be sure to save it out as type .csv, and not as .xls or .ods.


* Open Blender

* Install the FigureShader script:

   * File -> User Preferences... -> Add-Ons tab

   * At the bottom of this dialogue, click on Install From File...

   * Navigate to where you downloaded the zip file and extracted it. It should be in its own folder, likely called FigureShaders-master or something like that. *Note: be sure to select the **make_shaders.zip** file and not the FigureShaders-master.zip file.* Click 'Install from File...'
   
   * The add-on **Material: shaders for imported figures** should be visible in the add-ons tab. If not, browse your add-ons - click on 'User' under 'Categories' - and find the add-on. It is called **'Material: shaders for imported figures'**.
   
   * Tick the box on the right to activate it. **(If this does not appear, check in the scripts/addons/ folder for the existence of a make_shaders folder, and that all these files are within that folder).**

* Find the panel with the script. Currently, this will show up in the Tools Panel section - the one on the left, toggled with [T] - usually the bottom tab labeled '**FigureShader**'.

* If this is a new blender file with only the default cube, delete the cube and import your figure.

* File -> Import -> Wavefront (obj) ... navigate to your figure, select the OBJ (not the MTL) and chose the following Import settings:

* Untick Smooth Groups and untick Lines and everything in 'Split By'

* Tick 'Keep Vert Order' and tick 'Poly Groups'

* Import OBJ

* Click on the figure in the scene, press [S] (for scale), and type 10

Until you save your .blend file -- giving it a name -- you will notice the 'Apply Shaders' button is greyed out (disabled). The button will also be disabled if your figure - the target for the shaders - is not selected. Save your .blend. Make sure the 'path_list.csv' file is with your saved .blend, and that it contains valid path information about the location of your image files.

The next step is to give your object file (the figure you are trying to apply a shader to) a prefix, using one of these core figure names:

   1. V4
   
   2. Dawn
   
   3. Mariko

Any figure in the scene without the appropriate prefix will be ignored. You can rename the figure to an appropriate name in the box provided in the panel: select your figure, then enter the correct figure prefix in front of the name. For example, if you have a V4-based figure named **Katie**, rename your figure to '**V4Katie**'. The script will not apply shaders to a figure unless the name is prefaced by figure type.

Also, ensure that the 'image_list.csv' file is in your images folder and contains the correct information about which image files correspond to which regions, also making sure there are no missing double-quote marks. Note: you will need the following .png files for the eyelashes:

For V4: __http://www.tightbytes.com/Blender/dev/V4Lashes05.png__

For Dawn: __http://www.tightbytes.com/Blender/dev/4_DawnLashes.png__


Simply download them to your images folder.

# Caveat
-- This script has currently been tested in Linux (Mint Cinnamon 18), on a Macbook Pro running MacOS Sierra and on Windows 7 Professional. The script loads and runs successfully on all these OSes.
-- Some FigureShader messages are displayed on the Info panel, between the Render Engine dropdown and the Blender Logo now. **Most error messages will still show up on the System Console or in a popup, however.** I'm hoping these will become less with time as I do better error-handling.
I tend to run Blender from a Terminal window in Linux (Blenderites know this as the console), so I check there for error messages. In Windows, you can toggle the System Console under: (Menu) Window > Toggle System Console. Mac users, please refer to this page:
__http://blender.stackexchange.com/questions/6173/where-does-console-output-go__

Update 10-Nov-2016: version 0.4.3. Messages successfully sent to the Info panel in the Linux version. Need more extensive testing, however, on the Mac and in Windows. Changed the file structure in github to match what's required in Blender, so files are now in the make_shaders folder, which is where they need to be once installed. Removed previous versions as zips since they were buggy anyway.

Update 28-Oct-2016: version 0.4.2. Checks path statement in path_list.csv that the path is correct for the folder holding the image files. Checks for the existence of the image_list.csv file. Checks that all entries in image_list.csv are correct (as in: correspond to a file in that folder).

Update 25-Oct-2016: version 0.4.1. Checks for and compensates for Blender sometimes tacking on a :1 (or a .001, or even a :1.002) to a material name for the V4 series. I've solved some of those issues (material names), hopefully without creating others. Please do let me know if you run into dramas. Also checks for the presence of the .csv files. Invalid edits are as yet not trapped.

-- Remember, this is open-source software: if you break it, you get to keep both pieces. :D  

-- Please contact me if you run into any dramas at robinseahahn at gmail dot com, or (preferably) raise an issue under __https://github.com/robinboncoeur/FigureShaders/issues__.
