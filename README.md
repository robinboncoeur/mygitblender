<img style="width: 80px;" src="http://www.tightbytes.com/Blender/FigShaders01.png" alt="Skin shaders on V4"/>

# Figure Shaders

**tl;dr:**

To install the script in Blender, please click on the green Clone or Download button above. The download file (**Figureshaders-master.zip**) will contain a zip file: **make_shaders.zip**. You will need to unzip the **Figureshaders-master.zip** file to a folder, which will contain that **make_shaders.zip** file. Select this **make_shaders.zip** zip file in the Preference page in Blender to install this script:
File -> User Preferences... -> then click on "Install From File..." at the bottom of the dialogue box.


# Description

**Figure Shaders** is a script to give humanoid figures imported into Blender: skin, eyes and mouth shaders using an image set. These image sets are usually provided by the figure or character maker. The script runs in a panel [ T ] in the context of the the 3D Viewport window.
Currently - as of 19-Feb-2018 - the most recent version is 0.5.5. All should work as advertised.

**Figure Shaders** requires Blender 2.78 or newer to work properly, largely because it takes advantage of a new shader node called PrincipledShader. Download the current version of Blender at:

https://www.blender.org/download/

The current version of this script is comprised of five files:

* \__init__.py: contains the panel code and stuff to create the shaders

* figure_defs.py: dictionary object containing material slot names and material types (skin / eyes / etc)

* make_shader.py: creates the node sets to populate the material zones

These three files will reside in your scripts/addons folder -- after installation -- in a folder called **make_shaders**: Blender will install the folder and files from the make_shader.zip file, as noted above. Additionally, the zip contains these files:

* path_list.csv: **must be copied to the folder your currently open .blend file is in, and edited**.

* image_list.csv: **must be copied to the image folder for your figure, and edited**.

They need to be copied to their respective final folders **(and edited)** for the script to work. *Note: A copy of the csv files will end up in that /scripts/addons/make_shaders folder, but neither .csv file in that location will be read by the script.*

This script has been designed and should work for the Antonia, Victoria4, Dawn and Mariko figures. The only figure that has not undergone extensive testing has been Mariko. If you want other figures adding, please drop me a line (under **Issues**, above) and if I have that figure I'll try to add it to the **figure_defs.py** file... or: feel free to edit this file. This software is open-source... you're free to edit, chop and change all you want, as long as you observe the terms of GPL3. Be keen to see if you can get it working on another figure!


# Instructions for Use
* If you haven't already done so, install Blender.

* Download the **Figureshaders-master.zip** file and install the script in Blender using the above instructions.

* Find the .csv files: **image_list.csv** and **path_list.csv** will be in your unzip folder. Copy the image_list.csv to each skin-texture image folder. You will need to edit this file: in Windows and Linux use either a plain text editor or in a spreadsheet program such as Excel or LibreOffice Calc (free), or on the Mac, in LibreOffice. See notes below on how and why LibreOffice is recommended for the Mac.

The **image_list.csv** file should look something like this when you've finished editing (using Antonia textures as an example):

	"clrALimb","ToniPArms.jpg"  
	"clrLLimb","ToniPLegs.jpg"  
	"bmpALimb","ToniPArmsBUMP.jpg"  
	"bmpLLimb","ToniPLegsBUMP.jpg"  
	"spcALimb","ToniPArmsSPEC.jpg"  
	"spclLimb","ToniPLegsSPEC.jpg"  
	"clr_Body","ToniPBody.jpg"  
	"bmp_Body","ToniPBodyBUMP.jpg"  
	"spc_Body","ToniPBodySPEC.jpg"  
	"clr_Face","ToniPHead.jpg"  
	"bmp_Face","ToniPHeadBUMP.jpg"  
	"spc_Face","ToniPHeadSPEC.jpg"  
	"clr_Eyes","ToniPEyesAmber.jpg"  
	"clrMouth","ToniPMouthparts.jpg"  
	"bmpMouth","ToniPMouthpartsBUMP.jpg"  
	"clr_Lash","ToniPLashFakeTRANS.png"  
	

   * The two columns represent the region (i.e., the Field Name) the image is going to be assigned to, and the name of the image file itself. You only ever edit the names of the images (the second column): the field names are used by the script and so must not be changed. If you are using a plain-text editor such as Notepad or gEdit, be sure to respect the double-quotes (""): they need to exist for every image and field name. If you are using a spreadsheet program to edit this csv, be sure to save it out as type .csv, and not as .xls or .ods. For Mac and Linux, capitals count: an 'a' is not the same as an 'A'. Windows isn't as fussy.
   (An observation: editing .csv files on the Mac using TextEdit.app can/probably-will corrupt your .csv, as the **TextEdit.app** messes with the double-quotes. Microsoft Excel for the Mac appears to create the same mess, if not worse - no surprise there. However, LibreOffice respects double-quotes and will save your .csv correctly **if** you do a Save As... and tick the "Edit Filter Settings" tickbox. Save over your file when prompted (Replace), then in the next dialogue, make sure the Text Delimiter is a double-quote, and -- **very important** -- the 'Quote all text cells' tickbox is selected (ticked). Blender and the FigureShaders script will now read the file correctly.)

