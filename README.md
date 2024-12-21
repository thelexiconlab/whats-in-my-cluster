# What's in my cluster? Evaluating automated clustering methods to understand idiosyncratic search behavior in verbal fluency

This repository contains scripts to reproduce the analyses presented in the paper:

>> Kumar, A.A., Lundin, N.B., Jones, M.N. (in press). What’s in my cluster? Evaluating automated clustering methods to understand idiosyncratic search behavior in verbal fluency. *Journal of Memory and Language*.


The repository is organized as follows:
- `analysis`: contains the code for the analysis of participant and rater data. Open the `switch-analysis.Rproj` file to access the R project and run the scripts in the `analysis` folder. Alternatively, you can download the repository as a .zip file and view the knitted .html file in the `analysis` folder. 
- `forager_test`: contains code for using the python package *forager* to obtain predicted clusters and model estimates. To run forager on the data from different domains, navigate to the `forager_test` directory via the terminal, and run the code commented at the end of the `run_foraging.py` file.

Due to the size of the data and other files, some files are not included in this repository. These files can be accessed via the following link: [https://osf.io/m4dx3/](https://osf.io/m4dx3/). For reproducibility, please download the files and place them in the following directories:

- `data`: access via OSF link and store in subfolder titled `data`, contains the rater data from the pre-registered experiment
- `experiment`: access via OSF, contains the code for the pre-registered rater experiment, programmed in jsPsych 

