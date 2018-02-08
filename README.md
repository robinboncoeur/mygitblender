# Figure Shaders

**Please Note:**
In order to install the files easily into Blender, please download the contents of the make_shaders folder in the list above (the one under Archive). To do so, click on the make_shaders link, then click on the green Clone or Download button.

**Figure Shaders** is a script to give humanoid figures imported into Blender: skin, eyes and mouth shaders using an image set. These image sets are usually provided by the figure or character maker. The script runs in a panel [ T ] in the context of the the 3D Viewport window.
Currently - as of 08-Feb-2018 - the most recent version is **FgrShaders50.zip**.

**Figure Shaders** requires Blender 2.779 or greater to work properly, largely because it takes advantage of a new shader called PrincipledShader. Download the current version of Blender at:

https://www.blender.org/download/

The current version of this script is 0.5.0, which is comprised of five files:

* \__init__.py: contains the panel code and stuff to create the shaders

* figure_defs.py: dictionary object containing material slot names and material types (skin / eyes / etc)

* make_shader.py: creates the node sets to populate the material zones with

These reside in your scripts/addons folder in its own folder called **make_shaders**: Blender will install the folder and files from the zip. Additionally, the zip contains these files:

* path_list.csv: **must be copied to the folder your currently open .blend file is in, and edited**.

* image_list.csv: **must be copied to the image folder for your figure, and edited**.

They need to be copied to their respective final folders **(and edited)** for the script to work. *Note: A copy of the csv files will be copied to the scripts folder, but will not be read by the script.*

This script has been designed and should work for the Antonia, Victoria4, Dawn and Mariko figures, but has been extensively tested on the V4 and Antonia figures so far.


# Instructions for Use
* If you haven't already done so, install Blender.

* Download the current zip file: if you click the green [Clone or download] button and select Download ZIP, you will get all versions. You might want to just download the current version, however: click the FgrShadersxx.zip file, then on the right side (next to the History button) click Download. Extract the zip to a folder but keep the zip file, as you will be installing the script in Blender from that zip file.

* Find the .csv files: **image_list.csv** and **path_list.csv** will be in your unzip folder. Copy the image_list.csv to your images folder. You can edit this in Windows and Linux in either a plain text editor or in a spreadsheet program such as Excel or LibreOffice Calc (free), or on the Mac in LibreOffice. See notes below on how and why LibreOffice is recommended for the Mac.

   * The two columns represent the region (i.e., the Field Name) the image is going to be assigned to, and the name of the image file itself. You only ever edit the names of the images (the second column): the field names are used by the script and so must not be changed. If you are using a plain-text editor such as Notepad or gEdit, be sure to respect the double-quotes: they need to exist for every image and field name. If you are using a spreadsheet program to edit this csv, be sure to save it out as type .csv, and not as .xls or .ods.
   (An observation: editing .csv files on the Mac using TextEdit.app can/probably-will corrupt your .csv, messing in particular with the double-quotes. Microsoft Excel for the Mac appears to create the same mess, if not worse - no surprise there. However, LibreOffice will save your .csv correctly **if** you do a Save As... and tick the "Edit Filter Settings" tickbox. Save over your file when prompted (Replace), then in the next dialogue, make sure the Text Delimiter is a double-quote, and -- **very important** -- the Quote all text cells is ticked. Blender and the FigureShaders script will now read the file correctly.)

* Copy the path_list.csv file to the folder containing your .blend file. If you are creating a new .blend file and don't know where it is going to end up, you can install **Figure Shader** anyway, but the script will not run until you've saved the file somewhere. You will need to copy the path_list.csv to that folder and edit it prior to running the script.

   * Open the path_list.csv file. The two columns represent the path key ('key': this first column has names used by the script, so they must not be changed), and the fully-qualified path (value) to your images folder. Note: I tend to keep my textures files together in a sub-folder called "AllSkin" in my "AllTextures" folder in the main "Projects" folder that has all my Blender projects in it. This cuts down on redundant files everywhere and makes it easy for scripts (and Blender itself) to find stuff. The "path_list.csv" file assumes this sort of structure: of course, you can always just replace the existing images folder path in path_list.csv. The current entry is just an example and is almost definitely not a valid path to your files, since it is unlikely your name is Robyn and your computer is set up exactly like mine. Replace this with a fully-qualified path to your image texture files. An example of a fully-qualified path for Linux would be:

__"/home/robyn/Documents/Blender/Projects/AllTextures/AllSkin/V4/"__

or, for the Mac:

__"/Volumes/500GB/Blender/Projects/AllTextures/AllSkin/V4/"__

or, for Windows:

__"E:\MyRuntime\runtime\textures\VendorName\ImagesFolder\Character\"__


