var str = "http://www.google.com";

function foo(x) {
	with(x) {
		str = document.location.href;
	}
}

foo({bar: "bar"});
document.write(str);