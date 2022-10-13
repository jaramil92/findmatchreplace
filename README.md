Description: finds matchs and replaces lines on files and folders
Input: 1st arg: Path of file containing files or folders. One line per file or folder
       2nd arg: Path of file containing the matches and replaces.Files takes format takes csv International format to delimit match and replace
       3rd arg: List of valid extensions. Avoid using unreadable files (.obj,.png...). One extension per line
Output: Backup of the files [file].replaced_bak and match and replace result on original
Details: For every line of the 1st path arg
               If line is file match and replace every of the lines of 2nd path argument
               If line is folder, match and replace in every file (recursively) every of the lines of 2nd path argument
               
findmatchreplace.py [-i] [-w] [-simul] [-restore] [-regex] folders/files match/replaces extension"