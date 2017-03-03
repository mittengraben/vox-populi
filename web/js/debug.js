var DEBUG = {
  init: function( scene ) {
    this.greenHelper = new THREE.ArrowHelper( new THREE.Vector3( 0, 1, 0 ), new THREE.Vector3( 0, 0, 0 ), 1.5, 0x00ff00 );
    this.redHelper = new THREE.ArrowHelper( new THREE.Vector3( 1, 0, 0 ), new THREE.Vector3( 0, 0, 0 ), 1.5, 0xff0000 );
    this.yellowHelper = new THREE.ArrowHelper( new THREE.Vector3( 0, 0, 1 ), new THREE.Vector3( 0, 0, 0 ), 1.5, 0xffff00 );

    scene.add( this.greenHelper );
    scene.add( this.redHelper );
    scene.add( this.yellowHelper );
  }
}
