addpath('./octave_kf');

# functions for data merging

function sec = time_to_seconds(tms)
  sec = int32(tms(:,3) + tms(:,2)*60 + tms(:,1)*3600);
endfunction

function tms = seconds_to_time(tsec)
  hours = idivide(int32(tsec), int32(3600), 'floor');
  minsec = int32(tsec - hours*3600);
  mins = idivide(int32(minsec), int32(60), 'floor');
  sec = int32(minsec - mins*60);
  tms = [hours mins sec];
endfunction

function [cdata1, cdata2] = merge_data_by_time(data1, data2)
  sec1 = time_to_seconds(data1(:,6:8));
  sec2 = time_to_seconds(data2(:,6:8));
  sec_inters = intersect(sec1, sec2);
  ismember1 = ismember(sec1, sec_inters);
  ismember2 = ismember(sec2, sec_inters);
  new_len = sum(ismember1);
  assert(new_len==sum(ismember2));
  cdata1 = zeros(new_len, size(data1)(2));
  curr = 1;
  for i = 1:size(data1)(1)
    if ismember1(i)==1
      cdata1(curr,:) = data1(i,:);
      curr += 1;
    endif
  endfor
  cdata2 = zeros(new_len, size(data2)(2));
  curr = 1;
  for i = 1:size(data2)(1)
    if ismember2(i)==1
      cdata2(curr,:) = data2(i,:);
      curr += 1;
    endif
  endfor
endfunction

# precision estimation
function [p_res, mean_est, std_est] = estimate_point(data, markup, point_val)
  is_point = (markup==point_val);
  num_groups = 0;
  # find number of subgroups
  if is_point(1) == 1
    num_groups += 1;
  endif
  for i = 1:length(is_point)-1
    if is_point(i)==0 && is_point(i+1)==1
      num_groups += 1;
    endif
  endfor
  # find starts and ends of the subgroups
  starts = zeros(num_groups, 1);
  ends = zeros(num_groups, 1);
  curr_sg = 1;
  if is_point(1) == 1
    starts(curr_sg) = 1;
  endif
  for i = 1:length(is_point)-1
    if is_point(i)==0 && is_point(i+1)==1
      starts(curr_sg) = i;
    endif
    if is_point(i)==1 && is_point(i+1)==0
      ends(curr_sg) = i;
      curr_sg += 1;
    endif
  endfor
  if is_point(length(is_point)) == 1
    ends(curr_sg) = length(is_point);
  endif
  # estimate each subgroup
  p_res = zeros(num_groups, 2);
  for i=1:num_groups
    p_res(i,:) = mean(data(starts(i):ends(i), :));
  endfor
  mean_est = min(p_res);
  std_est = std(p_res);
endfunction

function [uv, means, stds] = estimate_all_points(data, markup)
  uv = unique(markup);
  # drop free points
  uv = setdiff(sort(uv), [-1]);
  means = zeros(length(uv), 2);
  stds = zeros(length(uv), 2);
  # calculate values for each point
  for i=1:length(uv)
    [p_res, mv, sds] = estimate_point(data, markup, uv(i));
    means(i,:) = mv;
    stds(i,:) = sds;
  endfor
endfunction

function plot_points(uv, means, stds)
  for i=1:size(means)(1)
    plot([means(i,2) means(i,2)], [means(i,1)-stds(i,1) means(i,1)+stds(i,1)], 'k');
    plot([means(i,2)-stds(i,2) means(i,2)+stds(i,2)], [means(i,1) means(i,1)], 'k');
    text(means(i,2), means(i,1), int2str(uv(i)), 'verticalalignment', 'top', 'fontsize', 20);
    text(means(i,2), means(i,1)+stds(i,1), num2str(stds(i,1), "%5.1f"), 'verticalalignment', 'bottom', 'horizontalalignment', 'left', 'fontsize', 16);
    text(means(i,2)-stds(i,2), means(i,1), num2str(stds(i,2), "%5.1f"), 'verticalalignment', 'bottom', 'horizontalalignment', 'right', 'fontsize', 16);
  endfor
endfunction

function newdata = postprocess_base(data, max_step_allowed)
  newdata = zeros(size(data)(1), size(data)(2));
  newdata(1,:) = data(1,:);
  curr_nd = 2;
  for i=2:size(data)(1)
    if (data(i,3)-data(i-1,3))^2 + (data(i,4)-data(i-1,4))^2 < max_step_allowed^2
      newdata(curr_nd,:) = data(i,:);
      curr_nd +=1;
    endif
  endfor
  newdata = newdata(1:curr_nd-1,:);
endfunction

# read the data from differential mode
logf_base = './120816_114033_BASE.csv';
logf_prt1 = './120816_114033_PRT1.csv';
logf_prt2 = './120816_114033_PRT2.csv';

#logf_base = './050816_131430_BASE.csv';
#logf_port = './050816_131430_PORT.csv';


