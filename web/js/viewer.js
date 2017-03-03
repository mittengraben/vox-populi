var VIEWER = {
  init: function( camera, renderer ) {
    this.camera = camera;
    this.renderer = renderer;

    this.inertia = {
      oldAxis: new THREE.Vector3(),
      angle: 0.0,
      damping: 1.0
    };

    window.addEventListener( 'resize', function() {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize( window.innerWidth, window.innerHeight );
    } );

  },

  update: function( dt ) {
    var delta = INPUT.dragDelta();
    if ( delta === null || delta.lengthSq() == 0 ) {
        return;
    };

    var newPointDir = new THREE.Vector3( INPUT.currentPos.x, INPUT.currentPos.y, 0.5 );
    var oldPointDir = new THREE.Vector3( INPUT.currentPos.x - delta.x, INPUT.currentPos.y - delta.y, 0.5 );

    newPointDir.unproject( this.camera );
    oldPointDir.unproject( this.camera );

    newPointDir.subVectors( newPointDir, this.camera.position ).normalize();
    oldPointDir.subVectors( oldPointDir, this.camera.position ).normalize();

    var worldSphere = WORLD.boundingSphere;

    newIntersect = new THREE.Ray( this.camera.position, newPointDir ).intersectSphere( worldSphere );
    if ( null === newIntersect ) return;

    oldIntersect = new THREE.Ray( this.camera.position, oldPointDir ).intersectSphere( worldSphere );
    if ( null === oldIntersect ) return;

    var axis = new THREE.Vector3();
    axis.crossVectors( newIntersect.sub( worldSphere.center ), oldIntersect.sub( worldSphere.center ) ).normalize();

    var eye = this.camera.position.clone().sub( worldSphere.center );
    var angle = newIntersect.angleTo( oldIntersect );
    eye.applyAxisAngle( axis, -angle );

    this.camera.position.copy( worldSphere.center ).add( eye );
    this.camera.up.applyAxisAngle( axis, -angle ).normalize();

    this.camera.lookAt( worldSphere.center );
    this.camera.updateProjectionMatrix();
  }
}
