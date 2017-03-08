var CLIENT = {
  init: function() {
    _this = this;
    this.socket = null;
    this.statusDiv = document.getElementById('serv-status');

    this.dispatch = {
      open: function() {
        _this.send( { name: 'worldgeometry' } );
      },

      worldgeometry: function( data ) {
        WORLD.setGeometry( data );
      }
    }

    this.reconnect();
  },

  showStatus: function( text ) {
    this.statusDiv.innerHTML = text;
  },

  reconnect: function() {
    if ( this.socket !== null ) {
      if (
        this.socket.readyState === WebSocket.CONNECTING ||
        this.socket.readyState === WebSocket.OPEN
      ) {
        return;
      };
      this.socket.close();
    };
    this.showStatus( 'Reconnecting...' );

    this.socket = new WebSocket('wss://192.168.1.35:8888');
    this.socket.binaryType = 'arraybuffer';

    _this = this;

    this.socket.addEventListener('open', function ( event ) {
      _this.showStatus( 'Connected to ' + _this.socket.url );
      _this.dispatch.open();
    });

    this.socket.addEventListener('message', function ( event ) {
      response = msgpack.unpack( new Uint8Array( event.data ) );
      if ( _this.dispatch.hasOwnProperty( response.name ) ) {
        _this.dispatch[ response.name ]( response );
      } else {
        console.error('Unexpected response ' + JSON.stringify( response ));
      };
    });

    this.socket.addEventListener('error', function ( event ) {
      _this.showStatus( 'Error ' + event );
      console.error( event );
    });

    this.socket.addEventListener('close', function ( event ) {
      _this.showStatus( 'Closed');
      console.log( 'closed' );
      window.setTimeout( function() { _this.reconnect(); }, 3000 );
    });
  },

  send: function( data ) {
    this.socket.send( new Uint8Array( msgpack.pack( data ) ) );
  }
};

CLIENT.init()
