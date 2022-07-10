@ECHO OFF
:doAgain
	:: CLS
	ENDLOCAL
	SETLOCAL EnableDelayedExpansion
	TITLE AOL GID Converter

	python.exe "C:\Users\My Free PC\Documents\GitHub\Re-AOL\gid_tools\gid_conv.py"

	SET /p Again=Convert another? [hit ENTER for YES, type "N/n" for NO]: 
	if '%Again%'=='' (
		SET Again=% %
		GOTO doAgain
	)
