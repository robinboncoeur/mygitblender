<img style="width: 80px;" src="http://www.tightbytes.com/images/pubimages/blender/SeaChange.jpg" alt="Sea Change"/>

# Blender-focused Projects

2022-03-29: Blender is currently at version 3.1. My Figure Shaders script was written for v2.79. It has not been maintained. In all likelihood, it is no longer relevant, if it ever was.

**Figure Shaders**

Quick tip: to install the script in Blender, please click on the green Clone or Download button above. The download file (**Figureshaders-master.zip**) will contain a zip file: **make_shaders.zip**. You will need to unzip the **Figureshaders-master.zip** file to a folder, which will contain that **make_shaders.zip** file. Select this **make_shaders.zip** zip file in the Preference page in Blender to install this script:
File -> User Preferences... -> then click on "Install From File..." at the bottom of the dialogue box.

Please see the wiki for more detailed instructions on installation and usage:

https://github.com/robinboncoeur/FigureShaders/wiki




# [ Update Log ]
Update 11-Nov-2018: I am moving wiki pages to a more manageable approach:

https://robinboncoeur.github.io/FigureShaders/index.html

These web pages are easier to maintain, as the structure is done in Sphinx. Also, the whole workflow is being reviewed as it is unneccesarily convoluted and awkward, not to mention error-prone.

Update 11-May-2018: version 0.6.0 Current testing shows script is fully stable in Linux, Mac and Windows. Removed beta status.

Update 05-May-2018: version 0.5.92 Removed image_list.csv and parm_list.csv, as the app now writes them, and so less errors will result as opposed to manually-edited files. Tested in Linux and Mac, currently testing in Windows. Removed debug code and generally cleaning up. Considering changing how make_shader.py will be called (no real need for parameters anymore). 

Update 30-Apr-2018: version 0.5.91 Relative path (invalid path) trapped, test and working in Linux. To test on the Mac and Windows Much debug code commented out but not removed. Dialogue box still does not respond to clicking [OK]. Very much still in Alpha.

Update 29-Apr-2018: version 0.5.9 Relatively stable version, full debugging / testing in progress. Debug code commented out but not removed. Please report bugs to the Issues page: https://github.com/robinboncoeur/FigureShaders/issues.

Update 26-Apr-2018: version 0.5.8 Reads and writes (creates if it doesn't exist) CSV files. Edit image file association to regions to shader. Initial debugging / testing started.

Update 25-Apr-2018: version 0.5.7 -> branch parmListRead. Able to navigate to image folder. Loads -- reads -- settings from parm_list.csv (which replaces path_list.csv). Allows management of SSSValue, SSSRadiate, SpecAmt (erroneously labeled Spec Tint), Spec roughness, Sheen Value and IOR value. Very much a WIP at this point: main next goal is to be able to write settings to csv.

Update 01-Apr-2018: version 0.5.6 Included trap for old path_list.csv files, which contain old format (and invalid information). *Proposed solution: this and other .csv situations to be managed by the software writing to the file as opposed to having the user manually editing the file. Currently under development.*

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

