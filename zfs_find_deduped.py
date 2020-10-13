#!/usr/bin/python3

import subprocess
import sys

def extract_pool(filesystem):
    return filesystem.split('/')[0]


INDIRECT_BLOCKS=0
OTHER=1

DEBUG=False
if "--debug" in sys.argv:
    DEBUG=True
    sys.argv.remove("--debug")

filesystem = sys.argv[1]
pool = extract_pool(filesystem)


def debug(*args):
    if DEBUG:
        print(*args)


def find_file_indirect_blocks(filesystem):
    process = subprocess.run(["/sbin/zdb", "-ddddd", filesystem], stdout=subprocess.PIPE);
    output=process.stdout

    blocks = {}
    current_path = None
    status=OTHER
    for line in output.split(b'\n'):
        tokens = line.strip().split()
        if len(tokens) > 0 and tokens[0] == b"path":
            current_path = line[ line.index(b"path") + 4:].strip()
            blocks[current_path] = []
            debug("Processing file", current_path)
        elif len(tokens) == 2 and tokens[0] ==b"Indirect":
            debug("Found indirect blocks")
            status = INDIRECT_BLOCKS
        elif len(tokens) == 0:
            status = OTHER
        elif status == INDIRECT_BLOCKS and current_path is not None:
            block_name = tokens[2].decode("utf-8")
            blocks[current_path].append(block_name)
            debug("Found block", block_name)
    return blocks

def find_dedup_blocks(pool):
    process = subprocess.run(["/sbin/zdb", "-DDDDD", pool], stdout=subprocess.PIPE, universal_newlines=True);
    output=process.stdout
    blocks = {}
    
    for line in output.split('\n'):
        tokens = line.strip().split()
        if len(tokens) > 0 and tokens[0] == "index":
            refcount = int(tokens[3])
            block = tokens[5][8:-1]
            blocks[block] = refcount
    return blocks

print("Scanning filesystem", filesystem,"to gather file and block list...")
file_blocks = find_file_indirect_blocks(filesystem)

print("Scanning pool", pool,"to gather dedup block list...")
dedups = find_dedup_blocks(pool)
result = {}
print("List of files with dedup indexes:")
count = 0
for path in file_blocks.keys():
    for block in file_blocks[path]:
        if dedups.get(block):
            if not path in result:
                result[path] = [0,0]
            cnt = dedups[block]
            if cnt == 1:
                result[path][0] += 1
            else:
                result[path][1] += 1
    if path in result:
        count += 1
        try:
            print (result[path][0], result[path][1], path.decode("utf-8"))
        except:
            print (result[path][0], result[path][1], path)

if count == 0:
    print ("No deduped files!")
    
            
        
