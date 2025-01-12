// === USER'S CREATIVE CODE ===
// Wave parameters
float[] amplitudes = new float[5];
float[] frequencies = new float[5];
float[] phases = new float[5];
float[] colors = new float[5];

void initSketch() {
  // Initialize wave parameters with interesting variations
  for (int i = 0; i < 5; i++) {
    amplitudes[i] = random(50, 150);
    frequencies[i] = random(2, 6);
    phases[i] = random(TWO_PI);
    colors[i] = random(100, 255);
  }
}

void runSketch(float progress) {
  // Create smooth wave interference patterns
  noFill();
  strokeWeight(2);
  
  // Draw multiple rotating wave forms
  for (int layer = 0; layer < 5; layer++) {
    stroke(colors[layer], 100 + layer * 30, 255 - layer * 30, 150);
    
    beginShape();
    for (float angle = -PI; angle <= PI; angle += 0.05) {
      float r = 0;
      // Combine multiple sine waves
      for (int w = 0; w < 5; w++) {
        r += sin(angle * frequencies[w] + progress * TWO_PI + phases[w]) * amplitudes[w];
      }
      
      // Add some perlin noise movement
      float noise_offset = noise(angle * 0.5 + progress * 2, layer * 0.5) * 30;
      r += noise_offset;
      
      // Convert polar to cartesian coordinates
      float x = cos(angle) * r;
      float y = sin(angle) * r;
      
      curveVertex(x, y);
    }
    endShape();
    
    // Rotate each layer slightly differently
    rotate(sin(progress * TWO_PI) * 0.1);
  }
  
  // Add floating particles
  for (int i = 0; i < 20; i++) {
    float angle = noise(i * 0.5, progress * 2) * TWO_PI;
    float radius = noise(i * 0.5, progress * 2 + 1000) * 300;
    float x = cos(angle) * radius;
    float y = sin(angle) * radius;
    
    fill(255, 255, 255, 100);
    noStroke();
    circle(x, y, 5);
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
        
        String renderPath = "renders/render_v2349";
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