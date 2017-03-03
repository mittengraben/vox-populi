var VIEWER = {
  init: function( camera, renderer ) {
    this.camera = camera;
    this.renderer = renderer;

    this.inertia = {
      axis: new THREE.Vector3(),
      angle: 0.0,
      damping: 0.95,
      targetDistance: 1.8,
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
    var delta = INPUT.zoomDelta();
    var worldSphere = WORLD.boundingSphere;
    var eye = this.camera.position.clone().sub( worldSphere.center );

    if ( Math.abs(delta) > 0 ) {
        this.inertia.distanceAnimation = 0.0;
        this.inertia.targetDistance = eye.length() * ( 1 + delta * 0.001 );
        if ( this.inertia.targetDistance < 1.1 ) {
          this.inertia.targetDistance = 1.1;
        };
        if ( this.inertia.targetDistance > 2 ) {
          this.inertia.targetDistance = 2;
        };
    };

    if ( this.inertia.distanceAnimation < 1.0 ) {
      var targetEye = eye.clone().normalize().multiplyScalar( this.inertia.targetDistance );
      eye.lerp( targetEye, this.inertia.distanceAnimation );
      this.inertia.distanceAnimation += dt / 0.2;
      this.camera.position.copy( worldSphere.center ).add( eye );
    };
  },

  update: function( dt ) {
    this.applyRotation( dt );
    this.applyZoom( dt );
    this.camera.updateProjectionMatrix();
  }
}
