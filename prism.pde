// === USER'S CREATIVE CODE ===
//--------------------------
// 1. Define any classes
//--------------------------
class WindLine {
  float angleOffset;  // base rotation around center
  float spin;         // integer multiple rotational speed for perfect looping
  float freq;         // wave frequency
  float amplitude;    // wave amplitude
  float offset;       // phase offset for the sine wave
  float sw;           // stroke weight
  color lineColor;    // stroke color

  WindLine() {
    angleOffset = random(TWO_PI);
    // spin must be an integer >= 1 for clean looping rotations
    spin = floor(random(1, 4)); 
    freq = random(0.005, 0.02);
    amplitude = random(50, 150);
    offset = random(10000); 
    sw = random(1, 3);
    // Monochromatic, bright grayscale with some alpha
    lineColor = color(200 + random(55), 120);
  }

  void display(float progress) {
    pushMatrix();
    // Rotate line by its offset + spinning factor
    rotate(angleOffset + progress * TWO_PI * spin);

    stroke(lineColor);
    strokeWeight(sw);
    noFill();

    beginShape();
    // We'll draw a sinusoidal line from -400 to 400
    for (float x = -400; x <= 400; x += 10) {
      float phaseShift = progress * ( TWO_PI / freq ); // ensures wave loops perfectly
      float y = sin(freq * (x + offset + phaseShift)) * amplitude;
      vertex(x, y);
    }
    endShape();

    popMatrix();
  }
}

//--------------------------
// 2. Declare global variables
//--------------------------
WindLine[] lines;
int numLines = 20;

//--------------------------
// 3. Define initSketch() - called once at start
//--------------------------
void initSketch() {
  lines = new WindLine[numLines];
  for (int i = 0; i < numLines; i++) {
    lines[i] = new WindLine();
  }
}

//--------------------------
// 4. Define runSketch(progress) - called each frame
//    progress goes from 0.0 to 1.0
//--------------------------
void runSketch(float progress) {
  // Draw each wind line
  for (int i = 0; i < numLines; i++) {
    lines[i].display(progress);
  }
}
// END OF YOUR CREATIVE CODE

// === SYSTEM FRAMEWORK ===
void setup() {
    size(1080, 1080);
    frameRate(60);
    smooth();
    initSketch();  // Initialize user's sketch
}

final int totalFrames = 360;
boolean hasError = false;

void draw() {
    try {
        background(0);
        stroke(255);  // Default stroke but can be changed
        float progress = float(frameCount % totalFrames) / totalFrames;
        translate(width/2, height/2);
        
        runSketch(progress);  // Run user's sketch with current progress
        
        String renderPath = "renders/render_v1";
        saveFrame(renderPath + "/frame-####.png");
        if (frameCount >= totalFrames) {
            exit();
        }
    } catch (Exception e) {
        println("Error in draw(): " + e.toString());
        hasError = true;
        exit();
    }
}