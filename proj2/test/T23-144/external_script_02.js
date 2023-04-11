function foo() {
	var pos = document.URL.indexOf("name=") + 5;
	var name = document.URL.substring(pos, document.URL.length);
	var sanitizedName = decodeURI(name);
	document.getElementById("d1").appendChild(document.createTextNode(sanitizedName));
}