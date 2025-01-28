// === USER'S CREATIVE CODE ===
// ------------------------------------------------------------
// 1. (Optional) Classes
//    (No classes needed in this example; everything is handled
//     procedurally and via global variables/functions)
// ------------------------------------------------------------

// ------------------------------------------------------------
// 2.Global Variables
// ------------------------------------------------------------
int circleCount;
int recursionDepth;
float baseRadius;

// ------------------------------------------------------------
// 3.initSketch() - Called once at the start
// ------------------------------------------------------------
void initSketch() {
  // Configure global variables
  circleCount    = 6;     // Number of circles in each ring
  recursionDepth = 3;     // How deep the recursive pattern goes
  baseRadius     = 120;   // Base radius for the main circle
}

// ------------------------------------------------------------
// Utility: Returns a rainbow color using an angle-based approach
// ------------------------------------------------------------
color getRainbowColor(float angle) {
  // Create smoothly transitioning rainbow hues with sine waves
  float r = 127 + 127 * sin(angle + 0.0);
  float g = 127 + 127 * sin(angle + TWO_PI/3);
  float b = 127 + 127 * sin(angle + 2*TWO_PI/3);
  return color(r, g, b);
}

// ------------------------------------------------------------
// Recursive drawing of circles
// ------------------------------------------------------------
void drawRecursiveCircle(float x, float y, float r, int depth, float time, int index) {
  // Harmonic scale factor to make circles pulsate
  float scaleFactor = 0.8 + 0.2 * sin(time + index);
  float circleSize = 2.0 * r * scaleFactor; // diameter
  
  // Choose color based on time + index
  color c = getRainbowColor(time + index);
  
  noStroke();
  fill(c);
  ellipse(x, y, circleSize, circleSize);
  
  // If we still have recursion depth left, draw a ring of smaller circles
  if (depth > 0) {
    for (int i = 0; i < circleCount; i++) {
      float angleStep = TWO_PI / circleCount;
      float ringAngle = angleStep * i + time * 0.5;  // slight rotation over time
      
      // Additional harmonic motion in ring distance
      float ringDist = r * (1.5 + 0.2 * sin(time + i + index));
      
      float nx = x + ringDist * cos(ringAngle);
      float ny = y + ringDist * sin(ringAngle);
      
      // Recurse with half the radius, decreased depth, offset index
      drawRecursiveCircle(nx, ny, r * 0.5, depth - 1, time, index + i + 1);
    }
  }
}

// ------------------------------------------------------------
// 4.runSketch(progress) - Called each frame with progress 0..1
// ------------------------------------------------------------
void runSketch(float progress) {
  // progress goes from 0.0 to 1.0 over 6 seconds, then loops
  float t = progress * TWO_PI;  // Make one complete cycle from 0..2
  
  // Draw one fractal circle pattern at the center
  drawRecursiveCircle(0, 0, baseRadius, recursionDepth, t, 0);
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
        
        String renderPath = "renders/render_v2";
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