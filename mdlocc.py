#!/usr/bin/python
#!encoding:utf-8


import os
import re
import argparse
import subprocess as sp


# mdlocc.py
# ---------
# Manage deMon local compilations.
# ----------------------------------------------------------------------


def check_demon():
    """Check for deMon path and version in $HOME/demon.
    Sets the working directory to $HOME/demon/X.Y.Z, where
    X.Y.Z is the deMon version."""

    global demon_path
    global working_dir

    demon_path = os.path.expandvars('$HOME/demon')
    if not os.path.exists(demon_path):
        print(f'{demon_path} doesn\'t exists.')
        return 1

    # Read available deMon versions
    os.chdir(demon_path)
    versions = [v for v in os.listdir() if re.match('\d.\d.\d', v)]
    default_version = os.path.join(demon_path, '.default-version')

    # Read default version and Fortran compiler or ask
    if os.path.exists(default_version):
        with open(default_version) as f:
            line = f.readline()
            vac = re.match('(\d.\d.\d).(\w+)', line)
            ver = vac.group(1)
            ftn = vac.group(2)
    else:
        print('Choose a deMon version:')
        for i,ver in enumerate(versions):
            print(f'{i+1}. {ver}')
        ver = versions[int(input())-1]

    working_dir = os.path.join(demon_path, ver)
    os.chdir(working_dir)

    return 0


def check_tags_dir():
    """Check if $HOME/demon/ver/tags exists.
    Otherwise, asks to create it."""

    global tags_dir
    tags_dir = os.path.join(working_dir, 'tags')

    if not os.path.exists(tags_dir):
        print(f'The directory {tags_dir} doesn\'t exists.')
        print('Do you want to create it? [Y/n]: ', end='')
        answer = input().lower()
        if answer == 'n':
            return 2
        else:
            os.mkdir(tags_dir)

    return 0


def calculate_tag_id(source='source'):
    """Calculates the tag id by sha1sum over the source files
    specified in `source`."""

    src_dir = os.path.join(working_dir, source)
    os.chdir(src_dir)

    # Create temporary file where sha1sum output is stored
    pid = os.getpid()
    tmp_file = os.path.join(working_dir, f'tmp.{pid}')

    # Calculate sha1sum on .f and .h files only
    sp.run(['echo', 'Calculating tag id...'])
    with open(tmp_file, 'w') as tf:
        for file in os.listdir():
            match = re.match('.*\.[fh]$', file)
            if match is None: continue

            sp.run(['sha1sum', file], stdout=tf)

    tag_id = sp.run(['sha1sum', tmp_file], capture_output=True)
    tag_id = tag_id.stdout.decode().split()[0]
    print(f'DONE')
    
    sp.run(['rm', tmp_file])
    os.chdir(working_dir)

    return tag_id


def get_objects():
    """Get objects folders for local deMon compilations.
    Returns a dictionary with the compilation type as keyword and
    a full paths to object dirs as values."""

    objects = {}
    for f in os.listdir():
        match = re.match('object\.(\w{3}).*$', f)
        if match is not None:
            ext = match.group(1)
            obj = os.path.join(working_dir, match.group(0))
            try:
                objects[ext].append(obj)
            except:
                objects[ext] = [obj]

    return objects


def create_tag(name, description, source='source'):
    """Creates tag by name, copies source and object files."""

    new_tag_dir = os.path.join(tags_dir, name)

    if os.path.exists(new_tag_dir):
        print(f'Tag {name} already exists.')
        print(f'Update tag? [y/N]: ', end='')
        answer = input().lower()
        if answer == 'y':
            update_tag(name, source)
            return 0
        else:
            return 0
    else:
        tag_id = calculate_tag_id(source)

    os.mkdir(new_tag_dir)
    os.chdir(new_tag_dir)
    sp.run(['mkdir', 'obj', 'src'])
    with open(f'tag.{tag_id}', 'w') as tag:
        tag.write(description)

    # Copy source and object files
    src_dir = os.path.join(working_dir, source)
    os.chdir(src_dir)
    for f in os.listdir():
        sp.run(['cp', f'{src_dir}/{f}', f'{new_tag_dir}/src/'])

    os.chdir(working_dir)
    objects = get_objects()
    for ext in objects:
        sp.run(['echo', f'Copying {ext} object files... '])
        os.mkdir(f'{new_tag_dir}/obj/{ext}')
        sp.run(['cp', '-r', *objects[ext], f'{new_tag_dir}/obj/{ext}'])
        print('DONE')

    return 0
    

