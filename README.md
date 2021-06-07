# qc-hela-ana
Quality control pipeline for MS-based proteomics. Automatically analyzes Hela samples with MaxQuant and extracts relevant parameters. The pipeline is triggered by the copying of new raw files that conatain a certain substring (e.g. *QC_HELA*) to a network folder. For real-time backup of raw files, we use SyncBackPro to copy the raw files to a network location as soon as the MS run is finished. In order to analyze the raw files only after successful backup, we actually use the final renaming of the temporary file as a trigger rather than the copying event itself. 

## Setup instructions
1. Clone this repo to your local machine. 
2. Setup a Python installation that includes numpy and pandas (e.g. via Anaconda) and add it to your PATH variable. 
3. Download MaxQuant version of your choice and place the "MaxQuant" folder inside the "MQ_automated". We use 1.6.10.43, since we have been using this version for manual analysis before and wanted to keep the continuity. Older MQ versions can be found here: https://drive.google.com/drive/folders/1Ja9iaCQ6mM66VQEeaS36hqq77bnsmxQF
5. Place th
6. 

## Known issues
* depending on network architecture, the FileWatcher might not be able to monitor subdirectories, even with IncludeSubdirectories set to True. Simple workaround would be to have only a single backup folder or multiple watcher instances for each subfolder. 

## Future features
* automatically set the paths (e.g. of the backup drive) by running a small startup script
