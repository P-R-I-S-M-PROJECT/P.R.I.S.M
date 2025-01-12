// === USER'S CREATIVE CODE ===
void runSketch(float progress) {
  int numLines = 100;
  float maxRadius = 300;
  for (int i = 0; i < numLines; i++) {
    float angle = TWO_PI * i / numLines;
    float radius = maxRadius * sin(progress * PI + angle);
    float x1 = radius * cos(angle);
    float y1 = radius * sin(angle);
    float x2 = maxRadius * cos(angle);
    float y2 = maxRadius * sin(angle);
    stroke(255 - (i * 255 / numLines), 100, i * 255 / numLines);
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
        
        String renderPath = "renders/render_v2348";
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