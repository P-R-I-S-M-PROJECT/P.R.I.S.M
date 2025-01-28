// === USER'S CREATIVE CODE ===
class Spiro {
  float R, r, p;

  // Removed direct color assignment in favor of dynamic/animated colors
  Spiro(float bigR, float smallR, float penOffset) {
    R = bigR;
    r = smallR;
    p = penOffset;
  }

  void drawSpiro(float offset, int detail) {
    // Use HSB for more "trippy" color transitions
    colorMode(HSB, 360, 100, 100, 100);
    noStroke();
    rectMode(CENTER);

    for (int i = 0; i < detail; i++) {
      float t = map(i, 0, detail, 0, TWO_PI * 4);
      float x = (R - r) * cos(t + offset) + p * cos(((R - r) / r) * (t + offset));
      float y = (R - r) * sin(t + offset) - p * sin(((R - r) / r) * (t + offset));

      pushMatrix();
      translate(x, y);
      rotate(t + offset);

      // Dynamic hue based on angle
      float hueVal = (degrees(t + offset) * 2) % 360;
      // Vary square size for extra movement
      float sqSize = 6 + 6 * sin((t + offset) * 3);

      // Primary square
      fill(hueVal, 100, 100, 80);
      rect(0, 0, sqSize, sqSize);

      // Secondary "square influence" rotated for a trippier effect
      rotate(PI / 4);
      fill((hueVal + 180) % 360, 100, 100, 60);
      rect(0, 0, sqSize * 0.7, sqSize * 0.7);

      popMatrix();
    }
  }
}

// Global variables
Spiro[] spiros;

void initSketch() {
  // More varied parameters for extra complexity
  spiros = new Spiro[4];
  spiros[0] = new Spiro(200, 60, 20);
  spiros[1] = new Spiro(250, 30, 80);
  spiros[2] = new Spiro(180, 80, 40);
  // An additional spiro for a fuller composition
  spiros[3] = new Spiro(220, 40, 60);
}

void runSketch(float progress) {
  // progress goes from 0.0 to 1.0 in a loop, mapping to one full rotation
  float angle = progress * TWO_PI;

  // Draw each spirograph with a slight offset variation
  for (int i = 0; i < spiros.length; i++) {
    float offset = angle * (1 + 0.3 * i);
    spiros[i].drawSpiro(offset, 600);
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
        
        String renderPath = "renders/render_v2";
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