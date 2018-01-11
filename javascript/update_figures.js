// Check if our big images are available locally or remotely:
var big_data_output = "./../big_data_output";
var img = new Image();
img.onerror = function() {
  window.big_data_output = "https://amsikking.github.io/remote_refocus_data";
  img.onerror = function() {
	window.big_data_output = "https://andrewgyork.github.io/remote_refocus_data";
	img.onerror = ""
	img.src = big_data_output + "/Worm_DIC/poster.png"
}
  img.src = big_data_output + "/Worm_DIC/poster.png"
}
img.onload = function() {
  console.log("Loading interactive images from: " + big_data_output)
}
img.src = big_data_output + "/Worm_DIC/poster.png"

function update_figure_1() {
  var choice = document.getElementById("figure_1_choice").value;
  if ((choice === "DIC")){
  var filename = big_data_output + "/Worm_DIC/figure.mp4";
  var postername = big_data_output + "/Worm_DIC/poster.png";}
  if ((choice === "TLFL")){
  var filename = big_data_output + "/Worm_TL_FL/figure.mp4";
  var postername = big_data_output + "/Worm_TL_FL/poster.png";}  
  var vid = document.getElementById("Figure_1_vid");
  vid.src = filename;
  vid.poster = postername;
}

function update_figure_5() {
  var microscope = document.getElementById("figure_5_microscope").value;
  var RR = document.getElementById("figure_5_RR").value;
  var filename = big_data_output + "/SIM_target/img" + microscope + RR + ".png";
  var img = document.getElementById("Figure_5_png");
  img.src = filename;
}

function update_figure_6() {
  var fov = document.getElementById("figure_6_fov").value;
  var microscope = document.getElementById("figure_6_microscope").value;
  var RR = document.getElementById("figure_6_RR").value;
  var filename = big_data_output + "/" + fov + "/img" + microscope + RR + ".png";
  var img = document.getElementById("Figure_6_png");
  img.src = filename;
}

function update_figure_8() {
  var sample1 = document.getElementById("figure_8_sample_choice").value;
  if ((sample1 === "graticule")){
  var vid_a_filename = big_data_output + "/Graticule/figure.mp4";
  var postername_a = big_data_output + "/Graticule/poster.png";
  var img_a_filename = "./images/Samples/graticule.jpg";
  var vid_b_filename = big_data_output + "/uFchip/figure.mp4";
  var postername_b = big_data_output + "/uFchip/poster.png";
  var img_b_filename = "./images/Samples/uFchip.jpg";
  }
  if ((sample1 === "agarose")){
  var vid_a_filename = big_data_output + "/Agarose/figure.mp4";
  var postername_a = big_data_output + "/Agarose/poster.png";
  var img_a_filename = "./images/Samples/agarose.jpg";
  var vid_b_filename = big_data_output + "/Dish/figure.mp4";
  var postername_b = big_data_output + "/Agarose/poster.png";
  var img_b_filename = "./images/Samples/dish.jpg";
  }
  var vid_a = document.getElementById("Figure_8a_vid");
  var img_a = document.getElementById("Figure_8a_svg");
  var vid_b = document.getElementById("Figure_8b_vid");
  var img_b = document.getElementById("Figure_8b_svg");
  vid_a.src = vid_a_filename;
  vid_a.poster = postername_a;
  img_a.src = img_a_filename;
  vid_b.src = vid_b_filename;
  vid_b.poster = postername_b;
  img_b.src = img_b_filename;
}

function update_figure_9() {
  var choice = document.getElementById("figure_9_choice").value;
  if ((choice === "3color")){
  var filename = big_data_output + "/Yeast_3_color/figure.mp4";
  var postername = big_data_output + "/Yeast_3_color/poster.png";}
  if ((choice === "2color")){
  var filename = big_data_output + "/Yeast_2_color/figure.mp4";
  var postername = big_data_output + "/Yeast_2_color/poster.png";}  
  if ((choice === "amoeba")){
  var filename = big_data_output + "/Amoeba/figure.mp4";
  var postername = big_data_output + "/Amoeba/poster.png";}
  if ((choice === "paramecium")){
  var filename = big_data_output + "/Paramecium/figure.mp4";
  var postername = big_data_output + "/Paramecium/poster.png";}
  if ((choice === "spiro")){
  var filename = big_data_output + "/Spirostomum/figure.mp4";
  var postername = big_data_output + "/Spirostomum/poster.png";}
  if ((choice === "food")){
  var filename = big_data_output + "/Spirostomum_food/figure.mp4";
  var postername = big_data_output + "/Spirostomum_food/poster.png";}
  if ((choice === "flower")){
  var filename = big_data_output + "/Spirostomum_flower/figure.mp4";
  var postername = big_data_output + "/Spirostomum_flower/poster.png";}
  var vid = document.getElementById("Figure_9_vid");
  vid.src = filename;
  vid.poster = postername;
}

function update_figure_a4() {
  var choice = document.getElementById("figure_a4_choice").value;
  if ((choice === "0.1umRR")){
  var filename = "./images/PI/Step_response-RR_piezo_for_0.1um-10ms.png";} 
  if ((choice === "0.5umRR")){
  var filename = "./images/PI/Step_response-RR_piezo_for_0.5um-10ms.png";}  
  if ((choice === "1.0umRR")){
  var filename = "./images/PI/Step_response-RR_piezo_for_1um-10ms.png";}
  if ((choice === "15umRR")){
  var filename = "./images/PI/Step_response-RR_piezo_for_15um-15ms.png";}
  if ((choice === "10umInsert")){
  var filename = "./images/PI/Step_response-Z_piezo_insert_for_10um-50ms.png";}
  var img = document.getElementById("Figure_A4_png");
  img.src = filename;
}
