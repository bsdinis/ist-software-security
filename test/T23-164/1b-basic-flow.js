a="";
a=b();
c=a;
d=c;
e(d);
c=f;
c="";
e(c);

// tip: assignments propagate taintedness, and the order in which they are performed matters
