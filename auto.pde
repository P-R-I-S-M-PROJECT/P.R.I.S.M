// === USER'S CREATIVE CODE ===
int numLines = 100;
float lineSpacing, lineWeight, lineLength;
float xFreq, yFreq, zFreq;
float xAmp, yAmp;
float zOffset, zInc;

void initSketch() {
  lineSpacing = 15;
  lineWeight = 2;
  lineLength = 400;
  
  xFreq = 0.017;
  yFreq = 0.037;
  zFreq = 0.067;
  
  xAmp = 120;
  yAmp = 80;

  zOffset = 0;
  zInc = 0.03;
  
  strokeWeight(lineWeight);
}

void runSketch(float progress) {
  float angle = progress * TWO_PI;
  
  for (int i = 0; i < numLines; i++) {
    float z = i * lineSpacing + zOffset;
    float x = xAmp * cos(z * xFreq + angle);  
    float y = yAmp * sin(z * yFreq + angle);
    
    stroke(255 * (i%2), 200, 255 - z/2, 100);
    line(x, -lineLength/2 + y, x, lineLength/2 + y);
  }
  
  zOffset += zInc;
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
        
        String renderPath = "renders/render_v2362";
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