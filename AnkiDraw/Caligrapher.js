/*
 -------------------------------- Caligrapher ------------------------------------------
 Created By: August Toman-Yih
 Git Repository: https://github.com/atomanyih/Calligrapher
*/
/* ------------------------------Unchanged Caligrapher Code------------------------------*/
/* ------------------------------        Corners.js        ------------------------------*/
/**
 * @classDescription        A shape made out of bezier curves. Hopefully connected
 * @param {Array} sections
 */
 function BezierShape(sections) {
    this.sections = sections;
    this.name = ""; //optional
    this.skeleton = [];
}

BezierShape.prototype.copy = function() {
    var newSections = [],
        newSkeleton = [];
    for(var i in this.sections) {
        newSections[i] = [];
        for(var j = 0; j<4; j++) {
            newSections[i][j] = this.sections[i][j].slice(0);
        }
    }
    for(var i in this.skeleton)
        newSkeleton[i] = this.skeleton[i].copy();
    
    var copy = new BezierShape(newSections);
    copy.name = this.name;
    copy.skeleton = newSkeleton;
    return copy;
};

/**
 * Draws the BezierShape NO SCALING OR NUFFIN. Probably only used internally
 * @param {Object} ctx
 */
BezierShape.prototype.draw = function(ctx) {
    var x = this.sections[0][0][0], //ew
        y = this.sections[0][0][1];
    var path = new Path2D()
    ctx.moveTo(x,y);
    for(var i = 0; i < this.sections.length; i++) {
        var b = this.sections[i];
        ctx.bezierCurveTo(b[1][0],b[1][1],b[2][0],b[2][1],b[3][0],b[3][1]);
    }
    ctx.closePath();
        // Erase
    var save = ctx.strokeStyle
    switch_to_no_alpha(save)
    ctx.globalCompositeOperation = "destination-out";
    ctx.fill(path);
    switch_back_to_correct_alpha(save)
    ctx.globalCompositeOperation = "source-over";
    ctx.fill(path);
};

function Bone(points,offset) {
    this.points = points;
    this.offset = offset;
}

Bone.prototype.copy = function() {
    var nP = [];
    for(var i in this.points)
        nP[i] = this.points[i].slice(0);
    return new Bone(nP,this.offset);
};

function drawCornerScaled(corner,pos,dir,width,height,ctx) { //FIXME degree, radian inconsistency
    ctx.save();
    ctx.translate(pos[0],pos[1]);
    ctx.rotate(dir);
    ctx.scale(height,width);
    
    corner.draw(ctx);
    ctx.restore();
}

function drawCorner(corner,pos,dir,width,ctx) {
    drawCornerScaled(corner,pos,dir,width,width,ctx);
}

function drawDICorner(corner,attrs,width,ctx) {
    if(corner == null)
        return;
    
    // corner rotation
    var pos = attrs.point,
        inAngle = attrs.inAngle-corner.skeleton["armA"].offset, //This is so the whole corner is rotated //FIXME a little gross
        outAngle = attrs.outAngle,
        c = setBoneAngles(corner,[["armB",(outAngle-inAngle)/180*Math.PI]]); 

    drawCorner(c,pos,inAngle/180*Math.PI,width,ctx);
}



// HERE ARE SOME CORNERS // some may need to be rotated
kappa = 0.5522847498;
// Circle-ish thing. Not a corner.
CIRCLE = new BezierShape([
    [[-5,0],[-5,-5*kappa],[-5*kappa,-5],[0,-5]],
    [[0,-5],[5*kappa,-5],[5,-5*kappa],[5,0]],
    [[5,0],[5,5*kappa],[5*kappa,5],[0,5]],
    [[0,5],[-5*kappa,5],[-5,5*kappa],[-5,0]]
]);
                
        
C1 = new BezierShape([
     [[15,6],  [-3,4],     [-11,5],   [-20,0]]
    ,[[-20,0],  [-15,-5],  [4,-9],    [13,-5]]
    ,[[13,-5], [20,0],     [21,8],    [15,6]]
]);
C1.name = "C1";

C2 = new BezierShape([
     [[2,5],    [-2,5],     [-12,2],    [-13,-2]]
    ,[[-13,2],  [-7,-5],    [0,-5],     [2,-5]]
    ,[[2,-5],   [3,-5],     [3,5],      [2,5]]
]);
C2.name = "C2";

C3 = new BezierShape([
    [[-8,5],    [-10,5],    [-10,-5],   [-8,-5]]
   ,[[-8,-5],   [3,-5],     [15,0],     [15,5]]
   ,[[15,5],    [10,7],     [2,5],      [-8,5]]
]);
C3.name = "C3";

C4 = new BezierShape([
    [[0,5],     [-2,5],     [-4,7],     [-5,8]]
   ,[[-5,8],    [-7,10],    [-9,12],    [-8,5]]
   ,[[-8,5],    [-7,3],     [-5,-5],    [0,-5]]
   ,[[0,-5],    [3,-5],     [3,5],      [0,5]]
]);
C4.name = "C4";

C5 = new BezierShape([
    [[0,-5],    [-3,-5],    [-3,5],     [0,5]]
   ,[[0,5],     [8,5],      [10,5],     [15,2]]
   ,[[15,2],    [12,-2],    [-2,-5],    [0,-5]]
]);
C5.name = "C5";

C6 = new BezierShape([
    [[0,5],     [-6,6],     [-8,7],     [-12,8]]
    ,[[-12,8],  [-13,9],    [-13,7],    [-12,6]]
    ,[[-12,6],  [-10,3],    [-5,-4],    [0,-5]]
    ,[[0,-5],   [3,-5],     [3,5],      [0,5]]
]);
C6.name = "C6";

C7 = new BezierShape([
    [[-5,-5],[0,-5],[11,-7],[15,-6]]
    ,[[15,-6],[17,-5],[2,4],[1,5]]
    ,[[1,5],[0,5],[0,5],[-5,5]]
    ,[[-5,5],[-8,5],[-8,-5],[-5,-5]]
]);
C7.name = "C7";

