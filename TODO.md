# Todo

- general refactoring
- sys.exit(1) for errors -- how to handle? Not good to simply sys.exit() from any random part of code (can leave things in a mess)
- consider context managers for handling compression, so as to keep operations atomic and/or rollback-able
- add a recursive option on the command-line for use with -d
- make -f accept a list of files
- make the current verbose be "normal", and make -verbose print the commandline app prints as well
- find a way to specify the version once for everywhere
- notification area drag/drop widget -> probably need gtk for gnome
- figure out how to make mac and win versions (someone else :) <- via gui2exe
- animate compressing.gif
- allow selection/deletion of rows from table (and subsequently the imagelist)
- punypng api? http://www.gracepointafterfive.com/punypng/api
- imagemagick/graphicsmagick?
- always on top option
- intelligently recompress, i.e. go through the list of files, recompress each until no more gains are seen (and a sensible number-of-tries limit isn't exceeded), and flag that file as fully-optimised. Repeat for each file in the list, until all are done. Saves pointlessly trying to optimise files. Consider the case of a directory of 100 files, already optimised once. Recompressing maximally compresses 90. Recompressing again would currently try to recompress all 100, when only 10 would be worthy of trying to compress further
