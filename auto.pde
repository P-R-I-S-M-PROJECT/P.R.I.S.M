// === USER'S CREATIVE CODE ===
class LSystem {
  String axiom;
  String rule;
  String current;
  
  LSystem(String axiom_, String rule_) {
    axiom = axiom_;
    rule = rule_;
    current = axiom;
  }

void generate() {
    StringBuilder next = new StringBuilder();
    for (int i = 0; i < current.length(); i++) {
      char c = current.charAt(i);
      if (c == 'F') {
        next.append(rule);
      } else {
        next.append(c);
      }
    }
    current = next.toString();
  }
  
  String getString() {
    return current;
  }
}

// Global variables
LSystem ls;
float angleDeg = 60; // angle to turn (degrees)
String fractalPath;
float length = 6; // length of each "F" segment

void initSketch() {
  // Initialize the L-System
  ls = new LSystem("F++F++F++F", "F-F++F-F");
  
  // Generate a few iterations
  int iterations = 3;
  for (int i = 0; i < iterations; i++) {
    ls.generate();
  }
  fractalPath = ls.getString();
}

void runSketch(float progress) {
  // Smooth rotation from 0 -> TWO_PI -> 0, over 0.0 to 1.0
  float rotationAmount = progress * TWO_PI;
  rotate(rotationAmount);
  
  // Vary color smoothly over time
  float r = lerp(50, 255, progress);
  float g = lerp(200, 100, progress);
  float b = lerp(180, 255, 1 - progress);
  stroke(r, g, b, 180);
  strokeWeight(1);
  noFill();
  
  // Parse the L-System string and draw
  float angleRad = radians(angleDeg);
  for (int i = 0; i < fractalPath.length(); i++) {
    char c = fractalPath.charAt(i);
    if (c == 'F') {
      line(0, 0, length, 0);
      translate(length, 0);
    } else if (c == '+') {
      rotate(angleRad);
    } else if (c == '-') {
      rotate(-angleRad);
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
        
        String renderPath = "renders/render_v465";
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