SI_CORNERS = [C1,C2,C3,C4,C5,C6,C7];

C8 = new BezierShape([
    [[-13,3],   [-20,3],    [-20,-3],   [-13,-3]],
    [[-13,-3],  [-5,-5],    [-6,-7],    [-4,-8]],
    [[-4,-8],   [0,-8],     [12,3],     [7,5]],
    [[7,5],     [5,6],      [5,8],      [3,13]],
    [[3,13],    [3,20],     [-3,20],    [-3,13]],
    [[-3,13],   [-5,5],     [-10,5],    [-13,3]]
]);
C8.name = "C8";
C8.skeleton["armA"] = new Bone([[0,0],[0,1],[0,2],[0,3],[1,0],[1,1],[5,2],[5,3]],0);
C8.skeleton["armB"] = new Bone([[4,0],[4,1],[4,2],[4,3],[3,2],[3,3],[5,0],[5,1],
                                [1,2],[1,3],[2,0],[2,1]],90);

C8R = horizFlipCopy(C8);

/*C9 = new BezierShape([ //TODO fix corner so that stem moves depending on angle
    [[-3,-10],  [-3,-15],   [3,-15],    [3,-10]],
    [[3,-10],   [5,-5],     [6,6],      [0,11]],
    [[0,11],    [-5,15],    [-3,5],     [-10,3]],
    [[-10,3],   [-15,3],    [-15,-3],   [-10,-3]],
    [[-10,-3],  [-5,-5],    [-5,-7],    [-3,-10]]
]);
C9.name = "C9";
C9.skeleton["armA"] = new Bone([[0,0],[0,1],[0,2],[0,3],[1,0],[1,1],[4,2],[4,3]],90);
C9.skeleton["armB"] = new Bone([[3,0],[3,1],[3,2],[3,3],[4,0],[4,1],[2,2],[2,3]],180);*/

C9 = new BezierShape([ //note, 90º angles look a little weird
   [[-4,-12],[-4,-15],[4,-15],[5,-12]],
   [[5,-12],[5,-2],[6,3],[1,8]],
   [[-1,8],[-3,11],[-4,2],[-12,-5]],
   [[-12,-5],[-15,-7],[-15,-9],[-10,-8]],
   [[-10,-8],[-6,-8],[-4,-7],[-4,-12]] 
]);
C9.name = "C9";
C9.skeleton["armA"] = new Bone([[0,0],[0,1],[0,2],[0,3],[1,0],[1,1],[4,2],[4,3],[1,2]],90); //not that this actually matters
C9.skeleton["armB"] = new Bone([[3,0],[3,1],[3,2],[3,3],[4,0],[4,1],[2,2],[2,3]],210);

C9R = vertFlipCopy(C9);

C10 = new BezierShape([
    [[-5,5],[-6,5],[-6,-5],[-5,-5]],
    [[-5,-5],[-2,-7],[2,-7],[5,-5]],
    [[5,-5],[6,-5],[6,5],[5,5]],
    [[5,5],[2,7],[-2,7],[-5,5]]
]);

C10.name = "C10";
C10.skeleton["armA"] = new Bone([[0,0],[0,1],[0,2],[0,3],[1,0],[1,2],[3,2],[3,3]],0);
C10.skeleton["armB"] = new Bone([[2,0],[2,1],[2,2],[2,3],[3,0],[3,1],[1,2],[1,3]],0);

function linInterpolate(y0,y1,mu) {
    return y0*(1-mu) + y1*mu;
}

function cosInterpolate(y0,y1,mu) {
    var mu2 = (1-Math.cos(mu*Math.PI))/2;
    return y0*(1-mu2)+y1*mu2;
}

/**
 * Returns a function that linearly interpolates between the values given
 */
function linFunction(points) {
    return function(t) {
        if(t==0)
            return points[0][1];
        for(var i = 1; i<points.length; i++) {
            var p0 = points[i-1],
                p1 = points[i];
            if(t<=p1[0] && t>p0[0]) {
                var mu = (t-p0[0])/(p1[0]-p0[0]);
                return linInterpolate(p0[1],p1[1],mu); //cubic might be better
            }
        }
    };
}

/**
 * Returns a function that cosine interpolates between the values given
 */
function cosFunction(points) {
    return function(t) {
        if(t==0)
            return points[0][1];
        for(var i = 1; i<points.length; i++) {
            var p0 = points[i-1],
                p1 = points[i];
            if(t<=p1[0] && t>p0[0]) {
                var mu = (t-p0[0])/(p1[0]-p0[0]);
                return cosInterpolate(p0[1],p1[1],mu); //cubic might be better
            }
        }
    };
}

//example thickness functions
function one(t) {
    return 1;
}

function test(t) {
    return t;
}

//These are ugly
SEGMENT_I = cosFunction([[0,1],[.5,.7],[1,1]]); //FIXME, sometimes extends past corners
SEGMENT_II = linFunction([[0,1],[.5,.8],[1,.2]]); //kinda ugly :||
SEGMENT_III = linFunction([[0,.2],[.5,.8],[1,1]]);

HEN = [C2,SEGMENT_I,C3];
SHU1 = [C4,SEGMENT_I,C5];
SHU2 = [C4,SEGMENT_II];
NA = [C6,SEGMENT_I,C7];
DIAN = [C1];
OTHER = [C4,SEGMENT_II];

function RAND(t) {
    return Math.random();
}

function setBoneAngles(c,dirList) {
    var c = c.copy();
    
    for(var i in dirList) {
        var dir = dirList[i][1],
            bone = dirList[i][0];
        for(var j in c.skeleton[bone].points) {
            var p = c.skeleton[bone].points[j],
                offset = c.skeleton[bone].offset/180*Math.PI,
                vec = c.sections[p[0]][p[1]];
            //console.log(vec);
            //console.log(dir-offset);
            //console.log(rotate(vec,dir-offset));
            c.sections[p[0]][p[1]] = rotate(vec,dir-offset);
            
        }
    }
    
    return c;
}

