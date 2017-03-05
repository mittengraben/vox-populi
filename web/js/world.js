var WORLD = {
  init: function( scene ) {
    this.boundingSphere = new THREE.Sphere( new THREE.Vector3(0, 0, 0), 1 );
    this.scene = scene;
    this.world = null;
  },

  setGeometry: function( data ) {
      if ( this.world !== null ) {
        this.scene.remove( this.world );
      }

      var geometry = new THREE.BufferGeometry();
      geometry.setIndex( new THREE.BufferAttribute( new Uint32Array( data.indicies ), 1 ) );
      geometry.addAttribute( 'position', new THREE.BufferAttribute( new Float32Array( data.position ), 3 ) );
      var material = new THREE.MeshBasicMaterial( { color: 0x0000ff } );
      this.world = new THREE.LineSegments( new THREE.WireframeGeometry( geometry ) );
      scene.add( this.world );
  }
}
