// === USER'S CREATIVE CODE ===
// Global variables
float[] hues;
int numCurves = 12;
float sortThreshold = 0.3;

void initSketch() {
  // Initialize array of hue values
  hues = new float[numCurves];
  for (int i = 0; i < numCurves; i++) {
    hues[i] = map(i, 0, numCurves, 0, 255);
  }
  
  strokeWeight(2);
  noFill();
}

void runSketch(float progress) {
  // Create semi-transparent overlay for trail effect
  fill(0, 25);
  rect(-width/2, -height/2, width, height);
  noFill();
  
  // Draw multiple Lissajous curves with different frequencies
  for (int i = 0; i < numCurves; i++) {
    float phase = progress * TWO_PI + (float)i/numCurves * PI;
    float freq1 = 3 + i * 0.5;
    float freq2 = 2 + i * 0.3;
    
    // Calculate base color with shifting hue
    float hue = (hues[i] + progress * 100) % 255;
    color c = color(hue, 200, 255);
    
    // Draw main curve
    beginShape();
    for (float t = 0; t < TWO_PI; t += 0.02) {
      float x = sin(t * freq1 + phase) * 300;
      float y = sin(t * freq2) * 300;
      
      // Add vertical pixel sorting effect based on position
      float sortOffset = 0;
      if (abs(x/300) > sortThreshold) {
        sortOffset = map(abs(x/300), sortThreshold, 1, 0, 50) * sin(progress * TWO_PI);
      }
      
      // Adjust color based on sorting effect
      stroke(red(c), green(c), blue(c), map(abs(x/300), 0, 1, 255, 100));
      vertex(x, y + sortOffset);
    }
    endShape();
  }
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
        
        String renderPath = "renders/render_v2359";
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