function vertFlipCopy(c) {
    var c = c.copy();
    
    for(var i in c.sections){
        for(var j in c.sections[i]) {
            c.sections[i][j][1] = -c.sections[i][j][1];
        }
    }
    for(var i in c.skeleton) {
        c.skeleton[i].offset = 360 - c.skeleton[i].offset;
    }
    return c
}

function horizFlipCopy(c) {
    var c = c.copy();
    
    for(var i in c.sections){
        for(var j in c.sections[i]) {
            c.sections[i][j][0] = -c.sections[i][j][0];
        }
    }
    for(var i in c.skeleton) {
        c.skeleton[i].offset = 180 - c.skeleton[i].offset;
        if(c.skeleton[i].offset<0)
            c.skeleton[i].offset += 360;
    }
    return c
}

/* ------------------------------        bezier.js        ------------------------------*/

//TODO use vectors for everything so it's less stupid

// Generalized recurvsive BEZIER FUNCTIONS (why am I doing it this way I don't know)
/**
 * returns a point on the bezier curve
 * @param {Array} ps    Control points of bezier curve
 * @param {Numeric} t   Location along bezier curve [0,1]  
 * @return {Array}      Returns the point on the bezier curve
 */
 function bezierPos(ps, t) {
    var size = ps.length;
    if(size == 1)
        return ps[0];
        
        //WARNING, changed direction on this. May cause problems
    var bx = (t) * bezierPos(ps.slice(1),t)[0] + (1-t) * bezierPos(ps.slice(0,size-1),t)[0],
        by = (t) * bezierPos(ps.slice(1),t)[1] + (1-t) * bezierPos(ps.slice(0,size-1),t)[1];
        
    return [bx,by];
}

function bezierSlo(ps, t) {
    var size = ps.length;
    
    if(size == 1)
        return ps[0];
        
    var dx = bezierPos(ps.slice(0,size-1),t)[0] - bezierPos(ps.slice(1),t)[0] ,
        dy = bezierPos(ps.slice(0,size-1),t)[1] - bezierPos(ps.slice(1),t)[1];
        
    return dy/dx;
}

// Bezier function class. Meant simply as a math thing (no drawing or any bullshit)
/**
 * @class Bezier function class.
 * @return {Bezier} Returns the bezier function
 */
function Bezier(controlPoints) {
    this.order = controlPoints.length-1; //useful? or obtuse? //Answer: not used anywhere
    this.controlPoints = controlPoints; 
}

Bezier.prototype.getStart = function() {
    return this.controlPoints[0];
};

Bezier.prototype.getEnd = function() {
    return this.controlPoints[this.order];
};

Bezier.prototype.getPoint = function(t) {
    return bezierPos(this.controlPoints,t);
};

Bezier.prototype.drawPlain = function(ctx) {
    if(this.order == 3) {
        var c = this.controlPoints;
        var path = new Path2D()

        path.moveTo(c[0][0],c[0][1]);
        path.bezierCurveTo(c[1][0],c[1][1],c[2][0],c[2][1],c[3][0],c[3][1]);


        // Erase
        var save = ctx.strokeStyle
        switch_to_no_alpha(save)
        ctx.globalCompositeOperation = "destination-out";
        ctx.stroke(path);
        switch_back_to_correct_alpha(save)
        ctx.globalCompositeOperation = "source-over";
        ctx.stroke(path);
    }
};

Bezier.prototype.getDerivativeVector = function(t) {
    var size = 0.001,
        p0 = null,
        p1 = null;
    if(t<size) {
        p0 = bezierPos(this.controlPoints,t);
        p1 = bezierPos(this.controlPoints,t+2*size);
    } else if (1-t<size) {
        p0 = bezierPos(this.controlPoints,t-2*size);
        p1 = bezierPos(this.controlPoints,t);
    } else {
        p0 = bezierPos(this.controlPoints,t-size);
        p1 = bezierPos(this.controlPoints,t+size); 
    }
    return sub(p1,p0);
};

Bezier.prototype.getTangentVector = function(t) {
    return normalize(this.getDerivativeVector(t));
};

Bezier.prototype.getLength = function() {
    var res = 50, //FIXME: can't use resolution :|| that would be circular
        len = 0,
        point = this.getStart();
    for(var i = 0; i <= res; i++){
        var t = i/res;
        len += getDist(point,this.getPoint(t));
        point = this.getPoint(t);
    }
    return len;
};

Bezier.prototype.getLengthAt = function(t) {
    return getLengthAtWithStep(t,0.01);
};

Bezier.prototype.getLengthAtWithStep = function(t,s) {
    var tt = 0,
        len = 0,
        point = this.getStart();
    while(tt <= t) {
        var newPoint = this.getPoint(tt);
        len += getDist(point,newPoint);
        point = newPoint;
        t += s;
    }
    return len;
};

Bezier.prototype.getPointByLength = function(l) {//doesn't actually return a point. bad name
    var t = 0,
        len = 0,
        point = this.getStart();
    while(len < l) {
        var newPoint = this.getPoint(t);
        len += getDist(point,newPoint);
        point = newPoint;
        t += 0.01;
        if(t>=1)
            return 1; //so we don't extrapolate or anything stupid
    }
    return t;
};

Bezier.prototype.getPointByLengthBack = function(l) {//doesn't actually return a point. bad name
    var t = 1,
        len = 0,
        point = this.getEnd();
    while(len < l) {
        var newPoint = this.getPoint(t)
        len += getDist(point,newPoint);
        point = newPoint;
        t -= 0.01;
        if(t<=0)
            return 1; //so we don't extrapolate or anything stupid
    }
    return t;
};

function getSlopeVector(slope,length) {
    var x = length * Math.cos(Math.atan(slope)),
        y = length * Math.sin(Math.atan(slope));
    return [x,y];
}

function scalePoint(s0,s1,p0,p1,v) { //Could probs be simplified, also currently not used
    var xScale = (p1[0]-p0[0])/(s1[0]-s0[0]), //scaling factos
        yScale = (p1[1]-p0[1])/(s1[1]-s0[1]),
        x = p0[0]+xScale*(v[0]-s0[0]), //Scaled x and y
        y = p0[1]+yScale*(v[1]-s0[1]);
    return [x,y];
}

