// === USER'S CREATIVE CODE ===
// ------------------------------------------------------
// 1) (OPTIONAL) CLASSES OR HELPER FUNCTIONS
// ------------------------------------------------------

ArrayList<PVector> superellipsePoints;
PGraphics pg;

// Create a set of points along a superellipse
ArrayList<PVector> makeSuperellipse(float radius, float exponent, int resolution) {
  ArrayList<PVector> pts = new ArrayList<PVector>();
  for (int i = 0; i < resolution; i++) {
    float t = map(i, 0, resolution, 0, TWO_PI);
    float x = pow(abs(cos(t)), 2.0/exponent);
    float y = pow(abs(sin(t)), 2.0/exponent);
    // Retain sign so we get the "superellipse" in all quadrants
    x *= cos(t) < 0 ? -radius : radius;
    y *= sin(t) < 0 ? -radius : radius;
    pts.add(new PVector(x, y));
  }
  return pts;
}

// ------------------------------------------------------
// 2) DECLARE GLOBAL VARIABLES
// ------------------------------------------------------
// (They are at the top: "pg" and "superellipsePoints")

// ------------------------------------------------------
// 3) initSketch() - Called ONCE at the start
// ------------------------------------------------------
void initSketch() {
  // Create an offscreen buffer for a feedback-like effect
  pg = createGraphics(width, height);

  // Generate superellipse shape points
  superellipsePoints = makeSuperellipse(280, 2.5, 240);

  // Optional: set color mode on our buffer
  pg.beginDraw();
  pg.colorMode(HSB, 255);
  pg.endDraw();
}

// ------------------------------------------------------
// 4) runSketch(progress) - Called EACH FRAME
//    progress goes from 0.0 to 1.0 over 6 seconds
// ------------------------------------------------------
void runSketch(float progress) {
  // Begin drawing in the offscreen buffer
  pg.beginDraw();

  // Fade out the previous frame slightly for a feedback-like effect
  pg.noStroke();
  pg.fill(0, 10); // Very gentle fade
  pg.rect(0, 0, pg.width, pg.height);

  pg.pushMatrix();
  // Move to center of pg
  pg.translate(pg.width/2, pg.height/2);

  // Gradually rotate over one full turn as progress goes from 0..1
  float angle = progress * TWO_PI;
  pg.rotate(angle);

  // Let the hue shift over progress
  float hueVal = (progress * 255) % 255;

  // Draw the superellipse shape
  pg.stroke(hueVal, 255, 255, 150);
  pg.noFill();

  pg.beginShape();
  for (PVector pt : superellipsePoints) {
    pg.vertex(pt.x, pt.y);
  }
  pg.endShape(CLOSE);

  pg.popMatrix();
  pg.endDraw();

  // Draw our offscreen buffer onto the main canvas (already centered)
  image(pg, -width/2, -height/2);
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
        
        String renderPath = "renders/render_v2343";
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