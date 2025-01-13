// === USER'S CREATIVE CODE ===
class Rose {
  float k;
  float amplitude;
  
  Rose(float kValue, float amp) {
    k = kValue;
    amplitude = amp;
  }

void drawRose(float offset, float hueShift) {
    // Use a small step for smooth curves
    float step = 0.01;
    // Set dynamic color shifted by progress
    stroke(
      (int)((150 + hueShift) % 255), 
      (int)((100 + hueShift * 2) % 255), 
      (int)((200 + hueShift * 3) % 255)
    );
    noFill();
    beginShape();
    for (float a = 0; a < TWO_PI; a += step) {
      float r = amplitude * cos(k * (a + offset));
      float x = r * cos(a + offset);
      float y = r * sin(a + offset);
      vertex(x, y);
    }
    endShape(CLOSE);
  }
}

// Global variables
Rose[] roses;
float phi = (1 + sqrt(5)) / 2.0; // Golden ratio

void initSketch() {
  // Create an array of Rose objects with different k values
  roses = new Rose[5];
  
  // Spread amplitude using some golden ratio offsets
  for (int i = 0; i < roses.length; i++) {
    float kVal = 2 + i; 
    float amp = 100 + i * 30 * phi;
    roses[i] = new Rose(kVal, amp);
  }
}

void runSketch(float progress) {
  // progress goes from 0.0 to 1.0 over 6 seconds
  // Use it to create a looping angle and color offset
  float angleOffset = progress * TWO_PI;
  float colorShift  = progress * 255;
  
  // Draw each rose curve
  for (int i = 0; i < roses.length; i++) {
    roses[i].drawRose(angleOffset, colorShift + i * 40);
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
        
        String renderPath = "renders/render_v90";
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