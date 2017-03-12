var CONFIG = {
  socketServer: 'wss://{{ target }}:{{ websock_port }}',
  reconnectTimeout: 3000,
  debug: {{ debug }},
  minZoom: 0.6,
  maxZoom: 1.1,
  zoom1Distance: 1.8,
  version: [0, 3, 0],
  frameTime: 1 / 30.0,
  clickLag: 10,
}
