# calculate one step of Kalman filter by parameters of model;
# model is: x = Fx + w(Q), y = Hx + v(R)
function [x, P] = kf_step(x0, P0, F, Q, y, H, R)
  # size assertions
  assert(size(x0)(1)==size(F)(2));
  assert(size(x0)(2)==1);
  assert(size(F)(1)==size(F)(2));
  assert(size(Q)(1)==size(Q)(2));
  assert(size(F)(1)==size(Q)(2));
  assert(size(y)(1)==size(H)(1));
  assert(size(y)(2)==1);
  assert(size(H)(2)==size(x0)(1));
  assert(size(R)(1)==size(R)(2));
  assert(size(R)(1)==size(y)(1));
  # calculate
  xe = F*x0;
  Pe = F*P0*F' + Q;
  dy = y - H*xe;
  G = Pe*H'*inv(H*Pe*H' + R);
  x = xe + G*dy;
  P = (eye(size(x0)(1)) - G*H)*Pe;
endfunction
