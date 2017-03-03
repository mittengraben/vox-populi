var INPUT = {
  init: function() {
    inpObj = this;
    this.currentPos = new THREE.Vector2();
    this.drag = false;
    this.oldPos = new THREE.Vector2();
    this.zoom = 0;

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
      inpObj._fromEvent( evt );
    } );

    document.addEventListener( 'wheel', function( evt ) {
      evt.preventDefault();
      inpObj.zoom = evt.deltaY;
    } );

    document.addEventListener( 'touchstart', function( evt ) {
      evt.preventDefault();
      if ( evt.touches.length > 0 ) {
          inpObj._fromEvent( evt.touches[0] );
          inpObj.drag = true;
          inpObj.oldPos.copy( inpObj.currentPos );
      };
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
      if ( evt.touches.length > 0 ) {
          inpObj._fromEvent( evt.touches[0] );
      };
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

  zoomDelta: function() {
    var delta = this.zoom;
    this.zoom = 0;
    return delta;
  },

  _fromEvent: function( src ) {
    this.currentPos.x = ( src.clientX / window.innerWidth ) * 2 - 1;
    this.currentPos.y = - ( src.clientY / window.innerHeight ) * 2 + 1;
  }
}

INPUT.init()
