% training the matrix for 2 DOFs: open/close and pronate/supinate

close all;
clc;
clear all;

load capturedData/set3;

elecData = elecData.' - 128; % centre amplitude on 0
Fs = 4808;

butterlo = lowOnButter();
elecData = filter(butterlo,elecData);

wo = 60/(Fs/2); bw = wo/35;
[num,den] = iirnotch(wo,bw);

for i = 2:6 % generate comb filter to remove mains hum
    wo = i*60/(Fs/2); bw = wo/35; % need to remove 60 Hz and higher harmonics
    [b,a] = iirnotch(wo,bw);
    num = conv(num,b);
    den = conv(den,a);
end

% padLength = 32*ceil(length(elecData)/32) - length(elecData);
% elecData = [elecData; zeros(16,8)];
% zif = zeros(1,12);
% test = zeros(size(elecData));
% 
% for i = 1:32:length(elecData) % just testing I guess...
%     sample = elecData(i:i+31,:);
%     [y, zif] = filter(num,den,sample,zif);
%     test(i:i+31,:) = y;
% end

% elecData = test;

elecData = filtfilt(num,den,elecData);

elecData = elecData.^2;

windowLen = round(0.5*Fs);
window = ones(1,windowLen)/windowLen;
smoothedData = filter(window,1,elecData);

timeStart = ((0:9:45) + 8)*Fs;
timeEnd = timeStart + 3*Fs;

L = 8; % number of channels
N = 4; % number of synergies
Ob = length(elecData); % number of observations

% baseline
relaxedData = smoothedData(timeStart(1):timeEnd(1),:);
baselines = mean(relaxedData);
maxs = [0 0 0 0 0 0 0 0];

for i = 1:8
    smoothedData(:,i) = smoothedData(:,i) - baselines(i);
    maxs(i) = max(smoothedData(:,i));
    smoothedData(:,i) = smoothedData(:,i)/max(smoothedData(:,i));
end

% first DOF
openData = smoothedData(timeStart(2):timeEnd(2),:).';
closeData = smoothedData(timeStart(3):timeEnd(3),:).';

% second DOF
proData = smoothedData(timeStart(4):timeEnd(4),:).';
soupData = smoothedData(timeStart(5):timeEnd(5),:).';

[W1,H1] = nnmf(openData,1,'algorithm','mult');  % assuming all but one channels of H are inactive
[W2,H2] = nnmf(closeData,1,'algorithm','mult'); % this totally works, okay?
[W3,H3] = nnmf(proData,1,'algorithm','mult');
[W4,H4] = nnmf(soupData,1,'algorithm','mult');

H = [H1;H2;H3;H4];
maxes = max(H.');
W = [W1*maxes(1),W2*maxes(2),W3*maxes(3),W4*maxes(4)];  % is this it? did I win?

load capturedData/set2; % cross validation set, loaded in as elecData

elecData = elecData.' - 128; % centre amplitude on 0
elecData = filter(butterlo,elecData);

for i = 1:6 % comb filter? get rid of that mains hum...
    wo = i*60/(Fs/2); bw = wo/35; % notch filter to remove 60Hz noise
    [b,a] = iirnotch(wo,bw);

    elecData = filtfilt(b,a,elecData);
end

elecData = elecData.^2;
windowLen = round(0.1*Fs);
% window = blackmanharris(windowLen);
% smoothedData = filter(window,1,elecData);

Hd = myfilter();
smoothedData = filter(Hd,elecData);

% % baseline
% relaxedData = smoothedData(timeStart(1):timeEnd(1),:);
% baselines = mean(relaxedData);

for i = 1:8
    smoothedData(:,i) = smoothedData(:,i) - baselines(i);
    smoothedData(:,i) = smoothedData(:,i)/maxs(i);

end

F = smoothedData/W.';

F(F<0) = 0;

