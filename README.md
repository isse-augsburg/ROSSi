# Ros Simple (ROSSi)
This is an attempt to convert the middleware ROS into a graphical programming environment. For this purpose the common ROS development process was divided into the creation of nodes and the creation of launchfiles. In addition, an attempt was made to create a real-time variant of the rqt graph that adapts to changes in the running ROS environment.

Please note that this was created as part of a bachelor's thesis and still is only a prototype of the concepts from the thesis.

## Requirements
- This project was created during the lifetime of  [ros eloquent](https://docs.ros.org/en/eloquent/Installation.html) and has not been tested on other distributions.

## Setup
- after cloning this repo navigate inside the folder `ROSSi_workspace`
- source your eloquent workspace
- run `colcon build --symlink-install`
- source the setup file of your choice inside the created `install` folder
- run `rqt --force-discover` 
- the ROSSi plugin should appear in the plugins tab of rqt

## Usage
After selecting the plugin you will see the real-time graph of your running ros nodes. By pressing the `+` tab you can choose to open the launchfile editor or the node editor (which still has very limited functionality). You can browse for graphic items representing the runnables and launchfiles in all of your installed packages in the library window similar to simulinks library window. Drag and drop to add them to the current editor window. Export them via the export button inside the currently selected editors menu tab. Save or load a diagram for later editing via the save or load buttons inside the file menu tab.
