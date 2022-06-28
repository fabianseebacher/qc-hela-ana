# qc-hela-ana
Quality control pipeline for MS-based proteomics. Automatically analyzes Hela samples with MaxQuant and extracts relevant parameters. A powershell script is listening for copying of new raw files that conatain a certain substring (e.g. *QC_HELA*) to a network folder. For real-time backup of raw files, we use SyncBackPro to copy them to a network location as soon as the MS run is finished. In order to analyze the raw files only after successful backup, the script uses the final renaming event of the temporary file as a trigger rather than the copying event itself. 

## Setup instructions
1. Clone this repo to your local analysis machine. 
2. Setup a Python installation that includes numpy and pandas (e.g. via Anaconda) and add it to your PATH variable. 
3. Download MaxQuant version of your choice and place the "MaxQuant" folder inside the "MQ_automated". We use version 1.6.10.43, as we have been using this version for manual analysis before and wanted to keep the continuity. Older MQ versions can be found here: https://drive.google.com/drive/folders/1Ja9iaCQ6mM66VQEeaS36hqq77bnsmxQF
5. Edit the fastFilePath variable in "mqpar.xml" to point to your fasta file. Edit the basepath variable in the "copy_and_run_mq.ps1" to point to the top folder of the repo on your machine. In the same file, set the $watcher.Path to the path on your network drive, where the Hela raw files are backed up.
6. Right-click on "copy_and_run_mq.ps1" and start the watcher by clicking "Run with Powershell".


## Comments
* We recommend to place all files on a fast SSD, as this will improve overall performance. As the script is based on a powershell FileWatcher, the PC or VM should be permanently stay on.
* Activity of the watcher will be written to a logfile and console. 
* File size and creation date are saved to a temporary file with the same name as the raw file and ultimately placed in the result folder alongside the MQ output files as "additionalInfo.txt".
* If multiple raw files are backed up in short succession, the script will analyze on one after the other. Beware that this may lead to a buildup, if the analysis time should be longer than the time between Hela samples. On our setup, it usually takes around 70 min from completion of acquisition on the MS to the final result in the table. A 2h Hela run  takes around 140 min including loading time.

## Extracted parameters

| Property | determined from | Values |
| ------------- | ------------- | ------------- |
| Filename | _summary.txt_ |  |
| analysis date | _summary.txt_ |  |
| File size [MB] | Raw file -> _additionalInfo.txt_ |  |
| creation date | Raw file -> _additionalInfo.txt_ |  |
| FAIMS | Rawfile name | "_1CV_" or "_noFAIMS_" to determine the presence of a FAIMS frontend on an Exploris 480. (default: noFAIMS)  |
| amount | Rawfile name | "_###ng_" to get the amount of peptides injected (default: 500ng)  |
| producer | Rawfile name | "_CPMS_", "_Pierce_" or "_MPI_" to identify the source of the HeLa sample. (default: CPMS)  |
| gradient length | Rawfile name | "_1h_" or "_2h_" (default: 2h)  |
| MS |  | Number of MS scans |
| MS/MS |  | Number of MS/MS scans |
| MS2/MS1 ratio |  | Ratio of MS/MS to MS scans |
| Peptide Seq Identified |  | Number of Peptides |
| ProteinGroups |  | Number of ProteinGroups |
| Uncalibrated mass error [ppm] | _evidence.txt_ |  |
| Retention length [s] |  | Peak width |
| MS TIC |  | Total ion current MS1 |
| MS Base peak intensity |  | Base peak intensity MS1 |
| MS/MS TIC |  | Total ion current MS2 |
| MS/MS Base peak intensity |  | Base peak intensity MS2 |  

## Known issues
* depending on network architecture, the FileWatcher might not be able to monitor subdirectories, even with IncludeSubdirectories set to True. A simple workaround would be to have only a single backup folder or to employ a watcher instance for each subfolder. 

## Future features
* automatically set the paths (e.g. of the backup drive) from config file
* extract identifier for MS device and write into output table (if you have multiple MS to monitor)
