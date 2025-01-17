// === USER'S CREATIVE CODE ===
int numPoints = 400;
float a = 200;
float b = 50;

void initSketch() {
  stroke(255);
  strokeWeight(2);
  noFill();
}

void runSketch(float progress) {
  float t = progress * TWO_PI;
  float k = b / a;
  
  beginShape();
  for (int i = 0; i < numPoints; i++) {
    float angle = map(i, 0, numPoints, 0, TWO_PI);
    float x = (a-b) * cos(angle) + b * cos((a-b)/b * angle);
    float y = (a-b) * sin(angle) - b * sin((a-b)/b * angle);
    
    float r = map(sin(t*3 + angle*8), -1, 1, 100, 255);
    float g = map(cos(t*2 + angle*4), -1, 1, 100, 255);
    float b = map(sin(t + angle*12), -1, 1, 100, 255);
    stroke(r, g, b);
    
    vertex(x * (1 + 0.2*sin(t)), y * (1 + 0.2*cos(t)));
  }
  endShape(CLOSE);
  
  float s = map(sin(t), -1, 1, 0.2, 0.8);  
  scale(s);
  rotate(t);
}
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
        
        String renderPath = "renders/render_v460";
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