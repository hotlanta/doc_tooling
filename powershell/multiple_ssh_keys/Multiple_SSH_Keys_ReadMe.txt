All scripts and files can be found here: \Mondi-Tech\Everyone - BSS\HPE MPC Common\Tools\Scripts\multiple_ssh_keys\
1. Copy config file to C:/Users/<username>/.ssh folder
2. Run Check-GitRemotes.ps1 to verify Git repo and if the URL contains the expected hostname pattern
   - Open script in a text editor and change file paths. I have HCLTech GitHub repos at "d:\hcltech_git\" and HPE GitHub repos at "d:\hpe_git\".
   - Before running the above PowerShell script run this command: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
3. Check if ssh-agent service is running (use PowerShell as Admin):
   Get-Service ssh-agent | Format-List *
   - Look for fields Status (Running/Stopped) StartType (Automatic/Manual/Disabled)
4. Set ssh-agent service to Automatic startup (use PowerShell as Admin):
   Set-Service -Name ssh-agent -StartupType Automatic
5. Start ssh-agent (use PowerShell as Admin):
   Start-Service ssh-agent
6. add ssh keys to ssh-agent (use PowerShell as Admin):
   ssh-add C:/Users/<username>/.ssh/id_rsa
   ssh-add C:/Users/<username>/.ssh/id_rsa_hpe
   ssh-add C:/Users/<username>/.ssh/id_ed25519
7. Add SSH keys to ssh-agent service on Windows startup using Add-SSHKeys-ps1 script
   - Open script in a text editor and change file paths from "C:/Users/EricSzegedi/.ssh/" to the path where your .ssh folder exists.
   - Create shortcut to run the script at startup:
     -- Right click your Desktop->New->Shortcut
	 -- For location, enter (change username to your laptop's username): powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File "C:\Users\EricSzegedi\Scripts\Add-SSHKeys.ps1"
	 -- Name shortcut something like Add SSH Keys
	 -- Click Finish
   - Add shortcut to Startup folder
     -- Press Win + R and type shell:startup
	 -- Move the shortcut you just created into this folder