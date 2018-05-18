close all;
clc;
clear all;

load capturedData/set2;
elecData = elecData.' - 128; % centre amplitude on 0
Fs = 4808;

for i = 1:6 % comb filter? get rid of that mains hum...
    wo = i*60/(Fs/2); bw = wo/35; % notch filter to remove 60Hz noise
    [b,a] = iirnotch(wo,bw);

    elecData = filtfilt(b,a,elecData);
end

d = designfilt('bandpassfir',...
    'FilterOrder',20,...
    'CutoffFrequency1',10,...
    'CutoffFrequency2',300,...
    'SampleRate',Fs);
% fvtool(d,'Fs',Fs);
elecData = abs(filtfilt(d,elecData));

N = 8; % number of channels
K = 4; % number of synergies
Ob = length(elecData); % number of observations

window = rectwin(round(0.2*Fs));

dat = conv2(elecData,window,'same');

% signalAnalyzer(data,'SampleRate',Fs);