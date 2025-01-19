// === USER'S CREATIVE CODE ===
void runSketch(float progress) {
  float maxRadius = 300;
  int numSpirals = 12;
  float angleOffset = TWO_PI / numSpirals;
  float waveFrequency = 3.0;
  for (int i = 0; i < numSpirals; i++) {
      float angle = i * angleOffset + progress * TWO_PI;
      float radius = maxRadius * noise(i * 0.1, progress * 2.0);
      beginShape();
      for (float a = 0; a < TWO_PI; a += 0.1) {
          float wave = sin(a * waveFrequency + progress * TWO_PI) * 50;
          float x = (radius + wave) * cos(a + angle);
          float y = (radius + wave) * sin(a + angle);
          stroke(200 - a * 30, 100 + a * 50, 255);
          vertex(x, y);
      }
      endShape(CLOSE);
  }
}

void initSketch() {
  // Initialize sketch
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