#!/usr/bin/env python3
# Created by Master on 2/27/2024

import os
import pathlib
import argparse

import jnt


USE_PADDED: bool = True


def extract(input_jnt: str, folder_extracted: str):
    if os.path.exists(input_jnt):
        if not os.path.isfile(input_jnt):
            print(f'Input file \"{input_jnt}\" is not a valid file!')
            return
        pass
    else:
        print(f'Input file \"{input_jnt}\" does not exist!')
        pass
    if not os.path.exists(folder_extracted):
        os.makedirs(folder_extracted)
        pass

    print(f'Reading file \"{input_jnt}\"...')
    with open(input_jnt, mode='rb+') as io_jnt:
        file_jnt = jnt.JNT()
        file_jnt.read_from_file(io_jnt)
        for entry in file_jnt.entries:
            fp = pathlib.Path(os.path.join(folder_extracted, entry.name.fn))
            if not fp.parent.exists():
                os.makedirs(fp.parent)
                pass
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
                data: bytes = entry.data.read(io_jnt, size)
                io_entry.write(data)
                del data
                del size
                pass
            del io_entry

            del fp
            continue
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
        # TODO
        print('Creating...')
        print('')
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