def update_tag(name, source='source'):
    old_tag_id = get_tag_id(name)
    new_tag_id = calculate_tag_id(source)

    if old_tag_id == new_tag_id:
        print(f'Tag {name} is up to date.')
        return 0
    else:
        os.chdir(f'{tags_dir}/{name}')
        with open(f'tag.{new_tag_id}', 'w') as nt:
            sp.run(['cat', f'tag.{old_tag_id}'], stdout=nt)
        sp.run(['rm', f'tag.{old_tag_id}'])
        sp.run(['rm', '-rf', 'obj', 'src'])
        sp.run(['mkdir', 'obj', 'src'])

    # Copy source and object files
    src_dir = os.path.join(working_dir, source)
    os.chdir(src_dir)
    for f in os.listdir():
        sp.run(['cp', f'{src_dir}/{f}', f'{tags_dir}/{name}/src/'])

    os.chdir(working_dir)
    objects = get_objects()
    for ext in objects:
        sp.run(['echo', f'Copying {ext} object files... '])
        os.mkdir(f'{tags_dir}/{name}/obj/{ext}')
        sp.run(
                ['cp', 
                 '-r', 
                 *objects[ext], 
                 f'{tags_dir}/{name}/obj/{ext}']
            )
        print('DONE')

    return 0


def delete_tag(name):
    tag_dir = os.path.join(tags_dir, name)

    print(f'Delete tag {name}? [y/N]: ', end='')
    answer = input().lower()
    if answer == 'y':
        sp.run(['rm', '-rf', tag_dir])
        print(f'Tag {name} has been deleted.')
        return 0
    else:
        return 0


def show_tag(name):
    tag_dir = os.path.join(tags_dir, name)
    tag_id = get_tag_id(name)

    last_mod = sp.run(['date', '-r', tag_dir], capture_output=True)
    last_mod = last_mod.stdout.decode()

    with open(f'{tag_dir}/tag.{tag_id}', 'r') as tag:
        description = tag.read()
        lines = description.split('\n')

    print(f'{name} ({tag_id[-8:]})')
    for line in lines:
        print('\t' + line, end='\n')
    print('\t' + last_mod[:24] + '\n')

    return 0


def show_all_tags():
    os.chdir(tags_dir)
    for tag in os.listdir():
        show_tag(tag)

    os.chdir(working_dir)
    return 0


def get_tag_id(name):
    tag_dir = os.path.join(tags_dir, name)

    if not os.path.exists(tag_dir):
        print(f'Couldn\'t find tag {name}')
        return 4

    os.chdir(tag_dir)
    for f in os.listdir():
        _id = re.match('tag\.(.+)', f)
        if _id is not None:
            _id = _id.group(1)
            os.chdir(working_dir)
            return _id

def get_all_tags():
    os.chdir(tags_dir)
    tags = [tag for tag in os.listdir()]
    
    os.chdir(working_dir)
    return tags


def add_comment(name, comment):
    tag_dir = os.path.join(tags_dir, name)
    tag_id = get_tag_id(name)
    tag_file = os.path.join(tag_dir, f'tag.{tag_id}')

    with open(tag_file, 'r') as ct:
        current = ct.read()

    with open(tag_file, 'w') as ct:
        ct.write(comment + '\n')
        ct.write(current)

    return 0


if __name__ == '__main__':
    # Initialization
    check_demon()
    check_tags_dir()

    # Argument parser
    parser = argparse.ArgumentParser(
            prog='mdlocc.py', 
            description='Manage deMon local compilations.',
            fromfile_prefix_chars='@',
            epilog=('Last change: 2021 Apr 11 '
                '(See jota-de/small-tools at github)')
        )
    parser.add_argument(
            '-l',
            '--list',
            action='store_true',
            help='list all tags in working directory'
        )
    parser.add_argument(
            '-a',
            '--add',
            metavar='TAG',
            nargs=1,
            default=None,
            help='add tag from current source and objects'
        )
    parser.add_argument(
            '-d',
            '--delete',
            metavar='TAG',
            nargs=1,
            default=None,
            help='delete tag directory'
        )
    parser.add_argument(
            '-u',
            '--update',
            metavar='TAG',
            nargs=1,
            default=None,
            help='update tag using current source and objects'
        )

    args = parser.parse_args()
    add = args.add
    delete = args.delete
    update = args.update

    if args.list:
        show_all_tags()

    if add is not None:
        name = add[0]
        print(f'Tag {name} description:')
        description = input()
        print('source directory relative to')
        print(f'{working_dir}[/source]: ', end='')
        source = input()
        if source == '': source = 'source'
        create_tag(name, description, source)

    if delete is not None:
        tag = delete
        tag_id = get_tag_id(tag)
        if tag_id != 4:
            delete_tag(tag)
    else:
        print('delete is none')

    if update is not None:
        tag = update[0]
        tag_id = get_tag_id(tag)
        if tag_id != 4:
            update_tag(tag)

