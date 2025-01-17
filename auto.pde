// === USER'S CREATIVE CODE ===
float noiseScale = 0.003;
int numPoints = 12;
float radius = 250;
float spiralGrowth = 15;

void initSketch() {
  noFill();
  strokeWeight(2);
}

void runSketch(float progress) {
  // Create multiple layers with different rotations and colors
  for (int layer = 0; layer < 5; layer++) {
    float layerProgress = (progress + (float)layer/5) % 1.0;
    float rotation = layerProgress * TWO_PI;
    
    // Color transition based on progress
    float hue = (layerProgress * 255 + layer * 50) % 255;
    stroke(hue, 200, 255, 150);
    
    beginShape();
    for (float i = 0; i < numPoints; i++) {
      float angle = map(i, 0, numPoints, 0, TWO_PI);
      
      // Morph between different shapes using noise
      float noiseVal = noise(cos(angle) * noiseScale * (1 + layer),
                            sin(angle) * noiseScale * (1 + layer),
                            layerProgress * 2);
      
      float morphRadius = radius * (0.8 + 0.4 * noiseVal);
      
      // Add spiral effect
      float spiralRadius = morphRadius + (i * spiralGrowth);
      
      // Calculate final position with rotation
      float x = cos(angle + rotation) * spiralRadius;
      float y = sin(angle + rotation) * spiralRadius;
      
      // Add subtle perlin noise movement
      x += 20 * noise(layerProgress * 2 + i, 0);
      y += 20 * noise(0, layerProgress * 2 + i);
      
      curveVertex(x, y);
      
      // Close the shape smoothly
      if (i == 0 || i == numPoints-1) {
        curveVertex(x, y);
      }
    }
    endShape(CLOSE);
    
    // Draw connecting lines between layers
    if (layer > 0) {
      float prevRotation = ((progress + (float)(layer-1)/5) % 1.0) * TWO_PI;
      for (int i = 0; i < numPoints; i += 2) {
        float angle = map(i, 0, numPoints, 0, TWO_PI);
        float x1 = cos(angle + rotation) * radius;
        float y1 = sin(angle + rotation) * radius;
        float x2 = cos(angle + prevRotation) * (radius + spiralGrowth);
        float y2 = sin(angle + prevRotation) * (radius + spiralGrowth);
        
        stroke(hue, 200, 255, 50);
        line(x1, y1, x2, y2);
      }
    }
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
        
        String renderPath = "renders/render_v459";
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