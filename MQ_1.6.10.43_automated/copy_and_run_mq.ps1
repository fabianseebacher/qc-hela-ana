### SET FOLDER TO WATCH + FILES TO WATCH + SUBFOLDERS YES/NO
    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = "N:\IDO_Proteomics_CellBiol\Temporary Backup_MS PC_Drive D\2021_05_May"
    $watcher.Filter = "*QC_HELA*.raw"
    $watcher.IncludeSubdirectories = $true
    $watcher.EnableRaisingEvents = $true  

### DEFINE ACTIONS AFTER AN EVENT IS DETECTED
    $action = { 
        ### Write the detected renaming event to the logfile.
        $basepath = "G:\hela\"
		$path = $Event.SourceEventArgs.FullPath
        $changeType = $Event.SourceEventArgs.ChangeType
        $logline = "$(Get-Date), $changeType, $path"
        $newfolder = (Get-Item $path).Basename
        Add-content $basepath'log.txt' -value $logline
        Write-Host $logline

		### Wait 1 minute and generate path with raw name as folder name.
        Start-Sleep -s 20
        
        $newpath = [string]$basepath+[string]$newfolder+"\"

        Write-Host "Waited for 20 seconds"

        ### Check if new path already exists (i.e. if file has already been copied). 
        if (Test-Path -Path $basepath'res\'$newfolder) {

            ### Report to logfile that folder already exists.
     
            $failtext = [string]$basepath+"res\"+[string]$newfolder+" already exists."
            $faillog = "$(Get-Date), $failtext"   
	        Add-content $basepath'log.txt' -value $faillog
            Write-Host $faillog

        } else {

            ### Create new folder and copy raw file to local disk
            New-Item -ItemType directory -Path $newpath
            Copy-Item -Path $path -Destination $newpath  
            $copytext = "Copied the file from "+[string]$path+" to "+$newpath

            ### Create a "additionalInfo" token txt file that contains file size and creation date
            $filesize = (Get-Item $path).length/1MB
            $created = (Get-Item $path).CreationTime
            $created2 = $created.ToString("yyyy-MM-dd HH:mm:ss")
            $tokenline = "$path,$filesize,$created2"
            New-Item -Path $basepath -Name $newfolder".txt" -ItemType file -Value $tokenline

            ### Report copying event to logfile 
            $logline2 = "$(Get-Date), $copytext"   
	        Add-content $basepath'log.txt' -value $logline2
            Write-Host $logline2

		    ### Copy mqpar.xml to subfolder and edit file path to local raw
            Copy-Item -Path $basepath'MQ_1.6.10.43_automated\mqparHelaNeptun.xml' -Destination $newpath
		    [xml]$myXML = $(Get-Content $newpath'\mqparHelaNeptun.xml')
     
            $filename = Split-Path $path -leaf
            $mystring = [string]$newpath+[string]$filename
		    $myXML.MaxQuantParams.filePaths.string=$mystring
            $savepath = [string]$newpath+'\mqpar.xml'
		    $myXML.Save($savepath)
            Remove-Item -Path $newpath'\mqparHelaNeptun.xml'

		    ### This starts the actual maxquant analyis
            Start-Sleep -s 30
            
            $text3 = "$(Get-Date), I started MaxQuant for $newpath"
		    Add-content $basepath'log.txt' -value $text3
            Write-Host $text3

		    $app = [string]$basepath+'MQ_1.6.10.43_automated\MaxQuant\bin\MaxQuantCmd.exe'
		    $arg1 = $savepath
		    & $app $arg1 

            Write-Host "Done"

            Start-Sleep -s 10

            ### Check if MQ ran finished properly. 
            $finpath = [string]$newpath+'\combined\proc\Finish_writing_tables 11.finished.txt'
            if (Test-Path -Path $finpath) {
                # If MQ finished properly, go ahead an run python script.
                $text4 = "$(Get-Date), Finsihed running MQ for $newpath"
		        Add-content $basepath'log.txt' -value $text4
                Write-Host $text4

                $destpath = [string]$basepath+'res\'+[string]$newfolder+'\'
                ### Write event to logfile
                $logline4 = "$(Get-Date), Starting Hela analyzer. "
		        Add-content $basepath'log.txt' -value $logline4
                Write-Host $logline4
                ### Create new subfolder in "res" named after the raw file 
                New-Item -Path $basepath'res\' -Name $newfolder -ItemType "directory" 
                ### Copy the content of txt folder from MQ results to thenew subfolder in  "res" directory
                Copy-Item -Path $newpath'\combined\txt\*' -Destination $destpath -Recurse 
                ### Copy the additional info file (with filesize + creation date) to res subfolder as well
                $tokenpath = [string]$basepath+[string]$newfolder+".txt"
                Move-Item -Path $tokenpath -Destination $destpath'additionalInfo.txt'
                ### Run python script to write results into table
                Write-Host "Running python script..."
                python $basepath'MQ_1.6.10.43_automated\hela_analyzer_v2.py'
                ### Wait 5 min and then copy the results table to network folder.
                Write-Host "Finished python script. Now waiting 2 minutes to copy to network drive."
                Start-Sleep -s 120
                Copy-Item -Path $basepath'\res\hela_auto2.xlsx' -Destination "N:\IDO_Proteomics_CellBiol\Temporary Backup_MS PC_Drive D\"
                
                $copytext = "$(Get-Date), Copied output table to network drive." 
                Add-content $basepath'log.txt' -value $copytext
                Write-Host $copytext

            } else {
                # Throw an error if MQ did not finish
                $text4 = "$(Get-Date), Error running MQ for $newpath"
		        Add-content $basepath'log.txt' -value $text4
                Write-Host $text4
            }

        }

        
              }    
### DECIDE WHICH EVENTS SHOULD BE WATCHED 
    Register-ObjectEvent $watcher "Renamed" -Action $action
    while ($true) {sleep 5}