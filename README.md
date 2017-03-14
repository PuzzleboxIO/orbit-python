orbit-python
==================


Puzzlebox Orbit


Copyright (2012-2017)

by Puzzlebox Productions, LLC

https://puzzlebox.io


License: GNU Affero General Public License v3.0
https://www.gnu.org/licenses/agpl-3.0.html


============

Available for Purchase:

https://puzzlebox.io/shop


============

Download Releases:

https://puzzlebox.io/orbit/development/downloads


============

Required Python Modules:
- pyside
- simplejson
- serial
- matplotlib


============

Instructions:

- Requires downloading and configuration of Puzzlebox Synapse and Puzzlebox Jigsaw:

https://github.com/PuzzleboxIO/synapse-python

https://github.com/PuzzleboxIO/jigsaw-python

- Create a symlink inside root directory to Synapse and Jigsaw:

Example: ln -s ../../synapse-python/Puzzlebox/Synapse Synapse

Example: ln -s ../../jigsaw-python/Puzzlebox/Jigsaw Jigsaw


============

Examples:

macOS (via MacPorts):

$ sudo port install py27-pyside py27-simplejson py27-serial py27-matplotlib

$ git clone https://github.com/PuzzleboxIO/synapse-python

$ git clone https://github.com/PuzzleboxIO/jigsaw-python

$ git clone https://github.com/PuzzleboxIO/Orbit-python

$ cd jigsaw-python/Puzzlebox

$ ln -s ../../synapse-python/Puzzlebox/Synapse Synapse

$ ln -s ../../jigsaw-python/Puzzlebox/Jigsaw Jigsaw

$ cd ..

$ python2.7 orbit-gui.py
