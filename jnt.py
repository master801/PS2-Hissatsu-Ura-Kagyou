#!/usr/bin/env python3
# Created by Master on 2/27/2024

import dataclasses
import typing
import struct


@dataclasses.dataclass
class JNT:

    @dataclasses.dataclass
    class Header:

        @dataclasses.dataclass
        class Entry:

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
                return data

        @dataclasses.dataclass
        class Name:

            offset: int
            fn: str = None

            def read(self, _io: typing.BinaryIO):
                seek = _io.tell()  # save seek position
                _io.seek(self.offset)
                buf: bytes = _io.read(1)
                while not buf.endswith(b'\x00'):
                    buf += _io.read(1)
                    continue
                _io.seek(seek)  # jump back to seek position
                self.fn = buf[:-1].decode(encoding='ascii')  # decode file name
                return self

        size: int  # size
        size_padded: int  # size including padding
        data: Data = None  # (offset + data bytes)
        name: Name = None  # (offset + name)

    header: Header = None
    entries: list[Entry] = None

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
            print(f'Found file entry \"{entry.name.fn}\" at offset 0x{entry.data.offset:02X}')
            continue
        del i
        return

    def read_header(self, _io: typing.BinaryIO):
        self.header = JNT.Header(
            [
                JNT.Header.Entry(struct.unpack('<I', _io.read(4))[0], struct.unpack('<I', _io.read(4))[0]),
                JNT.Header.Entry(struct.unpack('<I', _io.read(4))[0], struct.unpack('<I', _io.read(4))[0])  # Is this an actual second entry? Doesn't look like it is...
            ]
        )
        return

    def read_from_file(self, _io: typing.BinaryIO):
        self.read_header(_io)
        self.read_entries(_io)
        return