//Draws a bezier curve scaled between the two points (good idea? bad idea? dunno.) 
/**
 * @param {Bezier}  curve   The bezier curve to be drawn
 * @param {Numerical} wid   Nominal width
 * @param {Function} wF     Width function
 * @param {Context} ctx     Context to draw to
 */
//FIXME width function gets "bunched up" around control points (detail below)
//      the bezier calculation means that more of t is spent near control points. turn on debug to see
//      this is good for detail b/c it means higher resolution at tight curves (a happy accident)
//      but the width contour gets a bit bunched up. solution: instead of wF(t), use wF(currentLength/totalLength)

//FIXME Ugly (code)
function drawBezier(curve,wid,wF,ctx) { 
    var length = curve.getLength(),
        numPoints = Math.round(length/RESOLUTION),
        leftPoints = [],
        rightPoints = [],
        currentPoint = sub(scale(curve.getStart(),2),curve.controlPoints[1]);

    for(var i = 0; i <= numPoints; i++){
        var t = i/numPoints,
            centerPoint = curve.getPoint(t)
            offset = scale(perpNorm(sub(centerPoint,currentPoint)),wF(t)*wid/2);
            
        leftPoints.push(add(centerPoint,offset));
        rightPoints.push(sub(centerPoint,offset));
        currentPoint = centerPoint;

    }
    //Drawing the polygon
    var s = leftPoints[0];
    var path = new Path2D();
    path.moveTo(s[0],s[1]); //starting from start center
    for(var i = 0; i < leftPoints.length; i++){
        var p = leftPoints[i];
        path.lineTo(p[0],p[1]);
    }
    for(var i = rightPoints.length-1; i >= 0; i--){
        var p = rightPoints[i];
        path.lineTo(p[0],p[1]);
    }
    path.closePath();
    // Erase
    var save = ctx.strokeStyle
    switch_to_no_alpha(save)
    ctx.globalCompositeOperation = "destination-out";
    ctx.fill(path);

    switch_back_to_correct_alpha(save)
    ctx.globalCompositeOperation = "source-over";
    ctx.fill(path);
}

function drawBezierTransformed(p0,p1,curve,wid,wF,ctx) {
    var s0 = curve.getStart(),
        s1 = curve.getEnd(),
        xScale = (p1[0]-p0[0])/(s1[0]-s0[0]), //scaling factos
        yScale = (p1[1]-p0[1])/(s1[1]-s0[1]),
        controlPoints = [];
        
    for(var i = 0; i <= curve.order; i++) {
        var p = curve.controlPoints[i],
            x = p0[0]+xScale*(p[0]-s0[0]), //Scaled x and y
            y = p0[1]+yScale*(p[1]-s0[1]);
        controlPoints[i] = [x,y];
    }
    drawBezier(new Bezier(controlPoints),wid,wF,ctx);
        
}

/* ------------------------------        curveFitting.js        ------------------------------*/
function getLengths(chord) {
    var lens = [0]; //first is 0
    
    for(var i = 1; i<chord.length; i++)
        lens[i] = lens[i-1]+getDist(chord[i],chord[i-1]);
    return lens;
}

function normalizeList(lens) {
    for(var i = 1; i<lens.length; i++)
        lens[i] = lens[i]/lens[lens.length-1];
    return lens;
}

function findListMax(list) {
    var iMax = 0,
        max = list[0];
    for(var i = 0; i<list.length; i++) {
        if(max<list[i]) {
            iMax = i;
            max = list[i];
        }
    }
    return [iMax,max];       
}

function findListMin(list) {
    var iMin = 0,
        min = list[0];
    for(var i in list) {
        if(min>list[i]) {
            iMin = i;
            min = list[i];
        }
    }
    return [iMin,min];
}

function parameterize(chord) {
    /*var lens = getLengths(chord);
    return normalizeList(lens);*/
    var lens = [0]; //first is 0
    
    for(var i = 1; i<chord.length; i++)
        lens[i] = lens[i-1]+getDist(chord[i],chord[i-1]);
    for(var i = 1; i<chord.length; i++)
        lens[i] = lens[i]/(lens[chord.length-1]);
    return lens;
    
}

function parameterizeByLength(chord, curve) {
    var lens = getLengths(chord),
        ts = [0];
    for(var i = 1; i<chord.length; i++) {
        ts[i] = curve.getPointByLength(lens[i]);
    }
    return normalizeList(ts);
}

function coefficientHelper(chord,ts) { //bad name
    var c00 = 0, c01 = 0, c02x = 0, c02y = 0,
        c10 = 0, c11 = 0, c12x = 0, c12y = 0,
        x0 = chord[0][0],
        y0 = chord[0][1],
        x3 = chord[chord.length-1][0],
        y3 = chord[chord.length-1][1];
        
    for(var i = 0; i<ts.length; i++) {
        var t = ts[i],
            px = chord[i][0],
            py = chord[i][1];
        c00 += 3*Math.pow(t,2)*Math.pow(1-t,4); //I'm doing it the dumb way cause it's easier to read
        c01 += 3*Math.pow(t,3)*Math.pow(1-t,3);
        c02x += t*Math.pow(1-t,2)*(px - Math.pow(1-t,3) * x0 - Math.pow(t,3) * x3);
        c02y += t*Math.pow(1-t,2)*(py - Math.pow(1-t,3) * y0 - Math.pow(t,3) * y3);
        
        c10 += 3*Math.pow(t,3)*Math.pow(1-t,3);
        c11 += 3*Math.pow(t,4)*Math.pow(1-t,2);
        c12x += Math.pow(t,2)*(1-t)*(px - Math.pow(1-t,3) * x0 - Math.pow(t,3) * x3);
        c12y += Math.pow(t,2)*(1-t)*(py - Math.pow(1-t,3) * y0 - Math.pow(t,3) * y3);
    }
    return [[[c00,c01,c02x],[c10,c11,c12x]],
            [[c00,c01,c02y],[c10,c11,c12y]]];
}

