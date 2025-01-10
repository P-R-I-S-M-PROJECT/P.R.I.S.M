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
  int totalPoints = 500;
  float angleOffset = TWO_PI * progress;
  float scaleFactor = 300;
  float goldenAngle = radians(137.508);
  
  for(int i = 0; i < totalPoints; i++) {
      float angle = i * goldenAngle + angleOffset;
      float radius = scaleFactor * sqrt(i / (float)totalPoints);
      float x = radius * cos(angle);
      float y = radius * sin(angle);
      
      float brightness = map(i, 0, totalPoints, 50, 255);
      stroke(brightness);
      point(x, y);
  }
  // END OF YOUR CREATIVE CODE
            
            String renderPath = "renders/render_v2183";
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