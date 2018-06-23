function nm = normc_fcn(m)
nm = sqrt(m.^2 ./ sum(m.^2)) .* sign(m);
end

% from https://www.mathworks.com/matlabcentral/answers/372602-normalizing-columns-does-my-function-do-the-same-as-normc