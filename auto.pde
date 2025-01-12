// === USER'S CREATIVE CODE ===
void runSketch(float progress) {
  int numPetals = 8; // Number of petals in our flower-like shape
  float radius = 150; // Radius of the floral structure
  for (int i = 0; i < numPetals; i++) {
      float angleOffset = TWO_PI / numPetals; // Offset angle for each petal
      float petalAngle = i * angleOffset + progress * TWO_PI; // Calculate current angle of each petal
      float x1 = cos(petalAngle) * radius;
      float y1 = sin(petalAngle) * radius;
      float x2 = cos(petalAngle + angleOffset / 2) * radius / 2;
      float y2 = sin(petalAngle + angleOffset / 2) * radius / 2;
      stroke(255 * abs(sin(petalAngle)), 100, 255 * abs(cos(petalAngle)));
      strokeWeight(3);
      noFill();
      bezier(0, 0, x1, y1, x2, y2, -x1, -y1); // Draw a bezier curve for each petal
  }
  float particleRadius = 280;
  int numParticles = 20;
  for (int j = 0; j < numParticles; j++) {
      float particleAngle = j * TWO_PI / numParticles + progress * TWO_PI; // Calculate particle angle based on progress
      float px = cos(particleAngle) * particleRadius;
      float py = sin(particleAngle) * particleRadius;
      stroke(255);
      strokeWeight(2);
      point(px, py); // Draw the particle as a point
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
        
        String renderPath = "renders/render_v2344";
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