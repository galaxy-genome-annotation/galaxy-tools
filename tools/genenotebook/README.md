# GeneNoteBook Galaxy tool

This tool will generate a MongoDB database ready to be used by a GeneNoteBook server.

To achieve this, this tools starts a local MongoDB server, listening only on a UNIX socket within the job directory.

It also starts a GeneNoteBook server within the job evironment, using a port >7000, that is detected to be free at the time of running the job.
