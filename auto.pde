// === USER'S CREATIVE CODE ===
void runSketch(float progress) {
  int numLines = 150;
  float spiralAngle = progress * TWO_PI * 6; // Complete 6 full rotations
  for (int i = 0; i < numLines; i++) {
      float angleOffset = map(i, 0, numLines, 0, TWO_PI);
      float radius = map(i, 0, numLines, 50, 300);
      float x1 = radius * cos(angleOffset + spiralAngle);
      float y1 = radius * sin(angleOffset + spiralAngle);
      float x2 = (radius + 10 * sin(progress * TWO_PI)) * cos(angleOffset + spiralAngle + PI);
      float y2 = (radius + 10 * sin(progress * TWO_PI)) * sin(angleOffset + spiralAngle + PI);
      stroke(map(sin(angleOffset + spiralAngle), -1, 1, 100, 255), 
             map(cos(angleOffset + spiralAngle), -1, 1, 100, 255), 
             200);
      strokeWeight(map(sin(angleOffset + spiralAngle), -1, 1, 1, 3));
      line(x1, y1, x2, y2);
  }
}

void initSketch() {
  // Initialize sketch
}
// END OF YOUR CREATIVE CODE

// === SYSTEM FRAMEWORK ===
void setup() {
    size(800, 800);
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
        
        String renderPath = "renders/render_v2340";
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