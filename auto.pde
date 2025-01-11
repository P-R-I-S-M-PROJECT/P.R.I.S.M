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
  float numPetals = 12;
  float maxRadius = 300;
  float petalLength = 250;
  float petalWidth = 50;
  
  // Loop over each petal
  for (int i = 0; i < numPetals; i++) {
      // Calculate the angle for this petal
      float angle = map(i, 0, numPetals, 0, TWO_PI) + progress * TWO_PI;
      
      // Calculate the petal tip coordinates
      float x1 = maxRadius * cos(angle);
      float y1 = maxRadius * sin(angle);
      float x2 = (maxRadius + petalLength) * cos(angle);
      float y2 = (maxRadius + petalLength) * sin(angle);
  
      // Draw a petal with a line for the spine and two arcs as boundaries
      stroke(255, 0, 150); // Pink color
      strokeWeight(2);
      line(x1, y1, x2, y2);
      
      noFill(); // No fill for the petal arches
      stroke(100, 200, 255); // Light blue color
      arc((x1 + x2)/2, (y1 + y2)/2, petalWidth, petalLength, angle + HALF_PI, angle - HALF_PI);
      arc((x1 + x2)/2, (y1 + y2)/2, petalWidth, petalLength, angle - HALF_PI, angle + HALF_PI);
  }
  // END OF YOUR CREATIVE CODE
            
            String renderPath = "renders/render_v2288";
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