function leastSquaresFit(chord,ts) { //IT FUCKIN WORKS FUCK YEAAAAAAAH
    if(chord.length < 4) {
        var c1 = chord[0],
            c4 = chord[chord.length-1],
            c2 = midpoint(c1,c4,0.25),
            c3 = midpoint(c1,c4,0.75);
        return new Bezier([c1,c2,c3,c4]);
    }
    var cs = coefficientHelper(chord,ts),
        xs = gaussianElimination(cs[0]),
        ys = gaussianElimination(cs[1]);
    
    return new Bezier([chord[0], [xs[0],ys[0]], [xs[1],ys[1]], chord[chord.length-1]]);
}

function getMaxErrorPoint(chord,ts,curve) {
    var max = 0,
        iMax = 0;
    for(var i = 0; i<ts.length; i++) {
        var dist = getDist(curve.getPoint(ts[i]),chord[i]);
        if(dist > max) {
            max = dist;
            iMax = i;
        }
    }
    return [iMax,max];
}

function fitStroke(chord) {
    var chords = splitChord(chord,detectCorners(chord)),
        curves = [];
        
    for(var i in chords) {
        var ts = parameterize(chords[i]),
            curve = leastSquaresFit(chords[i],ts);
        curves.push(curve);
    }
    
    return curves;
}

function splitCurve(chord,ts,curve) { //TODO FIGURE THIS FUCKING SHIT OUT
    var errs = [];
    for(var i = 1; i<chord.length; i++) {
        var chord1 = chord.slice(0,i+1),
            chord2 = chord.slice(i),
            ts1    = parameterize(chord1),
            ts2    = parameterize(chord2),
            curve1 = leastSquaresFit(chord1,ts1),
            curve2 = leastSquaresFit(chord2,ts2);
        errs.push(sumSquaredError(chord1,ts1,curve1) +
                  sumSquaredError(chord2,ts2,curve2));
    }
    //console.log(errs);
    return findListMin(errs);
}

function splitCurveAt(chord,i) {
    var chord1 = chord.slice(0,i+1),
        chord2 = chord.slice(i),
        ts1    = parameterize(chord1),
        ts2    = parameterize(chord2),
        curve1 = leastSquaresFit(chord1,ts1),
        curve2 = leastSquaresFit(chord2,ts2);
    return [curve1,curve2];
}

function sumSquaredError(chord,ts,curve) {
    var sum = 0;
    for(var i in chord) {
        sum += Math.pow(getDist(chord[i],curve.getPoint(ts[i])),2);
    }
    return sum;
}

// corner detection?

function detectCorners(chord) {
    var segmentLength = 30,
        angleThreshold = 135,
        indices = [];
    for(var i = 1; i<chord.length-1; i++) {
        var angle = getSmallerAngle(getAngleBetween(sub(chord[i-1],chord[i]), sub(chord[i+1],chord[i])))*180/Math.PI;

        if(angle<=angleThreshold) {
            indices.push(i);
        }
    }
    
    return indices;
}

//returns the shortest segment of the chord that is at least the given length
function getChordSegmentByLength(chord,length) {
    var dist = 0;
    var i = 0;
    while(dist<length) {
        i++;
        if(i >= chord.length) //if it's not long enough just return the whole thing
            return chord; 
        dist+=getDist(chord[i],chord[i-1]); 
    }
    return chord.slice(0,i);
}

function splitChord(chord,indices) {
    var newChords = [],
        ind = 0;
    for(var i in indices) {
        newChords.push(chord.slice(ind,indices[i]+1));
        ind = indices[i];
    }
    newChords.push(chord.slice(ind));
    return newChords;
}

function chordPrint(chord) {
    var s = "| ";
    for(var i in chord) {
        s+= chord[i] + " | ";
    }
    //console.log(s);
}

/* ------------------------------        strokeDrawing.js        ------------------------------*/

//Stroke drawing and analysis
//Basically, a "stroke" will be a collection of segments
//the segments when drawn will be assigned corners and types and stuff

function drawSegment(wF,segment,width,ctx) {
    drawBezier(segment,width,wF,ctx);
    //ctx.fillStyle = "rgba(0,0,0,1)";
}



function drawBasicStroke(segment,width,ctx) { //TODO
    var attrs = getSegmentAttributes(segment),
        comps = checkRules2(attrs,RULE_BS);
    
    //corners
    if(comps.length == 1){ //dian
        var point = midpoint(attrs.startPoint,attrs.endPoint,0.5);  //FIXME these stupid width division factors
        drawCornerScaled(comps[0],point,degToRad(attrs.startAngle),width/13,attrs.length/20,ctx);
    } else {
        drawCorner(comps[0],attrs.startPoint,degToRad(attrs.startAngle),width/10,ctx);
        if(comps.length == 3) {
            drawCorner(comps[2],attrs.endPoint,degToRad(attrs.endAngle),width/10,ctx);
        }
        
        drawSegment(comps[1],segment,width,ctx);
    }
}

function Stroke(segments) {
    this.segments = segments;
}

Stroke.prototype.drawPlain = function(ctx) {
    var x = this.segments[0].getStart()[0],
        y = this.segments[0].getStart()[1];
    ctx.moveTo(x,y);
    var path = new Path2D();
    for(var i = 0; i < this.segments.length; i++) {
        var b = this.segments[i].controlPoints;
        path.bezierCurveTo(b[1][0],b[1][1],b[2][0],b[2][1],b[3][0],b[3][1]);
    }
    // Erase
    var save = ctx.strokeStyle
    switch_to_no_alpha(save)
    ctx.globalCompositeOperation = "destination-out";
    ctx.stroke(path);

    switch_back_to_correct_alpha(save)
    ctx.globalCompositeOperation = "source-over";
    ctx.stroke(path);
};

Stroke.prototype.draw = function(width, ctx) {
    if(this.segments.length == 1){ //Basic Stroke
        drawBasicStroke(this.segments[0],width,ctx);
    } else { //Compound stroke
        drawCompoundStroke(this,width,ctx);
    }
};

