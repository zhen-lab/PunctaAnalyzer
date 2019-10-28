% Copyright (C) 20071220 Taizo Kawano <tkawano at mshri.on.ca>
%
% This program is free software; you can redistribute it and/modify it 
% under the term of the GNU General Public License as published bythe Free Software Foundation;
% either version 2, or (at your option) any later version.
% 
% This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
% without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
% See the GNU General Public License for more details.
% 
% You should have received a copy of the GNU General Public License
% along with this file.  If not, write to the Free Software Foundation,
% 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

% This is a batch processing function for Octave/Matlab punctaanalysis program, punctaanalyser.
% Youll get output files containing each analysing data types, such as "distance.txt". 
%
% To use this program, you have to prepare a series of files named as 
% wt-1.txt, wt-2.txt... e5-1.txt, e5-2.txt etc. by imgprossor, other program written for puncta analysis.
% And all of these files should be in the same working directry with analyser.m and batch.m
% Then command like >batch(`wt,e5,fc16,`). (the genotypes shoud sepalate with "," without space.)
% If you prefer different threshold setting, use like this batch(`wt,e5,fc16,`, 20, 100)

% Defaultobjective is changed to 0. It will use pixel as out put unit. 091026

function batch (samplenames, thresholdcoeff, fixthreshold, mode, objective)
  % default values.
  defaultthreshold = 20;
  defaultfixthreshold = 1000;
  defaultmode = 1;
  defaultobjective = 0;
  %defaultobjective = 100;
% Octave and Matlab may need different code. So, here is Octave/Matlab distinction code
% This code is also product of strugle with differece between two environment. If its octave....
versionstr = version;
versionnum = str2num(versionstr(1));
% Octave2.9.9: environment == 1, Matlab6.5: environment == 0.
if(versionnum < 6)
  environment = 1;
else
  environment = 0;
end

  % suggestion for unexpected inputs.
  if(nargin < 1)
    error ('require samplenames');
  elseif(nargin > 5)
    usage ('punctaanalyser(samplenames, thresholdcoeff, fixthreshold, mode, objective)');
  end
  
  if(nargin == 1)
    thresholdcoeff = defaultthreshold;
    fixthreshold = defaultfixthreshold;
    mode = defaultmode;
    objective = defaultobjective;
  elseif(nargin == 2)
    fixthreshold = defaultfixthreshold;
    mode = defaultmode;
    objective = defaultobjective;
  elseif(nargin == 3)
    mode = defaultmode;
    objective = defaultobjective;
  elseif(nargin == 4)
    if(mode == 1)
      mode = defaultmode;
    %Matlab dont use !=. instead ~=  
    elseif(mode ~= 1)
      mode = 0;
    end
    objective = defaultobjective;
  elseif(nargin == 5)
    if(objective == 0)
      objective = 0;
    elseif(objective == 100)
      objective = 100;
    elseif(objective == 63)
      objective = 63;
    elseif(objective == 40)
      objective = 40;
    else
      error('unknown objective: enter 100, 63 or 40 at fifth value');
    end
    if(mode == 1)
      mode = defaultmode;
    elseif(mode ~= 1)
      mode = 0;
    end
  end
 

if(mode == 0)
  modestring = 'noisy';
elseif(mode == 1)
  modestring = 'silent';
end

samplenames
thresholdcoeff
fixthreshold
modestring
objective

input('Do you want to process with this condition? y/n ', 's')
if(ans == 'n')
  error('stopped.')
elseif(ans == 'y')
  sprintf('-----------PROCESS START: it will takes a while.------------')
  sprintf('\n')
elseif(ans ~= ('y' | 'n'))
  error('stopped.')
end

%----------------- Step 1: data file definition. --------------------
% problem is if matlab can use split. may have strsplit? or need to use regexp.
% damn no split no strsplit. also regexp has difference. and no substr. 
% So, subfunction hmsplit(handmade split) was made.
genotypes = hmsplit(samplenames, ',')
[numberofgenotypes,dummy] = size(genotypes);
listorder = 1;
% You may change the extension.
extension = '.txt';


%------------------ Step 2: data type definition and preparing output files --------------------
%%%%%%%%%%%%%%%%%%%%%%%%%%%%% For those who want to use this batch script for other analysis script
% This list indicating data types what are corrected with this batch script.
% They are also used as filename and label name within the datafile.
analysisfactor = str2mat('count', 'width', 'gap', 'distance', 'intensity', 'volume', 'lineardensity', 'fixwidth', 'fixvolume', 'fixgap', 'fixwidthlineardensity', 'fixgaplineardensity');

