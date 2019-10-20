"""
Lightweigt module for reading system font names from .ttf font files.
Based on http://www.codeproject.com/Articles/2293/Retrieving-font-name-from-TTF-file
Karim Bahgat, 2015
"""
# TODO: MAYBE ADD SUPPORT FOR WEIGHTS SUCH AS BOLD/ITALICS ETC



# Imports

import sys
import os
import struct



# System and font stuff
OSSYSTEM = {"win32":"windows",
             "darwin":"mac",
             "linux":"linux",
             "linux2":"linux"}[sys.platform]
SYSFONTFOLDERS = dict([("windows",["C:/Windows/Fonts/"]),
                       ("mac", ["/Library/Fonts/"]),
                       ("linux", ["/usr/share/fonts/truetype/"])])

# Include builtin fonts
LIBFONTFOLDER = os.path.join(os.path.split(__file__)[0], 'fonts')


# Apparently ttf is stored in big endian
endian = ">"



# Internals only

def _read_ushort(fileobj):
    frmt = endian + "H"
    raw = fileobj.read(struct.calcsize(frmt))
    (val,) = struct.unpack(frmt, raw)
    return val

def _read_ulong(fileobj):
    frmt = endian + "L"
    raw = fileobj.read(struct.calcsize(frmt))
    (val,) = struct.unpack(frmt, raw)
    return val

def _read_chars(fileobj, n):
    frmt = endian+bytes(n)+"s"
    raw = fileobj.read(struct.calcsize(frmt))
    (val,) = struct.unpack(frmt, raw)
    return val
    
def _read_file_header(fileobj):
    headerdict = {"MajorVersion": _read_ushort(fileobj),
                  "MinorVersion": _read_ushort(fileobj),
                  #"Version": _read_chars(fileobj, 4), MAYBE USE THIS INSTEAD...
                  "NumOfTables": _read_ushort(fileobj),
                  "SearchRange": _read_ushort(fileobj),
                  "EntrySelector": _read_ushort(fileobj),
                  "RangeShift": _read_ushort(fileobj)}
    if not headerdict["MajorVersion"] == 1 and headerdict["MinorVersion"] == 0:
        raise Exception("Only ttf version 1.0 is currently supported")
    return headerdict

def _read_offset_table(fileobj):
    tabledict = {"TableName": _read_chars(fileobj, 4),
                  "Checksum": _read_ulong(fileobj),
                  "Offset": _read_ulong(fileobj),
                  "Length": _read_ulong(fileobj)}
    return tabledict

def _read_namestable_header(fileobj):
    namesheaderdict = {"FormatSelector": _read_ushort(fileobj),
                      "RecordsCount": _read_ushort(fileobj),
                      "StorageOffset": _read_ushort(fileobj)}
    return namesheaderdict

def _read_namestable_record(fileobj):
    namesrecorddict = {"PlatformID": _read_ushort(fileobj),
                      "EncodingID": _read_ushort(fileobj),
                      "LanguageID": _read_ushort(fileobj),
                      "NameID": _read_ushort(fileobj),
                       "StringLength": _read_ushort(fileobj),
                       "StringOffset": _read_ushort(fileobj)}
    return namesrecorddict



# User Functions

def get_fontname(filepath):
    """
    Given a filepath to a .ttf font file, reads the font metadata
    and returns its font name.    
    """
    with open(filepath, "rb") as fileobj:

        # file header
        file_header = _read_file_header(fileobj)

        # find offset to the name table 
        for _ in range(file_header["NumOfTables"]):
            offset_table = _read_offset_table(fileobj)
            if offset_table["TableName"] == "name":
                break
        else:
            raise Exception("Could not find the names table")

        # skip ahead to the name table using the offset
        fileobj.seek(offset_table["Offset"])

        # read names table header
        namesheader = _read_namestable_header(fileobj)

        # loop through names records
        for _ in range(namesheader["RecordsCount"]):
            record = _read_namestable_record(fileobj)
            
            # NameID = 1 font family name.
            #        = 2 font subfamily name, including weights such as bold or italics.
            #        = 4 "Full font name; a combination of strings 1 and 2, or a similar human-readable variant"

            #print filepath,record["NameID"]
            if record["NameID"] == 4:

                # skip ahead
                fileobj.seek(offset_table["Offset"] + namesheader["StorageOffset"] + record["StringOffset"])

                # read name
                fontname = _read_chars(fileobj, record["StringLength"])

                # sometimes the font string has weird byte data in first position and between each character
                if fontname.startswith("\x00"):
                    fontname = fontname[1::2]

                #print filepath,record["NameID"],fontname
                return fontname

def get_fontpath(font):
    """
    Gets fontpath from either font name, fontfile name, or full fontfile path
    """
    font = font.lower()
    # first try to get human readable name from custom list
    if font in SYSFONTS:
        return SYSFONTS[font]
    # then try to get from custom font filepath
    elif os.path.lexists(font):
        return font
    # or try to get from filename in font folder
    else:
        for filepath in list(SYSFONTS.values()) + [LIBFONTFOLDER]:
            if filepath.endswith(font):
                return filepath
    # raise error if hasnt succeeded yet
    raise Exception("Could not find the font specified. Font must be either a human-readable name, a filename with extension in the default font folder, or a full path to the font file location")

def load_sysfonts():
    """
    Caches and returns a fontname-filepath mapping of available system fonts,
    by looking up SYSFONTFOLDERS. This function is run on startup, and
    the results can be accessed via the cached storage variable SYSFONTS. 
    """
    fontfilenames = dict([(filename.lower(), os.path.join(dirpath, filename))
                          for fontfold in SYSFONTFOLDERS[OSSYSTEM] + [LIBFONTFOLDER]
                           for dirpath,dirnames,filenames in os.walk(fontfold)
                          for filename in filenames
                          if filename.lower().endswith(".ttf")])
    fontnames = dict()
    for filename,filepath in fontfilenames.items():
        fontname = get_fontname(filepath)
        try:
            fontname = get_fontname(filepath)
            fontnames.update([(fontname.lower(), filepath)])
        except:
            # errors and fails are to be expected on some files, so just skip those
            pass

    # cache so other funcs can reuse results
    global SYSFONTS
    SYSFONTS = fontnames.copy()

    return fontnames

# Cache all sysfonts on import
load_sysfonts()










        
        

        
