#!/usr/bin/env python3
# Created by Master on 2/27/2024

import dataclasses
import typing
import struct
import yaml


@dataclasses.dataclass
class JNT:

    @dataclasses.dataclass
    class Header:

        @dataclasses.dataclass
        class Entry:

            pos: int
            offset: int
            size: int  # length / 16 (4 int blocks)

        header_entries: list[Entry]

    @dataclasses.dataclass
    class Entry:

        @dataclasses.dataclass
        class Data:

            offset: int

            def read(self, _io: typing.BinaryIO, size: int) -> bytes:
                seek = _io.tell()
                _io.seek(self.offset)
                data: bytes = _io.read(size)
                _io.seek(seek)
                del seek
                return data

        @dataclasses.dataclass
        class Name:

            offset: int
            fp: str = None

            def read(self, _io: typing.BinaryIO):
                seek = _io.tell()  # save seek position
                _io.seek(self.offset)
                buf: bytes = _io.read(1)
                while not buf.endswith(b'\x00'):
                    buf += _io.read(1)
                    continue
                _io.seek(seek)  # jump back to seek position
                self.fp = buf[:-1].decode(encoding='ascii')  # decode file name
                return self

        size: int  # size
        size_padded: int  # size including padding
        data: Data = None  # (offset + data bytes)
        name: Name = None  # (offset + name)

    header: Header = None
    entries: list[Entry] = None

    def write_directory_listing(self, io_jnt: typing.BinaryIO, directory_listing: list[str]):
        # TODO
        # none of this shit makes sense
        return

    def write_entries(self, io_jnt: typing.BinaryIO, directory_listing: list[str]):
        self.write_directory_listing(io_jnt, directory_listing)
        return

    # noinspection PyTypeChecker
    def create_header(self):
        self.header = JNT.Header(
            [
                # always 0x800?
                JNT.Header.Entry(0, 0x800, None),  # size of header entries
                JNT.Header.Entry(8, 0x800, None)  # offset to first JNT file data?
            ]
        )
        return

    # noinspection PyComparisonWithNone
    def write_header(self, _io: typing.BinaryIO):
        if self.header == None:
            self.create_header()  # generate a dummy header first
            pass

        for i in self.header.header_entries:
            size = i.size
            offset = i.offset
            if size == None:
                size = 0xFFFF  # write FFFF as placeholder
                pass
            if offset == None:
                offset = 0xFFFF  # write FFFF as placeholder
                pass
            _io.write(struct.pack('<I', offset))
            _io.write(struct.pack('<I', size))
            del offset
            del size
            continue
        del i

        while _io.tell() != 0x800:  # pad header to 0x800
            _io.write(b'\x00')
            pass

        # TODO Re-write actual size / offset of header entries
        return

    # noinspection PyMethodMayBeStatic
    def read_entry(self, _io: typing.BinaryIO) -> Entry:
        entry = JNT.Entry(
            struct.unpack('<I', _io.read(4))[0],
            struct.unpack('<I', _io.read(4))[0],
            JNT.Entry.Data(struct.unpack('<I', _io.read(4))[0]),
            JNT.Entry.Name(struct.unpack('<I', _io.read(4))[0]).read(_io)
        )
        return entry

    def read_entries(self, _io: typing.BinaryIO):
        _io.seek(self.header.header_entries[0].offset)
        self.entries: list[JNT.Entry] = list([None] * self.header.header_entries[0].size)
        for i in range(0, len(self.entries)):
            entry = self.read_entry(_io)
            self.entries[i] = entry
            print(f'Found file entry \"{entry.name.fp}\" at offset 0x{entry.data.offset:02X}')
            continue
        del i
        return

    def read_header(self, _io: typing.BinaryIO):
        self.header = JNT.Header(
            [
                JNT.Header.Entry(_io.tell(), struct.unpack('<I', _io.read(4))[0], struct.unpack('<I', _io.read(4))[0]),
                JNT.Header.Entry(_io.tell(), struct.unpack('<I', _io.read(4))[0], struct.unpack('<I', _io.read(4))[0])  # Is this an actual second entry? Doesn't look like it is... just looks like an offset to the first entry
            ]
        )
        return

    def read_from_file(self, _io: typing.BinaryIO):
        self.read_header(_io)
        self.read_entries(_io)
        return
