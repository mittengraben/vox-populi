var WORLD = {
  init: function( scene ) {
    this.boundingSphere = new THREE.Sphere( new THREE.Vector3(0, 0, 0), 1 );
    this.scene = scene;
    this.pointBuffer = null;
    this.world = null;
    this.hexMesh = null;
    this.borderMesh = null;

    this.selectionMesh = null;
    this.territoryBorderMesh = null;

    this.tileMap = null;
    this.regionMap = null;

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

      var materials = [
        new THREE.MeshBasicMaterial( {
          color: 0x333333, transparent: true, opacity: 0.8,
          polygonOffset: true,
          polygonOffsetFactor: 1.0,
          polygonOffsetUnits: 1.0,
        } ),
        new THREE.MeshPhongMaterial( {
          color: 0xa0c409,
          polygonOffset: true,
          polygonOffsetFactor: 1.0,
          polygonOffsetUnits: 1.0,
          shading: THREE.FlatShading,
          side: THREE.DoubleSide
        } )
      ]

      var geometry = new THREE.BufferGeometry();

      this.pointBuffer = new THREE.BufferAttribute( new Float32Array( data.position ), 3 );
      geometry.setIndex( new THREE.BufferAttribute( new Uint32Array( data.indicies ), 1 ) );
      geometry.addAttribute( 'position', this.pointBuffer );
      geometry.addAttribute( 'normal', this.pointBuffer );
      geometry.addGroup( 0, 6600, 0 );
      geometry.addGroup( 6600, data.indicies.length - 6600, 1 );
      this.world = new THREE.Mesh(
        geometry,
        new THREE.MultiMaterial( materials )
      );

      geometry = new THREE.BufferGeometry();
      geometry.setIndex( new THREE.BufferAttribute( new Uint32Array( data.mesh ), 1 ) );
      geometry.addAttribute( 'position', this.pointBuffer );
      this.hexMesh = new THREE.LineSegments( geometry, new THREE.LineBasicMaterial( { color: 0x365023 } ) );

      geometry = new THREE.BufferGeometry();
      geometry.setIndex( new THREE.BufferAttribute( new Uint32Array( data.bordermesh ), 1 ) );
      geometry.addAttribute( 'position', this.pointBuffer );
      this.borderMesh = new THREE.LineSegments( geometry, new THREE.LineBasicMaterial( { color: 0xffffff } ) );

      this.scene.add( this.world );
      this.scene.add( this.hexMesh );
      this.scene.add( this.borderMesh );

      this.directionalLight.target = this.world;
  },

  setTilemap: function( data ) {
    this.tileMap = data.tilemap;
  },

  setRegionmap: function( data ) {
    this.regionMap = data.regionmap;
  },

  setTerritoryBorder: function( data ) {
    if ( this.territoryBorderMesh !== null ) {
      this.scene.remove( this.territoryBorderMesh );
    }

    var geometry = new THREE.BufferGeometry();

    position = new THREE.BufferAttribute( new Float32Array( data.position ), 3 );
    geometry.setIndex( new THREE.BufferAttribute( new Uint32Array( data.indicies ), 1 ) );
    geometry.addAttribute( 'position', position );
    geometry.computeBoundingSphere();
    this.territoryBorderMesh = new THREE.Mesh(
      geometry,
      new THREE.MeshBasicMaterial( {
        color: 0xff0000, transparent: true, opacity: 0.3
      } )
    );
    this.territoryBorderMesh.drawMode = THREE.TriangleStripDrawMode;

    this.scene.add( this.territoryBorderMesh );
    VIEWER.centerOn( geometry.boundingSphere.center );
  },

  pickTile: function( raycaster ) {
    if ( this.world === null ) return;
    if ( this.tileMap === null ) return;
    if ( this.regionMap === null ) return;

    intersections = raycaster.intersectObject( this.world );
    if ( intersections.length < 1 ) return;

    faceIndex = intersections[0].faceIndex;
    var tileIndex = 0;
    if ( faceIndex < 5 * 12 ) {
      tileIndex = faceIndex / 5 | 0;
    } else {
      tileIndex = ((faceIndex - 5 * 12) / 6 | 0) + 12;
    };

    tile = this.tileMap[tileIndex];

    if ( this.selectionMesh !== null ) {
      this.scene.remove( this.selectionMesh );
    }

    var geometry = new THREE.BufferGeometry();
    var loop = tile.vertices.slice();
    loop.push( tile.vertices[0] );
    geometry.setIndex( new THREE.BufferAttribute( new Uint32Array( loop ), 1 ) );
    geometry.addAttribute( 'position', this.pointBuffer );
    this.selectionMesh = new THREE.Line( geometry, new THREE.LineBasicMaterial( { color: 0xff0000 } ) );
    this.scene.add( this.selectionMesh );
  },

  update: function() {
    var targetVec = new THREE.Vector3();
    targetVec.subVectors( this.directionalLight.position, this.boundingSphere.center );
    targetVec.applyAxisAngle( new THREE.Vector3( 1, 0, 0 ), 0.1 * CONFIG.frameTime );
    this.directionalLight.position.copy( this.boundingSphere.center ).add( targetVec );
  }
}