Note the closing forward slash [ / ] for Linux-Mac and back-slash [ \ ] for Windows: these are important and need to be appropriate for your system as well as at the end of the path statement. Also, if you are using a plain-text editor such as Notepad or gEdit, be sure to respect the double-quotes and commas: they need to exist for every image and field name. If you are using a spreadsheet program to edit this .csv file, be sure to save it out as type .csv, and not as .xls or .ods.


* Open Blender

* Install the FigureShader script:

   * File -> User Preferences... -> Add-Ons tab

   * At the bottom of this dialogue, click on Install From File...

   * Navigate to where you downloaded the zip file and select the **zip file** (not the unzipped folder). Click 'Install from File...'

   * Browse your add-ons - click on 'User' under 'Categories' - and find the add-on. It is called 'Material: Shaders-Poser Figures'. Tick the box on the right to activate it. **(If this does not appear, check in the scripts/addons/ folder for the existence of a make_shaders folder, and that all these files are within that folder).**

* Find the panel with the script. Currently, this will show up in the Tools Panel section, at the bottom labeled '**FigureShader**'.

* If this is a new blender file with only the default cube, delete the cube and import your figure.

   * File -> Import -> Wavefront (obj) ... navigate to your figure, select the OBJ (not the MTL) and chose the following Import settings:

   * Untick Smooth Groups and untick Lines and everything in 'Split By'

   * Tick 'Keep Vert Order' and tick 'Poly Groups'

* Import OBJ

* Click on the figure in the scene, press [S] (for scale), and type 10

Until you save your .blend file -- giving it a name -- you will notice the 'Apply Shaders' button is greyed out (disabled). The button will also be disabled if your figure - the target for the shaders - is not selected. Save your .blend. Make sure the 'path_list.csv' file is with your saved .blend, and that it contains valid path information about the location of your image files.

The next step is to change the name of your target object file (the figure you are trying to apply a shader to) to one of these core figure names:

   1. V4

   2. Dawn

   3. Mariko

   4. Antonia

Any figure in the scene without the appropriate prefix will be ignored. You can rename the figure to an appropriate name in the box provided in the panel: select your figure, then enter the correct figure prefix in front of the name. For example, if you have a V4-based figure named **Katie**, rename your figure to '**V4**'. The script will not apply shaders to a figure unless this is done.

Also, ensure that the 'image_list.csv' file is in your images folder and contains the correct information about which image files correspond to which regions, also making sure there are no missing double-quote marks.

Blender makes use of the alpha channel (transparency) of .png files. This is a far superior solution to lashes and hair to the one Poser uses, where black is interpreted as alpha. For this reason, you will need to convert your lashes jpgs to .png. This is trivial to accomplish in GIMP, a free download -- apparently not so easy to accomplish in PS. Anyway, a quick howto:

   1. If you haven't done so, install GIMP

   2. Open the lashes .jpg in GIMP

   3. Under Image -> Mode, confirm that the image is set to RGB, not greyscale

   4. Under Colors, select Colour to Alpha... and click OK  

   5. Under File, select Export As...  and click Export

   6. If you wish, you can save the XCF file or discard it.


# Caveat
-- This script has currently been tested in Linux (Mint Cinnamon 18), on a Macbook Pro running MacOS Sierra and on Windows 7 Professional. The script loads and runs successfully on all these OSes.
-- Some FigureShader messages are displayed on the Info panel, between the Render Engine dropdown and the Blender Logo now. **However, most error messages will still show up on the System Console or in a popup.**
I tend to run Blender from a Terminal window in Linux (Blenderites know this as the console), so I check there for error messages. In Windows, you can toggle the System Console under: (Menu) Window > Toggle System Console. Mac users, please refer to this page:
__http://blender.stackexchange.com/questions/6173/where-does-console-output-go__

Update 08-Jan-2018: branched to PrinceShader to take advantage of the Principled Shader. Restructured a lot of the code, basing it on what I learned from reading JScuptis' fine example.

Update 07-Nov-2016: version 0.4.3. Messages successfully sent to the Info panel in the Linux version. Need more extensive testing, however, on the Mac and in Windows.

Update 28-Oct-2016: version 0.4.2. Checks path statement in path_list.csv that the path is correct for the folder holding the image files. Checks for the existence of the image_list.csv file. Checks that all entries in image_list.csv are correct (as in: correspond to a file in that folder).

Update 25-Oct-2016: version 0.4.1. Checks for and compensates for Blender sometimes tacking on a :1 (or a .001, or even a :1.002) to a material name for the V4 series. I've solved some of those issues (material names), hopefully without creating others. Please do let me know if you run into dramas. Also checks for the presence of the .csv files. Invalid edits are as yet not trapped.

-- Remember, this is open-source software: if you break it, you get to keep both pieces. :D  

-- Please contact me if you run into any dramas at robinseahahn at gmail dot com, or (preferably) raise an issue under __https://github.com/robinboncoeur/FigureShaders/issues__.
