void setup() {
          size(800, 800);
          frameRate(60);
          smooth();
        }

        final int totalFrames = 360;
        boolean hasError = false;

        void draw() {
          try {
            background(0);
            stroke(255);  // Default stroke but can be changed
            float progress = float(frameCount % totalFrames) / totalFrames;
            translate(width/2, height/2);
            
            // YOUR CREATIVE CODE GOES HERE
  int gridCount = 30;
  float t = TWO_PI * progress;
  float spacing = 800.0 / (float)gridCount;
  float offset = -400.0 + spacing * 0.5;
  noFill();
  
  for(int i = 0; i < gridCount; i++){
    for(int j = 0; j < gridCount; j++){
      float x = offset + i * spacing;
      float y = offset + j * spacing;
      float r = sqrt(x * x + y * y);
      float angle = atan2(y, x);
      float wave = sin(r * 0.03 - angle * 4.0 + t * 2.0);
      float rad = 5.0 + wave * 2.0;
      
      stroke(
        (int)(128 + 127 * sin(wave)),
        (int)(128 + 127 * sin(wave * 2.0)),
        (int)(128 + 127 * sin(wave * 3.0))
      );
      strokeWeight(1.0);
      ellipse(x, y, rad, rad);
    }
  }
  // END OF YOUR CREATIVE CODE
            
            String renderPath = "renders/render_v2256";
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