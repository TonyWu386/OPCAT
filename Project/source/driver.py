#!/usr/bin/env python3.5

import getopt, sys, os
import data_retrieval.remoteGet as REM
import data_retrieval.apiGet as API
import data_parsing.XML_data_parser as XML
import data_parsing.CSV_data_parser as CSV
import data_comparison.Comparator as COMP
import data_comparison.proposed_change as PC
import github.gitClone as GIT
import storage_manager.storage_manager as STORAGE
import datetime

# usage string
usage_str = "usage: driver [--help] [--update] [--output string] [--planet " \
            + "string] [--showall | --shownumber int]\n"

# link to NASA catalogue
NASA_link = "http://exoplanetarchive.ipac.caltech.edu/cgi-bin/nsted\
API/nph-nstedAPI?table=exoplanets"

# link to exoplanet.eu catalogue
exoplanetEU_link = "http://exoplanet.eu/catalog/csv/"

# paths to NASA and EU csv files on local drive
nasa_file = "storage/nasa_csv"
EU_file = "storage/exoplanetEU_csv"

# path to XML .gz file
XML_path = "storage/OEC_XML.gz"

# list of all proposed changes (accumulated on update())
CHANGES = []


def status():
    '''() -> NoneType
    Prints the current status of the updates, including the following
    relevant information: time of last update, current auto-update settings and
    the number of changes pending to be reviewed.
    '''
    unpack_changes()
    last_update = STORAGE.config_get("last_update")
    num_changes = len(CHANGES)
    if last_update == "Never":
        print("Last Update: Never" + "\n")
    else:
        print("\nLast Update: " + str(last_update))
        print("Number of proposed changes stored : " + str(num_changes) + "\n")


def usage():
    '''() -> NoneType
    Example called method
    Returns NoneType
    '''
    print(usage_str)


def print_help():
    '''() -> NoneType
    '''
    print(STORAGE.manual())


def clean_files():
    '''() -> NoneType
    Removes text files from previous update.
    Returns None
    '''
    for name in [nasa_file, EU_file]:
        try:
            os.remove(name)
        except:
            pass


def show_all():
    '''() -> NoneType
    Skeleton function
    '''
    unpack_changes()
    # sort the list of proposed changes    
    i = 1
    while i <= len(CHANGES):
        show_number(i)
        i += 1
    print("\nNumber of changes shown : " + str(len(CHANGES)))
    print("Last update : " + str(STORAGE.config_get("last_update")))
    # to reset last update time to default state ("Never"), and config file in
    # general : STORAGE.clean_config_file()
    print("End.\n")


def show_range(start, end):
    '''() -> NoneType
    Skeleton function
    '''
    unpack_changes()
    # sort the list of proposed changes
    if isinstance(start, str) and start.lower() == "s":
        start = 1
    elif isinstance(start, str) and start.lower() == "e":
        start = len(CHANGES)
    if isinstance(end, str) and end.lower() == "e":
        end = len(CHANGES)
    elif isinstance(end, str) and end.lower() == "s":
        end = 1
    bothInts = isinstance(start, int) and isinstance(end, int)
    validRange = 1 <= start <= len(CHANGES) and 1 <=  end <= len(CHANGES)
    if (bothInts and validRange):
        if start <= end:
            i = start
            while i <= end:
                show_number(i)
                i += 1
        else:  # start > end
            # reverse range
            i = start
            while i >= end:
                show_number(i)
                i -= 1
    else:
        print("Invalid range")


def show_number(n):
    '''(int) -> NoneType
    Skeleton function
    '''
    if len(CHANGES) == 0:
        unpack_changes()
    if n <= len(CHANGES) and n > 0:
        print("\nShowing number : " + str(n) + "\n")
        print(CHANGES[n - 1])
        print()
    else:
        print("Out of range.")


def accept(n, strategy):
    '''(int, int) -> NoneType
    Function for accepting a specific change/addition
    n argument is that change number to accept
    strategy argument accepts "1" or "2"
    Returns NoneType
    '''
    if len(CHANGES) == 0:
        unpack_changes()
    if n < len(CHANGES) and n >= 0:
        if (strategy == 1):
            GIT.modifyXML(CHANGES[n], n)
        else:
            GIT.modifyXML(CHANGES[n], n, mode=True)
    else:
        print("Out of range.")
    print("\nAccepted: \n" + str(n))


