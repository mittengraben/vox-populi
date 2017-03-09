var VIEWER = {
  init: function( camera, renderer ) {
    this.camera = camera;
    this.renderer = renderer;

    this.inertia = {
      axis: new THREE.Vector3(),
      angle: 0.0,
      damping: 0.95,
      targetDistance: CONFIG.zoom1Distance,
      distanceAnimation: 0.0
    };

    window.addEventListener( 'resize', function() {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize( window.innerWidth, window.innerHeight );
    } );

  },

  applyRotation: function( dt ) {
    var delta = INPUT.dragDelta();
    var axis = this.inertia.axis;
    var angle = this.inertia.angle;

    var worldSphere = WORLD.boundingSphere;

    if ( delta === null ) {
        if ( angle < 0.0000001 ) {
          return;
        }

        this.inertia.angle = angle * this.inertia.damping;
    } else {
      var newPointDir = new THREE.Vector3( INPUT.currentPos.x, INPUT.currentPos.y, 0.5 );
      var oldPointDir = new THREE.Vector3( INPUT.currentPos.x - delta.x, INPUT.currentPos.y - delta.y, 0.5 );

      newPointDir.unproject( this.camera );
      oldPointDir.unproject( this.camera );

      newPointDir.subVectors( newPointDir, this.camera.position ).normalize();
      oldPointDir.subVectors( oldPointDir, this.camera.position ).normalize();

      newIntersect = new THREE.Ray( this.camera.position, newPointDir ).intersectSphere( worldSphere );
      oldIntersect = new THREE.Ray( this.camera.position, oldPointDir ).intersectSphere( worldSphere );

      if ( null !== newIntersect && null !== oldIntersect ) {
        axis = new THREE.Vector3();
        axis.crossVectors( newIntersect.sub( worldSphere.center ), oldIntersect.sub( worldSphere.center ) ).normalize();

        angle = newIntersect.angleTo( oldIntersect );

        this.inertia.axis = axis;
        if ( Math.abs( angle ) > Math.abs( this.inertia.angle ) ) {
          this.inertia.angle = angle;
        };
      };
    };

    var eye = this.camera.position.clone().sub( worldSphere.center );
    var distance = eye.length();
    eye.applyAxisAngle( axis, -angle ).normalize();

    this.camera.position.copy( worldSphere.center ).add( eye.multiplyScalar( distance ) );
    this.camera.up.applyAxisAngle( axis, -angle ).normalize();

    this.camera.lookAt( worldSphere.center );
  },

  applyZoom: function( dt ) {
    var worldSphere = WORLD.boundingSphere;
    var eye = this.camera.position.clone().sub( worldSphere.center );
    this.inertia.targetDistance = CONFIG.zoom1Distance * INPUT.zoom;

    var targetEye = eye.clone().normalize().multiplyScalar( this.inertia.targetDistance );
    this.camera.position.copy( worldSphere.center ).add( targetEye );
  },

  update: function( dt ) {
    this.applyRotation( dt );
    this.applyZoom( dt );
    this.camera.updateProjectionMatrix();
  }
}