function drawCompoundStroke(stroke,width,ctx) { //FIXME copypasta
    var numSegments = stroke.segments.length;

    //corners
    var attrs = getSegmentAttributes(stroke.segments[0]),
        corners = [];
    
    var corner = checkRules2(attrs,RULE_CC_START);//checkRules(attrs,COMPOUND_CORNER_START);
    if(corner != null)
        drawCorner(corner,attrs.startPoint,attrs.startAngle/180*Math.PI,width/10,ctx);
    corners.push(corner);
    
    for(var i = 1; i<numSegments; i++) {
        attrs = getCornerAttributes(stroke.segments[i-1],stroke.segments[i]);
        corner = checkRules2(attrs,RULE_CC_MID);//checkRules(attrs,COMPOUND_CORNER_MID);
        if(corner != null)
            drawDICorner(corner,attrs,width/10,ctx);
        corners.push(corner);
    }
    attrs = getSegmentAttributes(stroke.segments[numSegments-1]);
    corner = checkRules2(attrs,RULE_CC_END);//checkRules(attrs,COMPOUND_CORNER_END);
    if(corner != null)
        drawCorner(corner,attrs.endPoint,attrs.endAngle/180*Math.PI,width/10,ctx);
    corners.push(corner);
    
    //SEGMENTS FIXME gross code
    
    if(corners[0] == null)
        drawSegment(SEGMENT_III,stroke.segments[0],width,ctx);
    else
        drawSegment(SEGMENT_I,stroke.segments[0],width,ctx);
    for(var i = 1; i<numSegments-1; i++) {
        drawSegment(SEGMENT_I,stroke.segments[i],width,ctx); //FIXME only segment I. this is not done!
    }
    if(corners[numSegments] == null)
        drawSegment(SEGMENT_II,stroke.segments[numSegments-1],width,ctx);
    else
        drawSegment(SEGMENT_I,stroke.segments[numSegments-1],width,ctx);
    //ctx.fillStyle = "rgba(0,0,0,1)";
    
}

function inRange(num,range) {
    return num >= range[0] && num < range[1];
}

function inRanges(num,ranges) {
    for(var i = 0; i<ranges.length; i++) {
        if(inRange(num,ranges[i]))
            return true;
    }
    return false;
}

function getSegmentAttributes(seg) {
    var attrs = {
        "startAngle" : getSegAngleStart(seg) *180/Math.PI,
        "endAngle" : getSegAngleEnd(seg) * 180/Math.PI,
        "startPoint" : seg.getStart(),
        "endPoint" : seg.getEnd(),
        "length" : seg.getLength()
    };
    return attrs;
}

function getCornerAttributes(inSeg, outSeg) {
    var attrs = {
        "inAngle" : getSegAngleEnd(inSeg) * 180/Math.PI,
        "outAngle" : getSegAngleStart(outSeg) * 180/Math.PI,
        "point" : inSeg.getEnd()
    };
    attrs.betweenAngle = getInnerAngle(attrs.inAngle,attrs.outAngle);
    //console.log(attrs.inAngle,attrs.outAngle);
    //console.log(attrs.betweenAngle);
    return attrs;
}

function getInnerAngle(inAngle, outAngle) { //If outAngle is past inAngle, then it's negative
    inAngle = reduceAngleDeg(inAngle+180);
    var ang = Math.abs(getSmallerAngleDeg(inAngle - outAngle));
    if(inAngle>outAngle){
        if(inAngle-180<outAngle)
            return ang;
        return -ang;
    } else {
        if(outAngle-180<inAngle)
            return -ang;
        return ang;
    }
        
}

function innerAngleHelper(angle) { //if it's negative then it is the other angle
    if(angle>180)
        return angle-360;
    return angle;
}

function checkRule(obj,rule) {
    if(rule[0] == "Result")
        return rule[1];
    //console.log(rule[0]);
    if(inRange(obj[rule[0]],rule[1]))
        return checkRule(obj,rule[2]);
    return null;
}

function checkRules(obj,ruleset) { //checks all rules, no shortcircuiting currently
    var results = [];
    //console.log("Checking rules");
    for(var i = 0; i<ruleset.length-1; i++) {
        var result = checkRule(obj,ruleset[i]);
        if(result != null)
            results.push(result);
    }
    if(results.length > 1)
        throw "Overlapping conditions";
    if(results.length == 1)
        return results[0];
    //console.log("no result");
    return ruleset[ruleset.length-1]; //default
}

function checkRules2(obj,ruleset) {
    var results = [];
    //console.log("Checking rules");
    for(var i = 0; i<ruleset.length; i++) {
        if(ruleset[i].check(obj))
            return ruleset[i].result;
    }
    //console.log("No Result");
    return null
}

function Rule(result,condition) {
    this.condition = condition;
    this.result = result;
}

Rule.prototype.check = function(attrs) {
    return checkCond(attrs,this.condition);
}

function checkCond(attrs,cond) {
    var op = OPERATIONS[cond[1]],
        val = attrs[cond[0]];
    //console.log("Op:",cond[1]);
    //console.log(cond[0],val);
    return op(attrs,val,cond.slice(2));
}


TH1 = 60;
TH2 = 40;

OPERATIONS = {
    "TRUE" : function(a,n,r) {
        return true;
    },
    "IN_RANGE" : function(a,n,r) {
        for(var i in r)
            if(n>=r[i][0] && n<r[i][1])
                return true;
            return false;
    },
    "GREATER_THAN" : function(a,n,r) {
        return n>=r;
    },
    "LESS_THAN" : function(a,n,r) {
        return n<r;
    },
    "OR" : function(a,n,c) {
        for(var i in c)
            if(checkCond(a,c[i]))
                return true; 
            return false;
    },
    "AND" : function(a,n,c) {
        for(var i in c) 
            if(!checkCond(a,c[i]))
                return false; 
            return true;
    }
};

RULE_CC_START = [
    new Rule(C2, ["startAngle", "IN_RANGE", [0,10], [350,360]]),
    new Rule(C4, ["startAngle", "IN_RANGE", [80,350]])
];

