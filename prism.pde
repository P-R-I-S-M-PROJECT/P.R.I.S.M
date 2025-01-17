// === USER'S CREATIVE CODE ===
float phi = (1 + sqrt(5)) / 2;  // golden ratio
float angle = 0;
float radius = 300;
int numPoints = 200;
float[] radii = new float[numPoints];

void initSketch() {
  noFill();
  strokeWeight(2);
  
  // Initialize radii using golden ratio
  for (int i = 0; i < numPoints; i++) {
    radii[i] = 100 * pow(phi, i/10.0);
  }
}

void runSketch(float progress) {
  float t = progress * TWO_PI;
  
  stroke(255, 150, 0);
  
  // Draw spiraling cardioids 
  for (int i = 0; i < 8; i++) {
    pushMatrix();
    rotate(i * PI/4 + t);
    
    beginShape();
    for (int j = 0; j < numPoints; j++) {
      float a = map(j, 0, numPoints, 0, TWO_PI);
      float r = radii[j] * (1 - sin(t*2 + i)) * (1 + cos(a*8)) / 2;
      float x = r * cos(a);
      float y = r * sin(a);
      vertex(x, y);
    }
    endShape(CLOSE);
    
    popMatrix();
  }
  
  stroke(0, 255, 150);
  
  // Draw central golden spiral 
  beginShape();
  for (int i = 0; i < 500; i++) {
    float a = i * radians(137.5); // golden angle  
    float r = radius * sqrt(i/500.0);
    float x = r * cos(a + t);
    float y = r * sin(a + t);
    vertex(x, y);
  }
  endShape();
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
        
        String renderPath = "renders/render_v5";
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