#!/usr/bin/env python3
# Created by Master on 2/27/2024

import io
import os
import pathlib
import argparse
import typing
import yaml

import jnt


USE_PADDED: bool = False
EXTRACT_SUB_FILES: bool = False
YAML_FILE_LISTING: str = 'DO_NOT_EDIT.YAML'


def create(folder_input: str, file_output: str):
    if not os.path.exists(folder_input):
        print(f'Input folder \"{folder_input}\" does not exist!')
        return
    else:
        if not os.path.isdir(folder_input):
            print(f'Given input \"{folder_input}\" is not a folder?!')
            return
        pass
    if os.path.exists(file_output) and os.path.isdir(file_output):
        print(f'Output \"{file_output}\" is a directory?! This should not happen!')
        return

    # TODO
    # generate file list
    fp_directory_listing = os.path.join(folder_input, YAML_FILE_LISTING)
    if not os.path.exists(fp_directory_listing):
        print(f'Directory listing \"{fp_directory_listing}\" does not exist!\nPlease re-extract \"DATA.JNT\"!')
        return
    with open(fp_directory_listing, mode='rt+') as io_file_listing:
        directory_listing = yaml.safe_load(stream=io_file_listing)
        pass
    for i in directory_listing:  # ensure ALL of these files exist
        tp = os.path.join(folder_input, i)
        if not os.path.exists(tp):
            print(f'File \"{i}\" does not exist in the path, but exists in the directory listing YAML!')
            print('Please re-extract \"DATA.JNT\"!')
            return
        del tp
        continue
    del i

    if os.path.exists(file_output):
        mode = 'w+'
        pass
    else:
        mode = 'x'
        pass
    file_jnt: jnt.JNT = jnt.JNT()
    with open(file_output, mode=f'{mode}b') as io_jnt:
        file_jnt.write_header(io_jnt)
        file_jnt.write_entries(io_jnt, folder_input, directory_listing)
        pass
    return


def generate_file_listing(file_jnt: jnt.JNT, stream):
    file_listing = []
    for entry in file_jnt.entries:
        file_listing.append(
            entry.name.fp
        )
        # TODO generate sub-jnt files too
        continue
    return yaml.safe_dump(file_listing, stream=stream, encoding='utf8')


def extract_io(io_input_jnt: typing.BinaryIO, folder_extracted: str):
    if not os.path.exists(folder_extracted):
        os.makedirs(folder_extracted)
        pass

    file_jnt: jnt.JNT = jnt.JNT()
    file_jnt.read_from_file(io_input_jnt)

    fp_file_listing = os.path.join(folder_extracted, YAML_FILE_LISTING)
    if os.path.exists(fp_file_listing):
        mode = 'w+'
        pass
    else:
        mode = 'x'
        pass
    with open(fp_file_listing, mode=f'{mode}t', encoding='utf-8') as io_file_listing:
        generate_file_listing(file_jnt, io_file_listing)
        pass

    for entry in file_jnt.entries:
        fp = pathlib.Path(os.path.join(folder_extracted, entry.name.fp))
        if not fp.parent.exists():
            os.makedirs(fp.parent)
            pass

        if EXTRACT_SUB_FILES and (fp.name.endswith('.JNT')):  # extract sub-JNT files
            print('WARNING: EXTRACTING SUB FILES IS UNSUPPORTED AND WILL END WITH ERRORS WHEN CREATING!')
            # TODO Remove this warning message when proper sub file extraction is implemented
            if os.path.exists(fp.name):
                if os.path.isfile(fp.name):
                    print(f'Cannot extract file \"{fp}\"!?')
                    continue
                pass
            with io.BytesIO(entry.data.read(io_input_jnt, entry.size_padded)) as io_sub_jnt:
                extract_io(io_sub_jnt, fp.as_posix())
                pass
            del io_sub_jnt
            pass
        else:
            if fp.exists():
                mode = 'w+'
                pass
            else:
                mode = 'x'
                pass
            with open(fp, mode=f'{mode}b') as io_entry:
                size: int = entry.size
                if USE_PADDED:
                    size = entry.size_padded
                    pass
                data: bytes = entry.data.read(io_input_jnt, size)
                io_entry.write(data)
                del data
                del size
                pass
            del io_entry
            del mode
            pass

        del fp
        continue
    return


def extract(input_jnt: str, folder_extracted: str):
    if os.path.exists(input_jnt):
        if not os.path.isfile(input_jnt):
            print(f'Input file \"{input_jnt}\" is not a valid file!')
            return
        pass
    else:
        print(f'Input file \"{input_jnt}\" does not exist!')
        pass

    print(f'Reading file \"{input_jnt}\"...')
    with open(input_jnt, mode='rb+') as io_jnt:
        extract_io(io_jnt, folder_extracted)
        pass
    print('Done reading file')
    return


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--extract', action='store_true')
    arg_parser.add_argument('--create', action='store_true')
    arg_parser.add_argument('--input', required=True, type=str)
    arg_parser.add_argument('--output', required=True, type=str)
    args = arg_parser.parse_args()

    if args.create and args.extract:
        print('Cannot have both --extract and --create arguments!')
        return
    if args.create:
        print('Creating...')
        create(args.input, args.output)
        print('Done creating')
        pass
    elif args.extract:
        print('Extracting...')
        extract(args.input, args.output)
        print('Done extracting')
        pass
    else:
        print('No mode selected!')
        pass

    return


if __name__ == '__main__':
    main()
    pass