RULE_CC_END = [
    new Rule(C3, ["endAngle", "IN_RANGE", [0,10], [350,360]]),
    new Rule(C7, ["endAngle", "IN_RANGE", [10,80]]),
    new Rule(C5, ["engAngle", "IN_RANGE", [80,100]])
];

RULE_CC_MID = [
    new Rule(C8, ["", "AND", ["inAngle", "IN_RANGE",[0,45],[315,360]],
                             ["betweenAngle", "IN_RANGE",[0,180]]]),
    new Rule(C8R,["", "AND", ["inAngle", "IN_RANGE", [60,170]], //a little ugly :| but accurate?
                            ["betweenAngle", "IN_RANGE",[-180,0]]]), 
    new Rule(C9, ["", "AND", ["inAngle", "IN_RANGE", [45,145]],
                             ["betweenAngle","IN_RANGE", [0,180]]]),
    new Rule(C9R,["", "AND", ["inAngle", "IN_RANGE", [0,60], [240,360]],
                            ["betweenAngle","IN_RANGE",[-180,0]]])
];

RULE_BS = [ //TODO, fix the "default" case
    new Rule(DIAN,["length","LESS_THAN",TH2]),
    new Rule(HEN,["startAngle","IN_RANGE",[0,10],[350,360]]),
    new Rule(SHU1,["", "AND", ["startAngle","IN_RANGE",[80,100]],
                              ["length","GREATER_THAN",TH1]]),
    new Rule(SHU2,["", "AND", ["startAngle","IN_RANGE",[80,100]],
                              ["length","IN_RANGE",[TH2,TH1]]]), //to prevent overlap
    new Rule(NA,["startAngle","IN_RANGE",[10,80]]),
    new Rule(OTHER,["","TRUE"])
];

// Rules
BASIC_STROKE = [
    ["startAngle", [0,10]]
];

COMPOUND_CORNER_START = [
    ["startAngle",   [0,10],    ["Result",C2]],
    ["startAngle",   [80,350],  ["Result",C4]],
    ["startAngle",   [350,360], ["Result",C2]],
    null
    ];

COMPOUND_CORNER_MID = [
    ["inAngle",     [0,45], ["betweenAngle", [0,180], ["Result", C8]]],
    ["inAngle",     [315,360], ["betweenAngle", [0,180], ["Result", C8]]],
    ["inAngle",     [45,135], ["betweenAngle", [-180,-90], ["Result", C8R]]],
    ["inAngle",     [45,135], ["betweenAngle", [0,180], ["Result", C9]]],
    ["inAngle",     [45,180], ["betweenAngle", [-90,0], ["Result", C9R]]],
    ["inAngle",     [0,45], ["betweenAngle", [-180,0], ["Result", C9R]]],
    ["inAngle",     [315,360], ["betweenAngle", [-180,0], ["Result", C9R]]],
    null
];

COMPOUND_CORNER_END = [
    ["endAngle",   [0,10],    ["Result",C3]],
    ["endAngle",   [10,80],   ["Result",C7]],
    ["endAngle",   [80,100],  ["Result",C5]],
    null
    ];
   
/* ------------------------------        examples.js        ------------------------------*/

// (ugly) Character examples for testing

//compound stroke
CSTROKE_1 = new Stroke([
    new Bezier([[50,110],[60,110],[190,100],[200,90]]),
    new Bezier([[200,90],[205,90],[200,150],[195,150]]),
    new Bezier([[195,150],[170,160],[120,150],[100,150]])
])

/* ------------------------------        Character.js        ------------------------------*/
// Angle test distance
var ANG_DIST = 0.3;

function getSegAngleStart(curve) {
    var start = curve.getStart(),
        point = curve.getPoint(curve.getPointByLength(20)),//curve.getPoint(ANG_DIST),
        dir   = getAngle(sub(point,start));
    if(dir<0)                   //No like
        dir += 2*Math.PI;
    return dir;
}

function getSegAngleEnd(curve) {
    var end = curve.getEnd(),
        point = curve.getPoint(curve.getPointByLengthBack(20)),//curve.getPoint(1-ANG_DIST),
        dir   = getAngle(sub(end,point)); //different from counterpart, maybe bad?
    if(dir<0)
        dir += 2*Math.PI;
    return dir;
}

/* ------------------------------        Math.js        ------------------------------*/

/*
 * A bunch of stuff
 */

 function vectorSum(v1, c, v2) {
    var result = [];
    for (var i = 0; i < v1.length; i++)
        result[i] = v1[i] + c * v2[i];
    return result;
}

/**
 * Prints a matrix in row,column format
 */
function matrixPrint(matrix) {
    for (var i = 0; i < matrix.length; i++) {
        //console.log(matrix[i]);
    }
}

function zeroes(r, c) {
    var m = [];
    for (var i = 0; i < r; i++) {
        m[i] = [];
        for (var j = 0; j < c; j++)
            m[i][j] = 0;
    }
    return m;
}

//Basic matrix operations
function transpose(m) {
    var result = zeroes(m[0].length, m.length);
    for (var r = 0; r < result.length; r++) {
        for(var c = 0; c < result[0].length; c++) {
            result[r][c] = m[c][r];
        }
    }
    return result;
}

function matrixMult(m1,m2) {
    if(m1[0].length != m2.length)
        throw "Matrix dimension mismatch. Cannot multiply";
    
    var result = zeroes(m1.length,m2[0].length);
    
    for(var r = 0; r<result.length; r++) {
        for(var c = 0; c<result[0].length; c++) {
            result[r][c]=mMultHelper(m1,m2,r,c);
        }
    }
    return result;
}

function mMultHelper(m1,m2,r,c) { //does dot producting BS
    var result = 0;
    for(var i = 0; i<m1.length; i++)
        result += m1[r][i]*m2[i][c];
    return result;
}

//probably will never be used
function rowProduct(m,r) {
    var result = 1;
    for(var i = 0; i<m[0].length; i++)
        result *= m[r][i];
    return result;
}