* Copy the **path_list.csv** file to the folder containing the .blend file that will invoke the script. If you are creating a new .blend file and don't know where it is going to end up, you can install **Figure Shader** anyway, but the script will not run until:
	1. you've saved the file to some location with a name and
	2. you've saved (and edited) a path_list.csv file to that location
Be sure to edit this file prior to running the script. An edited file will look something like this:

		"img_pathP", "/home/robyn/Documents/Blender/Projects/AllTextures/AllSkin/Antonia/"  
		"img_pathN", "E:\Blender\Projects\AllTextures\AllSkin\Antonia\"  
		"csv_pathP", "/home/robyn/Documents/Blender/Projects/AllTextures/AllSkin/Antonia/"  
		"csv_pathN", "E:\Blender\Projects\AllTextures\AllSkin\Antonia\"  
		"csv_name", "image_list.csv"  

* To edit the **path_list.csv** file, open it in a pure-text editor or spreadsheet programme, as explained above. The two columns represent the path key: this first column has names used by the script, so they must not be changed, and the fully-qualified path (value) to your images folder. Note: I tend to keep my textures files together in a sub-folder called "AllSkin" in my "AllTextures" folder in the main "Projects" folder that has all my Blender projects in it. This cuts down on redundant files everywhere and makes it easy for scripts (and Blender itself) to find stuff. The **path_list.csv** file assumes this sort of structure: of course, you can always just replace the existing images folder path to the path location of your images. The current entry is just an example and is almost definitely not a valid path to your files, since it is unlikely your name is Robyn, nor would your computer be set up exactly like mine. Thus, you will need to replace the existing path statement with a fully-qualified path designating your image texture files' location. As you can see from the example, an example of a fully-qualified path for Linux would be:

__"/home/robyn/Documents/Blender/Projects/AllTextures/AllSkin/Antonia/"__

or, for the Mac:

__"/Volumes/500GB/Blender/Projects/AllTextures/AllSkin/Antonia/"__

or, for Windows:

__"E:\MyRuntime\runtime\textures\VendorName\ImagesFolder\Character\"__


Note the closing forward slash [ / ] for Linux-Mac and back-slash [ \ ] for Windows: these are important and need to be appropriate for your system **as well as at the end of the path statement**. Again, if you are using a plain-text editor such as Notepad or gEdit, be sure to respect the double-quotes and commas: they need to exist for each value.


# Reviewing Script Installation Instructions

* Open Blender

* Install the FigureShader script:

   * File -> User Preferences... -> Add-Ons tab

   * At the bottom of this dialogue, click on Install From File...

   * Navigate to where you downloaded the zip file and select the **make_shaders.zip file**, within the unzipped folder FigureShaders folder. Click 'Install from File...'

   * Browse your add-ons - click on 'User' under 'Categories' - and find the add-on. It is called 'Material: Shaders for Imported Figures'. Tick the box on the right to activate it. **(If this does not appear, check in the scripts/addons/ folder for the existence of a make_shaders folder, and that all these files are within that folder).**

* Find the panel with the script. Currently, this will show up in the Tools Panel section, labeled '**FigureShader**'.

* If this is a new blender file with only the default cube, delete the cube and import your figure. To do so, I suggest the following approach:

   * File -> Import -> Wavefront (obj) ... navigate to your figure, select the OBJ (not the MTL) and chose the following Import settings:

   * Untick Smooth Groups and untick Lines and everything in 'Split By'

   * Tick 'Keep Vert Order' and tick 'Poly Groups'