data_base = dlmread(logf_base, sep = ';');
data_prt1 = dlmread(logf_prt1, sep = ';');
data_prt2 = dlmread(logf_prt2, sep = ';');

data_base = postprocess_base(data_base, 0.5);
data_prt1 = postprocess_base(data_prt1, 2);
data_prt2 = postprocess_base(data_prt2, 2);

base_pos = mean(data_base(:, 3:4));

hold on;
plot(data_prt1(:,4)-base_pos(2), data_prt1(:,3)-base_pos(1), 'rx'),
plot(data_prt2(:,4)-base_pos(2), data_prt2(:,3)-base_pos(1), 'kx'),
title ('Nonlinear filtering (raw data) for differential mode'),
xlabel('Longitude, m'),
ylabel('Latitude, m'),
axis('equal');
plot(data_base(:,4)-base_pos(2), data_base(:,3)-base_pos(1), 'bx');

# filter the data from differential mode
sigma_proc = 0.25;
sigma_meas = 30;
P0 = eye(2)*sigma_proc; 
F = eye(2);
Q = eye(2)*sigma_proc;
H = eye(2);
R = eye(2)*sigma_meas;

[mdata_prt2, mdata_base] = merge_data_by_time(data_prt2, data_base);
y = mdata_prt2(:,3:4)-mdata_base(:,3:4);
x0 = (mdata_prt2(1,3:4)-mdata_base(1,3:4))';
res_diff2 = kf(x0, P0, y, F, Q, H, R);
plot(res_diff2(:,2), res_diff2(:,1), 'g');

[uv, means, stds] = estimate_all_points(res_diff2, mdata_prt2(:,2));
plot_points(uv, means, stds);


# read the data from dual mode
logf_base_dual = './120816_115224_BASE.csv';
logf_prt1_dual = './120816_115224_PRT1.csv';
logf_prt2_dual = './120816_115224_PRT2.csv';


logf_base_dual = './120816_103425_BASE.csv';
logf_prt1_dual = './120816_103425_PRT1.csv';
logf_prt2_dual = './120816_103425_PRT2.csv';


data_base_dual = dlmread(logf_base_dual, sep = ';');
data_prt1_dual = dlmread(logf_prt1_dual, sep = ';');
data_prt2_dual = dlmread(logf_prt2_dual, sep = ';');



hold on;
plot(data_prt1_dual(:,4)-base_pos(2), data_prt1_dual(:,3)-base_pos(1), 'r');
plot(data_prt2_dual(:,4)-base_pos(2), data_prt2_dual(:,3)-base_pos(1), 'k');
title ('Trajectories for dual mode'),
xlabel('Longitude, m'),
ylabel('Latitude, m'),
axis('equal');
plot(data_base_dual(:,4)-base_pos(2), data_base_dual(:,3)-base_pos(1), 'b');

# filter the data from dual mode
sigma_proc = 1;
sigma_meas = 20;
x0 = [0;0];
P0 = eye(2)*sigma_proc; 
F = eye(2);
Q = eye(2)*sigma_proc;
H = [eye(2); eye(2); eye(2)];
R = eye(6)*sigma_meas;
[mdata_port, mdata_base] = merge_data_by_time(data_port_dual, data_base_dual);
y = [mdata_port(:,3:4)-base_pos mdata_base(:,3:4)-base_pos];
res_dual = kf(x0, P0, y, F, Q, H, R);
plot(res_dual(:,2), res_dual(:,1), 'g');
[uv, means, stds] = estimate_all_points(res_dual, mdata_port(:,2));
plot_points(uv, means, stds);



# find the best R value based on errors

logf_base = './120816_101621_BASE.csv';
data_base = dlmread(logf_base, sep = ';');
base_pos = mean(data_base(:, 3:4));

logf_base_dual = './120816_103425_BASE.csv';
logf_prt2_dual = './120816_103425_PRT2.csv';

data_base_dual = dlmread(logf_base_dual, sep = ';');
data_prt2_dual = dlmread(logf_prt2_dual, sep = ';');
[mdata_port, mdata_base] = merge_data_by_time(data_prt2_dual, data_base_dual);
mdata_port(:,3:4) -= base_pos;
mdata_base(:,3:4) -= base_pos;

SigmaNum = 200;
sigmas = linspace(0.2, 30, SigmaNum);
errors = zeros(1,length(sigmas));
for sigma_pos = 1:length(sigmas)
  sigma_proc = 10;
  sigma_meas = sigmas(sigma_pos);
  x0 = [0;0];
  P0 = eye(2)*sigma_proc; 
  F = eye(2);
  Q = eye(2)*sigma_proc;
  H = [eye(2); eye(2)];
  R = eye(4)*sigma_meas;
  y = [mdata_port(:,3:4) mdata_base(:,3:4)];
  res_dual = kf(x0, P0, y, F, Q, H, R);
  [uv, means, stds] = estimate_all_points(res_dual, mdata_port(:,2));
  errors(sigma_pos) = mean(stds(:,1)) + mean(stds(:,2));
endfor

plot(sigmas, errors);


