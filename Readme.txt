Prerequisite:
- Python suds
- Django web app Portal already deployed


GenomicIndexer:
Gets all available cDNA from HVP database and run the Mutalyzer batchjob webservices(see https://mutalyzer.nl/webservices for info) to 
get the genomic equivalent variant nomenclature and the genomic refseqs. e.g: "NM_000059.3:c.3396A>G" to "NC_000013.10:g.32911888A>G".

To Run: set the path to one directory above where the HVP Portal django app is installed. 
e.g: if django Portal app is installed at "/home/user/projects/Portal", put in "/home/user/projects" as the path.
Then just run "python GenomicMutalyzer.py"



cDNAIndexer:
Reads all cDNA variants from HVP database and indexes the positions for searching ranges in portal.

To Run: set the path to one directory above where the HVP Portal django app is installed. 
e.g: if django Portal app is installed at "/home/user/projects/Portal", put in "/home/user/projects" as the path.
Then just run "python cDNAIndexer.py"