function colProduct(m,c) {
    var result = 1;
    for(var i = 0; i<m.length; i++)
        result *= m[i][c];
    return result;
}

/** indexed row,column 
 *  DOES NOT DO ANY LEGITIMACY CHECKS OR ANYTHING
 * @param {Object} matrix
 */
function gaussianElimination1(matrix) {
    matrix = matrix.slice(0); //shallow copy (it's cool cause it's ints)
    
    for(var i = 0; i<matrix.length; i++) {//each row get the first coeffecient
        var temp = gElHelper1(matrix[i]),
            p = temp[0],
            a = temp[1];
            
        for(var j = 0; j<matrix.length; j++) { //remove from other rows
            var b = matrix[j][p];
            
            if(b != 0 && i != j)
                matrix[j] = vectorSum(matrix[j],-b/a,matrix[i]);
        }
    }

    //This part assumes that you end up with something in almost row echelon form (coeffecients may not be 1)    
    var result = [],
        numVars = matrix[0].length-1;
    for(var i = 0; i<numVars; i++) { //grabbing the results
        result[i] = matrix[i][numVars]/matrix[i][i];
    }
    return result;
    
    
}
//Helper function returns the first position of a nonzero coeffecient and the coefficient itself
function gElHelper1(vector) {
    for(var i = 0; i<vector.length; i++)
        if(vector[i] != 0)
            return [i,vector[i]];
    return -1
}

function gaussianElimination(matrix) {
    matrix = matrix.slice(0);
    var numRows = matrix.length,
        numCols = matrix[0].length,
        sol = [];
        
    //matrixPrint(matrix);
    
    for(var c = 0; c<numRows; c++) {
        var iMax = gElHelper(matrix,c);
        
        if(matrix[iMax][c] == 0)
            throw "Matrix is singular"
        swapRows(matrix,c,iMax);
        
        for(var d = c+1; d<numRows; d++) {
            var mult = matrix[d][c]/matrix[c][c];
            
            matrix[d] = vectorSum(matrix[d],-mult,matrix[c]);
        }
    }
    
    for(var r = 0; r<numRows; r++) {
        var i = numRows-r-1;
        
        for(var s = r+1; s<numRows; s++) {
            var mult = -matrix[s][i]/matrix[r][i]
            matrix[s] = vectorSum(matrix[s],mult,matrix[r]);
        }
        sol.push(matrix[r][numCols-1]/matrix[r][i]);
    }
    
    return sol.reverse();
}
//Helper function finds the pos of the max in the column
function gElHelper(matrix,c) {
    var iMax = 0;
    for(var i = c; i<matrix.length; i++) {
        if(Math.abs(matrix[i][c])>Math.abs(matrix[iMax][c]))
            iMax = i;
    }
    return iMax
}

function swapRows(matrix,r0,r1) {
    var i = matrix[r0];
    matrix[r0]=matrix[r1];
    matrix[r1]=i;
    return matrix;
}

/* ------------------------------        Vector.js        ------------------------------*/

// Math
function truncate(vector, max) {
    var mag = getMag(vector);
    if(mag > max)
        return scale(vector,max/mag);
    return vector;
}

function perp(vector) {
    return [vector[1],-vector[0]];
}

function perpNorm(vector) {
    return normalize(perp(vector));
}

function normalize(vector) {
    //if(vector[0]==0 && vector[1]==0)
    //    return [0,1];
    var mag = getMag(vector);
    return scale(vector,1/mag);
}

function normalizeTo(vector,mag) {
    return scale(normalize(vector),mag);
}

function projectedLength(vector,along) {
    return dot(vector,along)/getMag(along);
}

function project(vector,along) {
    
}

function scale(vector,factor) {
    return [vector[0]*factor,vector[1]*factor];
}

function add(vector1, vector2) {
    return [vector1[0]+vector2[0],vector1[1]+vector2[1]];
}

function sub(vector1, vector2) {
    return [vector1[0]-vector2[0],vector1[1]-vector2[1]];
}

function getMag(vector) {
    return getDist([0,0],vector);
}
    
function getDist(vector1,vector2) {
    return Math.sqrt(Math.pow((vector2[0]-vector1[0]),2)+Math.pow((vector2[1]-vector1[1]),2));
}

function getAngle(vector) {
    var quad = 0;
    if(vector[0]===0) // because 0 and -0 are not always the same
        vector[0] = +0;
    if(vector[0]<0)
        quad = Math.PI;
    else if(vector[0]>0 && vector[1]<0)
        quad = 2*Math.PI;
    return reduceAngle(Math.atan(vector[1]/vector[0])+quad);
}

function getAngleBetween(vector1,vector2) {
    return Math.abs(getAngle(vector1)-getAngle(vector2));
}

function getSmallerAngle(angle) {
    if(angle > Math.PI)
        return 2*Math.PI-angle;
    if(angle < -Math.PI)
        return -2*Math.PI-angle
    return angle;
}

function getSmallerAngleDeg(angle) {
    if(angle > 180)
        return 360-angle;
    if(angle < -180)
        return -360-angle;
    return angle;
}

function radToDeg(angle) {
    return angle*180/Math.PI;
}

function degToRad(angle) {
    return angle*Math.PI/180;
}

function reduceAngle(angle) {
    return angle-Math.floor(angle/(2*Math.PI))*2*Math.PI;
}

function reduceAngleDeg(angle) {
    return angle-Math.floor(angle/360)*360;
}

function dot(vector1,vector2) {
    return vector1[0]*vector2[0]+vector1[1]*vector2[1];
}

function point(vector,dir) {
    var mag = getMag(vector);
    return [Math.cos(dir)*mag,Math.sin(dir)*mag];
}

function rotate(v,rad) {
    var ang = getAngle(v);
    if(v[0] == 0 && v[1] == -8) {
        //console.log(v);
        //console.log("!");
        //console.log(ang);
        //console.log(rad);
        //console.log(point(v,rad+ang));
    }
    return point(v,rad+ang);
}

function midpoint(p1,p2,t) {
    return add(scale(p1,1-t),scale(p2,t));
}