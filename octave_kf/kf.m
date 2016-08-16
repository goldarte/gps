# process data by Kalman filter
function x_res = kf(x0, p0, y, F, Q, H, R)
  num_states = size(x0)(1)
  num_meas_values = size(y)(2)
  num_steps = size(y)(1)
  x_res = zeros(num_steps, num_states);
  x_res(1,:) = x0';
  p_r = p0;
  for i=2:num_steps
    [x_r,p_r] = kf_step(x_res(i-1,:)', p_r, F, Q, y(i,:)', H, R);
    x_res(i,:) = x_r';
  endfor
endfunction

