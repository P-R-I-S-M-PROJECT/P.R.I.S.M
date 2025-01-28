// === USER'S CREATIVE CODE ===
// --------------------------------------------------------
// 1) Define Classes at Top
// --------------------------------------------------------
class Dot {
  float x;
  float finalY;
  float startY;
  float radius;
  float noiseOffset;

  Dot(float x_, float y_) {
    x = x_;
    finalY = y_;
    // Start each dot well below its final position for a vertical "rise" animation
    startY = y_ + random(150, 400);
    // Random radius for organic variation
    radius = random(2, 5);
    // Small random offset for subtle vertical wave
    noiseOffset = random(1000);
  }

  void update(float progress) {
    // Interpolate from startY to finalY
    float yPos = lerp(startY, finalY, progress);
    // Add slight vertical wave for optical flair
    yPos += 10 * sin(noiseOffset + progress * TWO_PI * 2.0);

    // Display this dot
    display(x, yPos);
  }

  void display(float px, float py) {
    noStroke();
    // Monochromatic approach: white circles with some transparency
    fill(255, 180);
    ellipse(px, py, radius, radius);
  }
}

// --------------------------------------------------------
// 2) Declare Global Variables
// --------------------------------------------------------
PGraphics letterMask;
ArrayList<Dot> dots = new ArrayList<Dot>();

// --------------------------------------------------------
// 3) Define initSketch() for Setup
// --------------------------------------------------------
void initSketch() {
  // REQUIRED - Create Text Mask EXACTLY
    PGraphics letterMask;
  letterMask = createGraphics(1080, 1080);
  letterMask.beginDraw();
  letterMask.background(0);
  letterMask.fill(255);
  letterMask.textAlign(CENTER, CENTER);
  letterMask.textSize(200);  // Adjust size as needed
  letterMask.text("PRISM", letterMask.width/2, letterMask.height/2);
  letterMask.endDraw();

  // Create an ArrayList of dots inside the text mask
  int totalDots = 2000;
  int attempts = 0;

  while (dots.size() < totalDots && attempts < totalDots * 50) {
    float rx = random(-540, 540);
    float ry = random(-540, 540);
    // Check letterMask brightness
    color c = letterMask.get(int(rx + 540), int(ry + 540));
    if (brightness(c) > 0) {
      dots.add(new Dot(rx, ry));
    }
    attempts++;
  }
}

// --------------------------------------------------------
// 4) Define runSketch(progress) for Animation
//    progress goes from 0.0 to 1.0
// --------------------------------------------------------
void runSketch(float progress) {
  // Animate and display each Dot
  for (Dot d : dots) {
    d.update(progress);
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
        
        String renderPath = "renders/render_v1";
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