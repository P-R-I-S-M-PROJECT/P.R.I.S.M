// === USER'S CREATIVE CODE ===
void runSketch(float progress) {
  int numCircles = 50;
  float maxRadius = 200;
  float waveSpeed = TWO_PI * 3;
  float rippleOffset = PI / 3;
  for (int i = 0; i < numCircles; i++) {
    float angle = map(i, 0, numCircles, 0, TWO_PI);
    float x = cos(angle + progress * TWO_PI) * maxRadius;
    float y = sin(angle + progress * TWO_PI) * maxRadius;
    float ripple = sin(progress * waveSpeed + i * rippleOffset);
    float radius = map(ripple, -1, 1, 5, maxRadius / 4);
    stroke(255, 200 - (255 * progress));
    strokeWeight(2);
    noFill();
    ellipse(x, y, radius, radius);
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
        
        String renderPath = "renders/render_v2342";
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