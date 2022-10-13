import sys
import os
import errno
import argparse
import re
from shutil import copyfile
from io import StringIO
import csv

#Author JRZ4
#Description: finds matchs and replaces lines on files and folders
#Input: 1st arg: Path of file containing files or folders. One line per file or folder
#       2nd arg: Path of file containing the matches and replaces.Files takes format takes csv International format to delimit match and replace
#       3rd arg: List of valid extensions. Avoid using unreadable files (.obj,.png...). One extension per line
#Output: Backup of the files [file].replaced_bak and match and replace result on original
#Details: For every line of the 1st path arg
#               If line is file match and replace every of the lines of 2nd path argument
#               If line is folder, match and replace in every file (recursively) every of the lines of 2nd path argument
#

def main(argv):
    parser = argparse.ArgumentParser(description='Match and replace on files or recursively on folders. Match can be regex compatible',usage="findmatchreplace.py [-i] [-w] [-simul] [-restore] [-regex] folders/files match/replaces extension")
    parser.add_argument('-i', dest='matchcase',action='store_const', const=True, default=False, help="Activate case sensitive if regex match")
    parser.add_argument('-w', dest='wholeword',action='store_const', const=True, default=False, help="Activate whole word if regex match")
    parser.add_argument('-simul', dest='simulation',action='store_const', const=True, default=False, help="Simulation")
    parser.add_argument('-restore',dest='restore',action='store_const', const=True, default=False, help="restore from the .replaced_bak files_")
    parser.add_argument('-regex',dest='regex',action='store_const', const=True, default=False, help="match regex based")
    parser.add_argument('foldersfile',help="Path of text file containing folders/files")
    parser.add_argument('replacesfile',help="Path of text file containing match/replaces. Files takes format takes csv International format to delimit match and replace")
    parser.add_argument('extensionsfile',help="Path of text file containing valid extensions")
    args = parser.parse_args()
    foldersfile = args.foldersfile
    replacesfile = args.replacesfile
    extensionsfile = args.extensionsfile
    matchcase = args.matchcase
    wholeword = args.wholeword
    simulation = args.simulation
    restore = args.restore
    regex = args.regex
    replaceformatlines = open(replacesfile).readlines()
    extensionsList = open(extensionsfile).readlines()
    if not restore:
        resultcsvfile = open('result.csv', 'w+')
        resultcsvfile.write("File,Match,Replace,Line,OriginalLine,ReplacedLine" + '\n')
    with open(foldersfile) as fpfoldersfile:
        for cnt,linepath in enumerate(fpfoldersfile):
            linepath = linepath.rstrip()
            if os.path.isdir(linepath):
                for dirname, dirnames, filenames in os.walk(linepath):
                    for filename in filenames:
                        for extension in extensionsList:
                            extension = extension.rstrip()
                            if filename.endswith(extension):
                                filenamepath = os.path.join(dirname, filename)
                                if restore:
                                    restorefrombackup(filenamepath,simulation)
                                else:
                                    resultcsvfile
                                    createcopyandreplace(filenamepath,replaceformatlines,resultcsvfile,wholeword,matchcase,simulation,regex)
            elif os.path.isfile(linepath):
                filename = linepath
                for extension in extensionsList:
                    extension = extension.rstrip()
                    if filename.endswith(extension):
                        if restore:
                            restorefrombackup(filename,simulation)
                        else:
                            createcopyandreplace(filename, replaceformatlines,resultcsvfile,wholeword,matchcase,simulation,regex)
            else:
                print("Error on line: ",linepath)
    if not restore:
        resultcsvfile.close()

#Function takes a path of a file and a list of lines with matches and replaces. Backup file is [pathfile].replaced_bak
#matches and replaces format: [match];[replace] -> limitation on character ";"

def createcopyandreplace(pathfile,listlinesreplace,resultcsvfile,wholeword,matchcase,simulation,regex):
    linesBefore = open(pathfile).read().splitlines()
    linesAfter = open(pathfile).read().splitlines()
    for matchreplaceline in listlinesreplace:
        f = StringIO(matchreplaceline)
        splittedline = list(csv.reader(f, delimiter=','))
        text_match = splittedline[0][0]
        text_replace = splittedline[0][1]
        text_replace = text_replace.rstrip()
        for i in range(0 , len(linesAfter)):
            if regex:
                regexstring= re.compile('')
                if(wholeword):
                    regexstring = r"\b" + text_match + r"\b"
                else:
                    regexstring = r""+text_match+r""
                found=False
                if(matchcase):
                    found = re.search(regexstring, linesBefore[i])
                else:
                    found = re.search(regexstring, linesBefore[i], re.IGNORECASE)
                if found:
                    print("Found " +str(chr(34))+ text_match+ str(chr(34)) + " in: " + linesBefore[i])
                    print("File: " + pathfile)
                    print()
                    if text_replace == "DELETE":
                        linesAfter[i] = ""
                    else:
                        if (matchcase):
                            linesAfter[i] = re.sub(regexstring, text_replace, linesAfter[i])
                        else:
                            linesAfter[i] = re.sub(regexstring, text_replace, linesAfter[i],re.IGNORECASE)
                    resultcsvfile.write(pathfile+","+text_match+","+text_replace+","+str(i)+","+ str(chr(34))+linesBefore[i]+ str(chr(34))+","+ str(chr(34))+linesAfter[i]+ str(chr(34))+ '\n')
            else:
                if text_match in linesBefore[i]:
                    print("Found " + str(chr(34)) + text_match + str(chr(34)) + " in: " + linesBefore[i])
                    print("File: " + pathfile)
                    print()
                    if text_replace == "DELETE":
                        linesAfter[i] = ""
                    else:
                        linesAfter[i] = linesAfter[i].replace(text_match, text_replace)
                    resultcsvfile.write(pathfile+","+text_match+","+text_replace+","+str(i)+","+ str(chr(34))+linesBefore[i]+ str(chr(34))+","+ str(chr(34))+linesAfter[i]+ str(chr(34))+ '\n')
    if(linesAfter!=linesBefore):
        if not simulation:
            try:
                with open(pathfile, 'w') as outputfile:
                    backuppathfile = pathfile + ".replaced_bak"
                    outputfilebackup = open(backuppathfile,"w+")
                    outputfile.write('\n'.join(linesAfter) + '\n')
                    outputfilebackup.write('\n'.join(linesBefore) + '\n')
                    print("Backup created: " + backuppathfile)
                    print()
            except IOError as error:
                if error.errno == errno.EACCES:
                    print("Read only file: " + pathfile)
                    print()
                else:
                    print("Unknown error on file: " + pathfile)
                    print()

def restorefrombackup(pathfile,simulation):
    backuppathfile = pathfile + ".replaced_bak"
    if os.path.isfile(pathfile) and os.path.isfile(backuppathfile):
        if simulation:
            print("Found backup: " + backuppathfile)
        else:
            try:
                os.remove(pathfile)
                os.rename(backuppathfile,pathfile)
                print("Restored from backup: " + pathfile)
            except IOError as error:
                if error.errno == errno.EACCES:
                    print("Read only file: " + pathfile)
                    print()
                else:
                    print("Unknown error on file: " + pathfile)
                    print()


if __name__ == "__main__":
    main(sys.argv[1:])