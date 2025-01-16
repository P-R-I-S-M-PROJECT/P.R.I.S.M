// === USER'S CREATIVE CODE ===
void runSketch(float progress) {
  float radius = 300;
  int numPoints = 200;
  float angleStep = TWO_PI / numPoints;
  for (int i = 0; i < numPoints; i++) {
      float angle = i * angleStep;
      float x = radius * cos(angle);
      float y = radius * sin(angle);
      float mappedAngle = map(progress, 0, 1, 0, TWO_PI * 2);
      float targetAngle = i * angleStep * 2 + mappedAngle;
      float targetX = radius * cos(targetAngle);
      float targetY = radius * sin(targetAngle);
      stroke(255, 100, 150);
      line(x, y, targetX, targetY);
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
        
        String renderPath = "renders/render_v357";
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