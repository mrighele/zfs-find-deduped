# zfs-find-deduped
Get a list of deduped files on a ZFS filesystem

This tool will crawl a ZFS filesystem and print all the files that have been
in part of all deduped.

The script is written in Python 3 but doesn't need any extra library. It requires
the zdb tool to be available (which should be the case if you're using ZFS)

To use it just call it with the name of the filesystem to investigate
```
python3 zfs_find_deduped.py pool/my/filesystem
```
The output is something like the following:

```
Scanning filesystem pool/my/filesystem to gather file and block list...
Scanning pool pool to gather dedup block list...
List of files with dedup indexes:
0 1 /file1.txt
1 0 /file2.txt
```

Every file in the output will have two numbers before it. The first is the number of blocks 
that appear in DDT (Deduplication Table) that are unique to that file. The second is the number
of blocks that are being shared with other files.

In particular files with a 0 in the second position don't share any block with other files and are
taking space in the DDT for no gain.

### Command line arguments

Beside the pool to test, the tool accept the following optional argument

* --debug will cause the program to print some debugging information while running


### Notes

I expect the tool to use a fair amount of memory. In particular the map to count the occurrences of the
blocks is kept in memory. I would be happy to receive some feedback on this.  

Since the tool runs the _zdb_ command which need superuser rights you will probably need to run it
either as root or with sudo.