(Note: *It's a good idea to save these settings so you merely have to select from the dropdown: I save the settings as 'Poser')*

* Import OBJ

* Click on the figure in the scene, press [S] (for scale), and type 10 (Poser's scale is woefully tiny!)

* Press T to open the panel, then find the FigureShader section. You should see two dropdowns and an 'Apply Shaders' button:

<img src="http://www.tightbytes.com/Blender/FigShTute00.png" alt="FigureShader"/>

Select the name of your target object file (the figure you are trying to apply a shader to) from the first dropdown under "Select the figure for SkinShaders:"

<img src="http://www.tightbytes.com/Blender/FigShTute01.png" alt="Select figure to shade"/>

... in this dropdown you will see a list of all objects in your Blender scene. Select the figure you wish to apply skin and other materials to. Currently, FigureShaders supports these core figures:

   1. Victoria4
   2. Dawn
   3. Mariko
   4. Antonia

* To identify which figure that object is based on, select the figure type name from the second dropdown.

<img src="http://www.tightbytes.com/Blender/FigShTute02.png" alt="Select base figure"/>

* Finally, click on Apply Shaders.
Remember: *until you save your .blend file -- giving it a name -- the 'Apply Shaders' button will remain disabled*.


# Behaviour

After some basic error checking, the script will paint a fairly basic shader on material zones of your figure, including eyelashes and teeth. If you have material zones in the figure that aren't in the list for that figure, those zones are ignored. 

Selecting the wrong base figure will result in no shaders being painted on your figure. Note: *previous versions of this script required that the figure be named that of its origins, such as 'V4' or 'Dawn': that is no longer required, the object can be named anything. If no shaders show up on your figure, double-check that you have the right figure type selected.*

The script will detect some basic issues and display them in an "Error Detected" dialogue:

<img src="http://www.tightbytes.com/Blender/FigShTute03a.png" alt="Error message"/>

This dialogue is a bit temperamental at this point, using somewhat immature API stuff, so expect that clicking the 'OK' button will not close the dialogue: moving the cursor away from the dialogue afterwards will.

The script currently traps for:

	1. missing path_list.csv - meant to be in the .blend file's folder, and edited
	2. missing image_list.csv - meant to be in the images folder, and edited
	3. missing or misspelt image file, referenced in the image_list.csv file: file name is identified
	4. missing double-quote ( " ) in either the path_list.csv or image_list.csv file

More issues could be managed this way as users identify them.


# Caveat
This script has currently been tested in Linux (Mint Cinnamon 18), on a Macbook Pro running MacOS High Sierra and on Windows 7 Professional. The script loads and runs successfully on all these OSes.

FigureShader will display known, trapped error messages in a dialogue instead of the Info panel and on the console.   **However, most untrapped Python error messages will still show up on the System Console and probably in a temporary popup, and will be Python-esque and seemingly unfriendly.**  I have endeavoured to trap for most known errors: however, some will probably still slip through. For that reason, if you expect something to happen and doesn't, the system console is your friend. I tend to run Blender from a Terminal window in Linux (Blenderites know this as the console), so I check there for error messages. In Windows, you can toggle the System Console under: (Menu) Window > Toggle System Console. Mac users, please refer to this page:

__http://blender.stackexchange.com/questions/6173/where-does-console-output-go__

Remember, this is open-source software: if you break it, you get to keep both pieces. 😁 

Please contact me if you run into any dramas at robinseahahn at gmail dot com, or (preferably) raise an issue under __https://github.com/robinboncoeur/FigureShaders/issues__.


# [ Update Log ]
Update 19-Mar-2018: version 0.5.5. FigureShader traps for missing double-quotes in csv files.

Update 18-Mar-2018: version 0.5.4. 
Added figure and figure-type selection dropdowns. No longer required that the object to be painted (shadered) be named after the figure the object is based on.  
Added: FigureShader now displays three trapped error messages (missing path_list.csv, missing image_list.csv or missing image file referenced in image_list.csv, which file is identified by name) in a dialogue instead of the Info panel and on the console.  

Update 08-Jan-2018: version 0.5.0. Takes advantage of the Principled Shader for skin. Restructured a lot of the code, basing it on what I learned from reading JSulpis' fine example: __https://github.com/jsulpis/blender-addons__ . 

Update 07-Nov-2016: version 0.4.3. Messages successfully sent to the Info panel in the Linux version. Need more extensive testing, however, on the Mac and in Windows.

Update 28-Oct-2016: version 0.4.2. Checks path statement in path_list.csv that the path is correct for the folder holding the image files. Checks for the existence of the image_list.csv file. Checks that all entries in image_list.csv are correct (as in: correspond to a file in that folder).

Update 25-Oct-2016: version 0.4.1. Checks for and compensates for Blender sometimes tacking on a :1 (or a .001, or even a :1.002) to a material name for the V4 series. I've solved some of those issues (material names), hopefully without creating others. Please do let me know if you run into dramas. Also checks for the presence of the .csv files. Invalid edits are as yet not trapped.


# Other Cool Stuff

Blender makes use of the alpha channel (transparency) of .png files. This is a far superior solution to lashes and hair to the one Poser uses, where black is interpreted as alpha. For this reason, you will need to convert your lashes jpgs to .png. This is trivial to accomplish in GIMP, a free download -- apparently not so easy to accomplish in PS. Anyway, a quick howto:

   1. If you haven't done so, install GIMP

   2. Open the lashes .jpg in GIMP

   3. Under Image -> Mode, confirm that the image is set to RGB, not greyscale

   4. Under Colors, select Colour to Alpha... and click OK  

   5. Under File, select Export As...  and click Export

   6. If you wish, you can save the XCF file or discard it.