% Follwing is a list of valiables obtained from child process. These valiables must correspond to the above.
correspondval = str2mat('pcount', 'pwidths', 'pgaps', 'pdist', 'pintens', 'pvolumes', 'plineardensity', 'fixwidth', 'fixvol', 'fixgap', 'fixwidthlineardensity', 'fixgaplineardensity');

[numberoffactor, temp] = size(analysisfactor);

% prepare CLEAN data files to write the data later.
% The OS (windows or not) is detecting to write with proper return code.
% This process erase previous data, so if you need previous one, 
% rename them or put them into different directory before run this batch script.
% In other word, if you want to append additional data, comment out following block.
if(ispc)
    for a = 1:numberoffactor
	    datafactor = deblank(analysisfactor(a, :));
	    fid = fopen(strcat(datafactor, '.txt'), 'w');
	    fprintf(fid, strcat(datafactor, ' genotype\r\n'));
	    fclose(fid);
    end
else
    for a = 1:numberoffactor
	    datafactor = deblank(analysisfactor(a, :));
	    fid = fopen(strcat(datafactor, '.txt'), 'w');
	    fprintf(fid, strcat(datafactor, ' genotype\n'));
	    fclose(fid);
    end
end
%------------------ Step 3: data collection --------------------
while listorder <= numberofgenotypes 

	% valiables named with data types are prepared and reset as null for strage of each data.
	for a = 1:numberoffactor
		datafactor = deblank(analysisfactor(a, :));
		% To command string as 'command', function 'eval' is used. 
		% Readability of code meight be impaired by this trick, 
		% but maintainability and ease of appending new analysis factor would be improved.
		% The following is doing like this
		% widthvector =[];
		eval(strcat(datafactor,'vector = []'));
	end

	% 'genotype' valiable having name of genotype, such as wt, et. 
	% and size(dir)) detecting how many pics there are in this directry
	genotype = deblank(genotypes(listorder, :));
	[picturesnum,a] = size(dir([genotype,'-*',extension]));

	for serialnumbernum = 1:picturesnum
		
		% This is changing the scalar to the string.
		serialnumberstrings = dec2base (serialnumbernum, 10);
		% make imagename which is passed to actual analysis program. above is for old. beneath is for new analyser.
		%imagename = [genotype, '-', serialnumberstrings, extension]
		imagename = [genotype, '-', serialnumberstrings]
		
		% calling punctaanalyser and let it analyse the picture defined above.
		%%%%%%%%%%%%%%%% You may change following function name for other analysis.
		[pcount, plineardensity, pdist, pwidths, pgaps, pintens, pvolumes, fixwidth, fixvol, fixgap,  fixwidthlineardensity, fixgaplineardensity]   = punctaanalyser (imagename, thresholdcoeff, fixthreshold, mode, objective)
		
		% Collect data from analyser. 
		% By this loop, correcting data and put them into each datastrage (widthvector, distancevector, etc.).
		for a = 1:numberoffactor
			datafactor = deblank(analysisfactor(a, :));
			valiable = deblank(correspondval(a,:));
			eval(strcat(datafactor,'vector = [', datafactor,'vector, ', valiable, ']'));
		end
		
	end
	
	%------------------ Step 4: Write (append) data to the output files.
	for a = 1:numberoffactor
		datafactor = deblank(analysisfactor(a, :));
		filename = strcat(datafactor, '.txt');
		row = 0;
		column = 0;
		[row,column] = size(eval(strcat(datafactor, 'vector')));
		fid = fopen(eval('filename'), 'a');
		if (ispc)
			for datacount = 1:column
				fprintf(fid, ' %f %s\r\n', eval(strcat(datafactor,'vector(1,datacount)')), genotype);
			end
				fclose(fid);
			else
			for datacount = 1:column
				fprintf(fid, ' %f %s\n', eval(strcat(datafactor,'vector(1,datacount)')), genotype);
			end
			fclose(fid);
		end
	end
listorder = listorder + 1;
end

%%%%%%%%%%%%% sub function hmsplit(handmade split)
function output = hmsplit(strings, sep)
sepposi = [];
[dummy, stringlength] = size(strings);
sepposi = [1, regexp(strings, sep) + 1, stringlength+2];
[dummy, factornum]=size(sepposi);
% Mat lab needs same # of columns.
maxchrnum = max(diff(sepposi))-1;
stuffstring = blanks(maxchrnum);
output = [stuffstring];
for i = 1:factornum-1
  addingstr =  [strings(sepposi(i):sepposi(i+1)-2),blanks(maxchrnum-(sepposi(i+1)-sepposi(i)-1))];
  output = [output;addingstr];
  addingstr = [];
end
output(1,:) = [];
%%end
