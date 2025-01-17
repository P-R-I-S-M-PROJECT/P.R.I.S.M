// === USER'S CREATIVE CODE ===
int numPoints = 300;
float radius = 300;
float angle = 0;
float angleSpeed = 0.01;
float radiusSpeed = 0.5;
float noiseScale = 0.02;
float noiseSpeed = 0.01;
float noiseStrength = 50;

void initSketch() {
  strokeWeight(2);
  colorMode(HSB, 360, 100, 100, 100);
}

void runSketch(float progress) {
  float hue = 360 * progress;
  float alpha = map(sin(TWO_PI * progress), -1, 1, 50, 100);
  
  stroke(hue, 80, 100, alpha);
  noFill();
  
  beginShape();
  for (int i = 0; i < numPoints; i++) {
    float t = map(i, 0, numPoints - 1, 0, TWO_PI);
    float noiseFactor = noise(noiseScale * cos(t), noiseScale * sin(t), noiseSpeed * progress);
    float r = radius + noiseStrength * noiseFactor;
    float x = r * cos(angle + radiusSpeed * t);
    float y = r * sin(angle + radiusSpeed * t);
    vertex(x, y);
  }
  endShape(CLOSE);
  
  angle += angleSpeed;
  radius = map(sin(TWO_PI * progress), -1, 1, 200, 400);
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
        
        String renderPath = "renders/render_v4";
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