def accept_all(strategy):
    '''() -> NoneType
    Function for accepting all changes/additions
    strategy argument accepts "1" or "2"
    '''
    unpack_changes()
    i = 0
    # for demo change back after!!!!!!!!
    while i < 25:
    #while i < len(CHANGES):
        accept(i, strategy)
        i += 1


def deny_number(n):
    # TODO
    print("denied ", n)


def deny_all():
    unpack_changes()
    i = 1
    while i <= len(CHANGES):
        deny_number(i)
        i += 1
    print("Done.")


def postpone_number(n):
    global CHANGES
    if len(CHANGES) == 0:
        unpack_changes()
    length = len(CHANGES)
    if n > 0 and n <= length:
        CHANGES.pop(n - 1)
        STORAGE.write_changes_to_memory(CHANGES)
    else:
        print("Out of range.")


def postpone_all():
    unpack_changes()
    i = 1
    while i <= len(CHANGES):
        postpone_number(i)
        i += 1
    print("Done.")


def unpack_changes():
    # TODO : check that the last time of the update is not "Never"
    global CHANGES
    CHANGES = STORAGE.read_changes_from_memory()


def update():
    '''() -> NoneType
    Example called method
    Returns NoneType
    '''
    # open exoplanet catalogue
    global CHANGES
    CHANGES = []
    XML.downloadXML(XML_path)
    OEC_lists = XML.buildSystemFromXML(XML_path)
    OEC_systems = OEC_lists[0]
    OEC_stars = OEC_lists[1]
    OEC_planets = OEC_lists[2]

    # delete text files from previous update
    clean_files()

    # targets:
    # Saves nasa database into a text file named nasa_file
    NASA_getter = API.apiGet(NASA_link, nasa_file)
    try:
        NASA_getter.getFromAPI("&table=planets")
    # NASA_getter.getFromAPI("")
    except (TimeoutError, API.CannotRetrieveDataException) as e:
        print("NASA archive is unreacheable.\n")

    # Saves exoplanetEU database into a text file named exo_file
    exoplanetEU_getter = API.apiGet(exoplanetEU_link, EU_file)
    try:
        exoplanetEU_getter.getFromAPI("")
    except (TimeoutError, API.CannotRetrieveDataException) as e:
        print("exoplanet.eu is unreacheable.\n")

    # build the dict of stars from exoplanet.eu
    EU_stars = CSV.buildDictStarExistingField(EU_file, "eu")
    # build the dict of stars from NASA
    NASA_stars = CSV.buildDictStarExistingField(nasa_file, "nasa")
    # build the dictionary of stars from Open Exoplanet Catalogue
    OEC_stars = XML.buildSystemFromXML(XML_path)[4]

    # clean both dictionaries
    for d in [EU_stars, NASA_stars]:
        for key in d:
            if d.get(key).__class__.__name__ != "Star":
                d.pop(key)

    # add chages from EU to the list
    for key in EU_stars.keys():
        if key in OEC_stars.keys():
            C = COMP.Comparator(EU_stars.get(key), OEC_stars.get(key), "eu")
            CHANGES.extend(C.proposedChangeStarCompare())

    # add chages from NASA to the list
    for key in NASA_stars.keys():
        if key in OEC_stars.keys():
            C = COMP.Comparator(NASA_stars.get(key), OEC_stars.get(key), "nasa")
            CHANGES.extend(C.proposedChangeStarCompare())

    # sort the list of proposed changes
    CHANGES = PC.merge_sort_changes(CHANGES)
    # write the list of proposed changes to memory using storage_manager
    STORAGE.write_changes_to_memory(CHANGES)
    # calculate current time
    curr_time = datetime.datetime.strftime(datetime.datetime.now(),
                                           '%Y-%m-%d %H:%M:%S')
    STORAGE.config_set("last_update", curr_time)
    print("\nNumber of differences discovered : " + str(len(CHANGES)))
    print("Current time : " + curr_time)
    print("Update complete.\n")


