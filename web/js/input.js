var INPUT = {
  init: function() {
    inpObj = this;
    this.currentPos = new THREE.Vector2();
    this.drag = false;
    this.oldPos = new THREE.Vector2();
    this.touchDist = 0.0;
    this.zoom = 1.0;

    document.addEventListener( 'mousedown', function( evt ) {
      evt.preventDefault();
      inpObj.drag = true;
      inpObj.oldPos.copy( inpObj.currentPos );
    } );

    document.addEventListener( 'mouseup', function( evt ) {
      evt.preventDefault();
      inpObj.drag = false;
    } );

    document.addEventListener( 'mousemove', function( evt ) {
      evt.preventDefault();
      inpObj._fromEvent( evt, inpObj.currentPos );
    } );

    document.addEventListener( 'wheel', function( evt ) {
      evt.preventDefault();
      inpObj.zoom = inpObj.zoom + evt.deltaY * 0.001;
      inpObj._clampZoom()
    } );

    document.addEventListener( 'touchstart', function( evt ) {
      evt.preventDefault();
      if ( evt.touches.length == 1 ) {
          inpObj._fromEvent( evt.touches[0], inpObj.currentPos );
          inpObj.drag = true;
          inpObj.oldPos.copy( inpObj.currentPos );
      };
      if ( evt.touches.length == 2 ) {
          inpObj.drag = false;
          var tp = [ new THREE.Vector2(), new THREE.Vector2() ]
          for ( var i = 0; i < 2; i++ ) {
            inpObj._fromEvent( evt.touches[i], tp[i] );
          };
          inpObj.touchDist = tp[0].distanceTo( tp[1] );
      }
    } );

    document.addEventListener( 'touchend', function( evt ) {
      evt.preventDefault();
      inpObj.drag = false;
    } );

    document.addEventListener( 'touchcancel', function( evt ) {
      evt.preventDefault();
      inpObj.drag = false;
    } );

    document.addEventListener( 'touchmove', function( evt ) {
      evt.preventDefault();
      if ( evt.touches.length == 1 ) {
          inpObj._fromEvent( evt.touches[0], inpObj.currentPos );
      };
      if ( evt.touches.length == 2 ) {
        var tp = [ new THREE.Vector2(), new THREE.Vector2() ]
        for ( var i = 0; i < 2; i++ ) {
          inpObj._fromEvent( evt.touches[i], tp[i] );
        };
        var touchDist = tp[0].distanceTo( tp[1] );
        inpObj.zoom = inpObj.zoom * (inpObj.touchDist / touchDist);
        inpObj._clampZoom();
        inpObj.touchDist = touchDist;
      }
    } );
  },

  dragDelta: function() {
    if ( ! this.drag ) {
      return null;
    };
    var delta = new THREE.Vector2();
    delta.subVectors( this.oldPos, this.currentPos );
    this.oldPos.copy( this.currentPos );
    return delta;
  },

  _clampZoom: function() {
    if ( this.zoom < 0.6 ) this.zoom = 0.6;
    if ( this.zoom > 1.1 ) this.zoom = 1.1;
  },

  _fromEvent: function( src, target ) {
    target.x = ( src.clientX / window.innerWidth ) * 2 - 1;
    target.y = - ( src.clientY / window.innerHeight ) * 2 + 1;
  }
}

INPUT.init()
