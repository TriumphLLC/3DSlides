var m_anim   = b4w.require("animation");
var m_app    = b4w.require("app");
var m_cam    = b4w.require("camera");
var m_cfg    = b4w.require("config");
var m_cont   = b4w.require("container");
var m_cons   = b4w.require("constraints");
var m_ctl    = b4w.require("controls");
var m_data   = b4w.require("data");
var m_math   = b4w.require("math");
var m_obj    = b4w.require("objects");
var m_phy    = b4w.require("physics");
var m_quat   = b4w.require("quat");
var m_scenes = b4w.require("scenes");
var m_trans  = b4w.require("transform");
var m_tsr    = b4w.require("tsr");
var m_util   = b4w.require("util");
var m_vec3   = b4w.require("vec3");
var m_material  = b4w.require("material");
var m_logic_nodes = b4w.require("logic_nodes");
count = 0
var scene = m_scenes.get_active()
var goods = []                   
var current_object, max_shelf;
var startx,starty;
var postfix = "a_Entry";

/*
Touch Events Support for 3D Slides
for eneble call init_logic
after init in your b4w application

*/

function init_logic() { 

window.addEventListener('touchstart', function(e){
 	 	m_app.disable_camera_controls()
        var touchobj = e.changedTouches[0] 
        startx = parseInt(touchobj.clientX) 
        starty = parseInt(touchobj.clientY) 
     
    }, false);

window.addEventListener('touchend', function(e){
 	m_app.enable_camera_controls()
    var touchobj = e.changedTouches[0] 
    dist = parseInt(touchobj.clientX) - startx;
    distY = parseInt(touchobj.clientY) - starty;

    if(dist > 60) {
        right()
    } else if(dist < -60) {
       left()
    } else if(distY > 60) {
         up()
    } else if(distY < -60) {
          down()
    }

}, false);

	goods = m_scenes.get_all_objects().filter(function(e) { return e.name.split('_')[0] == 'product' && e.name.split('_').length == 4} ).reverse();

	
	var max = goods[goods.length -1].name
	var min = goods[0].name
	max_shelf = max.split('_')[2] 
	

	 var controllerOptions = { enableGestures: true };

        /* LEAP MOTION SUPPORT
            Create object Gesture
        */
//        var gestureObj = new Gesture();

        /*
            Function frame callback
        */
//         Leap.loop(controllerOptions, function(frame){
//             gestureObj.definitionGestures(frame);
//             switch(gestureObj.gesture){
//                 case "RIGTH":
//                     // console.log("gestureObj.gesture",gestureObj.gesture)
//                     right()
//                     break;
//                 case "LEFT":
//                      // console.log("gestureObj.gesture",gestureObj.gesture)
//                     left()
//                     break;
//                 case "TOP":
//                     // console.log("gestureObj.gesture",gestureObj.gesture)
//                     up()
//                     break;
//                 case "BOTTOM":
//                      // console.log("gestureObj.gesture",gestureObj.gesture)
//                     down()
//                     break;
//                 case "CLICK":
//                    // console.log("gestureObj.gesture",gestureObj.gesture)
//                     break;
//                 default:
//                 	// console.log("gestureObj.gesture",gestureObj.gesture)
//                 	break;    
//             };
//         });

// right()


}

function shelf_count() {
	var count;
	if(typeof(current_object) != "undefined") {
		var current_shelf_num = current_object.name.split('_')[2]
		var goods_on_shelf = goods.filter(function(e) { return e.name.split("_")[2] == current_shelf_num})
		count = goods_on_shelf.length
	}
	else {
		var current_shelf_num = goods[0].name.split('_')[2]
		var goods_on_shelf = goods.filter(function(e) { return e.name.split("_")[2] == current_shelf_num})
		count = goods_on_shelf.length
	}
	return count	
}


function left() {

if(count > 0) {
	count--
	var ob = goods[count]
	var scene = m_scenes.get_active()
	current_object = ob;
	m_logic_nodes.run_entrypoint(scene, "goods_logic_" + ob.name + postfix)
}
else if(count == 0) {
	count--
	current_object = undefined;
	var scene = m_scenes.get_active()
	m_logic_nodes.run_entrypoint(scene, "goods_logic_0")
}
else {
	count = goods.length - 1
	var ob = goods[count]
	var scene = m_scenes.get_active()
	current_object = ob;
	m_logic_nodes.run_entrypoint(scene, "goods_logic_" + ob.name + postfix)
}

}

function right() {
	
	
	if(count < goods.length-1) {
	count++
	var ob = goods[count]
	
	var scene = m_scenes.get_active()
	current_object = ob;
	m_logic_nodes.run_entrypoint(scene, "goods_logic_" + ob.name + postfix)
}
else if (count == goods.length-1) {
	count++
	current_object = undefined;
	var scene = m_scenes.get_active()
	m_logic_nodes.run_entrypoint(scene, "goods_logic_0")
}
else {
	count = 0
	var ob = goods[count]
	var scene = m_scenes.get_active()
	current_object = ob;
	m_logic_nodes.run_entrypoint(scene, "goods_logic_" + ob.name + postfix)	
}

	
}

function up() {

	if(typeof(current_object) == "undefined") {
	var current_pos = goods[0].name.split('_')[2]
	}
	else {
	var current_pos = current_object.name.split('_')[2]
	}
	
	
	if(parseInt(current_pos) < max_shelf) {
		count=shelf_count()
		var ob = goods.filter(function(e) { return e.name.split('_')[2] == String(parseInt(current_pos) + 1) && e.name.split('_')[3] == '1'})[0]
		console.log("ob",ob)
		var scene = m_scenes.get_active()
		current_object = ob;
		m_logic_nodes.run_entrypoint(scene, "goods_logic_" + ob.name + postfix)
	}
	else {
			current_object = undefined;
			var scene = m_scenes.get_active()
			m_logic_nodes.run_entrypoint(scene, "goods_logic_0")
	}
	
}

function down() {
	
	if(typeof(current_object) == "undefined") {
	var current_pos = goods[0].name.split('_')[2]
	var current_num = 1
	}
	else {
	var current_pos = current_object.name.split('_')[2]
	
	var current_num = current_object.name.split('_')[current_object.name.split('_').length -1]
	}
	if(parseInt(current_pos) > 1) {
		
		var ob = goods.filter(function(e) { return e.name.split('_')[2] == String(parseInt(current_pos) - 1) && e.name.split('_')[3] == '1'})[0]
		
		var delta =  parseInt(ob.name.split("_")[current_object.name.split('_').length -1]) - parseInt(current_num)
		var scene = m_scenes.get_active()
		current_object = ob;
		
		count-=shelf_count()- delta
		
		m_logic_nodes.run_entrypoint(scene, "goods_logic_" + ob.name + postfix)
	}
	else {
			current_object = undefined;
				var scene = m_scenes.get_active()
			m_logic_nodes.run_entrypoint(scene, "goods_logic_0")
	}

}