def main():
    '''() -> NoneType
    Main driver method
    Accepts command line arguments
    Returns NoneType
    '''
    # flags which do not expect parameter (--help for example)
    # short opts are single characters, add onto shortOPT to include
    shortOPT = "huacel"
    # log opts are phrases, add onto longOPT to include
    longOPT = ["help", "update", "showall", "acceptall", "acceptall2",
               "denyall", "status", "postponeall"]

    # flags that do expect a parameter (--output file.txt for example)
    # similar to shortOPT
    shortARG = "opsntdr"
    # similar to longOTP
    longARG = ["output", "planet", "shownumber", "accept", "accept2", "deny",
               "showrange", "postpone"]

    # arg, opt pre-processor, do not edit
    short = ':'.join([shortARG[i:i + 1] for i in range(0, len(shortARG), 1)]) \
            + ":" + shortOPT
    long = [arg + "=" for arg in longARG] + longOPT

    try:
        opts, args = getopt.getopt(sys.argv[1:], short, long)
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    output = None
    planet = None
    show_parameter = None
    show_range_flag = False
    show_range_parameter = None
    update_flag = False
    show_flag = False
    all_flag = False
    accept_flag = False
    accept_all_flag = False
    accept_all2_flag = False
    accept_marker = None
    accept2_flag = False
    accept2_marker = None
    deny_flag = None
    deny_all_flag = None
    deny_marker = None
    postpone_flag = None
    postpone_marker = None
    postponeall_flag = None

    for o, a in opts:

        # handles args and opts
        # a contains parameter for ARGs, not OPTs

        # help
        if o in ("-" + shortOPT[0], "--" + longOPT[0]):
            print_help()
            sys.exit()

        # update
        elif o in ("-" + shortOPT[1], "--" + longOPT[1]):
            update_flag = True

        # output
        elif o in ("-" + shortARG[0], "--" + longARG[0]):
            output = a

        # planet
        elif o in ("-" + shortARG[1], "--" + longARG[1]):
            planet = a

        # shownumber
        elif o in ("-" + shortARG[2], "--" + longARG[2]):
            show_flag = True
            show_parameter = int(a)

        # showall
        elif o in ("-" + shortOPT[2], "--" + longOPT[2]):
            show_flag = True
            all_flag = True

        # accept
        elif o in ("-" + shortARG[3], "--" + longARG[3]):
            accept_flag = True
            accept_marker = int(a)

        # accept
        elif o in ("-" + shortARG[4], "--" + longARG[4]):
            accept2_flag = True
            accept2_marker = int(a)

        # acceptall
        elif o in ("-" + shortOPT[3], "--" + longOPT[3]):
            accept_all_flag = True

        # acceptall
        elif o in ("-" + shortOPT[4], "--" + longOPT[4]):
            accept_all2_flag = True

        # deny
        elif o in ("-" + shortARG[5], "--" + longARG[5]):
            deny_flag = True
            deny_marker = int(a)

        # denyall
        elif o in ("-" + shortOPT[5], "--" + longOPT[5]):
            deny_all_flag = True

        # status
        elif o in ("--" + longOPT[6]):
            status()

        # showrange
        elif o in ("-" + shortARG[6], "--" + longARG[6]):
            show_flag = True
            show_range_flag = True
            show_range_parameter = a

        # postpone
        elif o in ("--" + longARG[7]):
            postpone_flag = True
            postpone_marker = int(a)

            # postponeall
        elif o in ("--" + longOPT[7]):
            postponeall_flag = True

        else:
            usage()
            assert False, "unhandled option"

    if (show_flag):
        if ((all_flag) and (show_parameter)):
            print_help()
            return 1
        elif (all_flag):
            show_all()
        elif show_range_flag:
            try:
                startend = show_range_parameter.split("-")
                if startend[0].lower() == "s":
                    start = "s"
                elif startend[0].lower() == "e":
                    start = "e"
                else:
                    start = int(startend[0])
                if startend[1].lower() == "e":
                    end = "e"
                elif startend[1].lower() == "s":
                    end = "s"
                else:
                    end = int(startend[1])
                show_range(start, end)

            except:
                print("Invalid Range.")
        else:
            try:
                show_parameter = int(show_parameter)
                show_number(show_parameter)
            except ValueError:
                print("Invalid Parameter to shownumber.")

    # update
    if (update_flag):
        update()

    # accept
    if (accept_flag):
        GIT.initGit()
        accept(accept_marker, 1)

    # accept all
    if (accept_all_flag):
        GIT.initGit()
        accept_all(1)
        print("Accepted all.")

    # accept
    if (accept2_flag):
        GIT.initGit2()
        accept(accept2_marker, 2)
        GIT.finalizeGit2()

    # accept all
    if (accept_all2_flag):
        GIT.initGit2()
        accept_all(2)
        GIT.finalizeGit2()
        print("Accepted all2")

    # deny
    if (deny_flag):
        deny_number(deny_marker)

    # deny all
    if (deny_all_flag):
        deny_all()

    # postpone
    if (postpone_flag):
        postpone_number(postpone_marker)

    # postponeall
    if (postponeall_flag):
        postpone_all()


if __name__ == "__main__":
    main()
