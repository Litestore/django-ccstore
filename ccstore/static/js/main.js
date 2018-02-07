$(function () {
    // Websocket
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var sock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/ws/");
    sock.onopen = function() {
        console.log("Connected!");
    };
    sock.onmessage = function(message) {
        var data = JSON.parse(message.data);
        if (data.msg_type == "ticker") {
            var ticker = data.ticker;
            var price = ticker[settings.DEFAULT_COIN][settings.DEFAULT_CURRENCY];
            $('.coin-price').text(price);
        };
    };
    // Misc
    var clipboard = new Clipboard('.btn-copy');
    clipboard.on('success', function(e) {
        console.log(e);
    });
    clipboard.on('error', function(e) {
        console.log(e);
    });
});