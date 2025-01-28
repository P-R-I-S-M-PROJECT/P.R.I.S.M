// === USER'S CREATIVE CODE ===
// 1. Define any classes at the top
class Dot {
  float x;
  float baseY;
  float phi;  // Random phase offset for more organic motion

  Dot(float x, float baseY, float phi) {
    this.x = x;
    this.baseY = baseY;
    this.phi = phi;
  }

  void display(float progress) {
    // Calculate a wave that goes to zero 4 times during the loop:
    float wave = sin(4 * PI * progress);

    // Speed changes each quarter of the loop:
    float spd = 1 + floor(progress * 4);

    // Horizontal offset (changed from vertical offset)
    float offset = wave * spd * 30 * sin(phi);

    // Add spiral motion
    // We'll revolve around (x, baseY) as progress goes from 0..1:
    float swirlAngle = TWO_PI * 2 * progress + phi;  // two full rotations
    float swirlRadius = 50 * progress;               // grows with progress
    float swirlX = swirlRadius * cos(swirlAngle);
    float swirlY = swirlRadius * sin(swirlAngle);

    // Rainbow color
    pushStyle();
    colorMode(HSB, 1);
    float hueVal = (phi / TWO_PI + progress) % 1;
    fill(hueVal, 1, 1);
    noStroke();
    ellipse(x + offset + swirlX, baseY + swirlY, 5, 5);
    popStyle();
  }
}

// 2. Declare global variables
PGraphics letterMask;
ArrayList<Dot> dots = new ArrayList<Dot>();

// 3. Define initSketch() for setup
void initSketch() {
  // REQUIRED - EXACT letterMask initialization
    letterMask = createGraphics(1080, 1080);
  letterMask.beginDraw();
  letterMask.background(0);
  letterMask.fill(255);
  letterMask.textAlign(CENTER, CENTER);
  letterMask.textSize(200);
  letterMask.text("PRISM", letterMask.width/2, letterMask.height/2);
  letterMask.endDraw();

  // Populate an ArrayList of Dot objects only where the letterMask is white
  // For a symmetrical design, we add mirrored dots about the Y-axis
  int attempts = 10000; // Increase if needed for denser fill
  for (int i = 0; i < attempts; i++) {
    // Random X in [0..540] so we can mirror
    float rx = random(0, 540);
    float ry = random(-540, 540);

    int mx = (int)(rx + 540);
    int my = (int)(ry + 540);

    // Check brightness in the mask
    if (mx >= 0 && mx < 1080 && my >= 0 && my < 1080) {
      float b = brightness(letterMask.get(mx, my));
      if (b > 0) {
        // Add a dot for +rx
        dots.add(new Dot(rx, ry, random(TWO_PI)));
        // And add a symmetrical partner for -rx (unless rx == 0)
        if (rx != 0) {
          dots.add(new Dot(-rx, ry, random(TWO_PI)));
        }
      }
    }
  }
}

// 4. Define runSketch(progress) for animation
void runSketch(float progress) {
  // Use each dot's display method
  for (Dot d : dots) {
    d.display(progress);
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
        
        String renderPath = "renders/render_v9";
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