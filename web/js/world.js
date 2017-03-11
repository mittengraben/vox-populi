var WORLD = {
  init: function( scene ) {
    this.boundingSphere = new THREE.Sphere( new THREE.Vector3(0, 0, 0), 1 );
    this.scene = scene;
    this.pointBuffer = null;
    this.world = null;
    this.hexMesh = null;
    this.borderMesh = null;

    this.directionalLight = new THREE.DirectionalLight( 0xdddddd );
    this.directionalLight.position.set( 0, 0, 1 );

    scene.add( this.directionalLight );

    this.ambientLight = new THREE.AmbientLight( 0x404040 );
    scene.add( this.ambientLight );
  },

  setGeometry: function( data ) {
      if ( this.world !== null ) {
        this.scene.remove( this.world );
        this.scene.remove( this.hexMesh );
        this.scene.remove( this.borderMesh );
      }

      var geometry = new THREE.BufferGeometry();

      this.pointBuffer = new THREE.BufferAttribute( new Float32Array( data.position ), 3 );
      geometry.setIndex( new THREE.BufferAttribute( new Uint32Array( data.indicies ), 1 ) );
      geometry.addAttribute( 'position', this.pointBuffer );
      geometry.addAttribute( 'normal', this.pointBuffer );
      this.world = new THREE.Mesh(
        geometry,
        new THREE.MeshPhongMaterial( {
          color: 0xa0c409,
          polygonOffset: true,
          polygonOffsetFactor: 1.0,
          polygonOffsetUnits: 1.0,
          shading: THREE.FlatShading
        } )
      );

      geometry = new THREE.BufferGeometry();
      geometry.setIndex( new THREE.BufferAttribute( new Uint32Array( data.mesh ), 1 ) );
      geometry.addAttribute( 'position', this.pointBuffer );
      this.hexMesh = new THREE.LineSegments( geometry, new THREE.LineBasicMaterial( { color: 0x365023 } ) );

      geometry = new THREE.BufferGeometry();
      geometry.setIndex( new THREE.BufferAttribute( new Uint32Array( data.bordermesh ), 1 ) );
      geometry.addAttribute( 'position', this.pointBuffer );
      this.borderMesh = new THREE.LineSegments( geometry, new THREE.LineBasicMaterial( { color: 0xffffff } ) );

      scene.add( this.world );
      scene.add( this.hexMesh );
      scene.add( this.borderMesh );

      this.directionalLight.target = this.world;
  },

  update: function( dt ) {
    var targetVec = new THREE.Vector3();
    targetVec.subVectors( this.directionalLight.position, this.boundingSphere.center );
    targetVec.applyAxisAngle( new THREE.Vector3( 1, 0, 0 ), 0.1 * dt );
    this.directionalLight.position.copy( this.boundingSphere.center ).add( targetVec );
  }
}
