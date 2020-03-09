import ij.ImagePlus;
import ij.gui.PlotWindow;
import ij.gui.PolygonRoi;
import ij.gui.Roi;
import ij.io.FileSaver;
import ij.plugin.filter.PlugInFilter;
import ij.process.FloatProcessor;
import ij.process.ImageProcessor;
import java.awt.Rectangle;

public class Preprocessor_2 implements PlugInFilter {
  ImagePlus imp;
  
  public int setup(String paramString, ImagePlus paramImagePlus) {
    this.imp = paramImagePlus;
    return 31;
  }
  
  public void run(ImageProcessor paramImageProcessor) {
    paramImageProcessor.setInterpolate(true);
    boolean bool = PlotWindow.interpolate;
    Roi roi = this.imp.getRoi();
    
    int numRoiPts = ( (PolygonRoi) roi ).getNCoordinates();
    int[] roiPtsXCoordinates = ((PolygonRoi) roi).getXCoordinates();
    int[] roiPtsYCoordinates = ((PolygonRoi) roi).getroiPtsYCoordinates();
    Rectangle roiBounds = roi.getBounds();
    
    double totalDistance = 0.0D;
    double[] pairWiseDistances = new double[numRoiPts];
    int[] pairWiseXDeltas = new int[numRoiPts];
    int[] pairWiseYDeltas = new int[numRoiPts];
    for (byte currPtIndex = 0; currPtIndex < numRoiPts - 1; currPtIndex++) {
      int pairWiseXDelta = roiPtsXCoordinates[currPtIndex + 1] - roiPtsXCoordinates[currPtIndex];
      int pairWiseYDelta = roiPtsYCoordinates[currPtIndex + 1] - roiPtsYCoordinates[currPtIndex];
      double distance = Math.sqrt((pairWiseXDelta * pairWiseXDelta + pairWiseYDelta * pairWiseYDelta));

      totalDistance += distance;
      pairWiseDistances[currPtIndex] = d;
      pairWiseXDeltas[currPtIndex] = pairWiseXDelta;
      pairWiseYDeltas[currPtIndex] = pairWiseYDelta;
    } 
    double[] totalDistArray = new double[(int)totalDistance];

    
    // not sure what the reason for constant height is
    byte FLOAT_PROCESSOR_HEIGHT_CONSTANT = 15;
    int floatProcessorWidth = (int)totalDistance;
    int floatProcessorHeight = FLOAT_PROCESSOR_HEIGHT_CONSTANT * 2 + 1;
    FloatProcessor floatProcessor = new FloatProcessor(floatProcessorWidth, floatProcessorHeight);

    
    double d2 = 1.0D;
    double d3 = 0.0D;
    
    double d4 = 0.0D, d5 = 0.0D, d6 = 0.0D;
    for (byte currPtIndex = 0; currPtIndex < numRoiPts; currPtIndex++) {
      double currDist = pairWiseDistances[currPtIndex];
      if (currDist != 0.0D) {

        
        double angleBetween = Math.atan2(pairWiseYDeltas[currPtIndex], pairWiseXDeltas[currPtIndex]);
        double d8 = d7 - 1.5707963267948966D;


        
        double d9 = pairWiseXDeltas[currPtIndex] / currDist;
        double d10 = pairWiseYDeltas[currPtIndex] / currDist;
        double d11 = 1.0D - d2;
        double d12 = (roiBounds.x + roiPtsXCoordinates[currPtIndex]) + d11 * d9;
        double d13 = (roiBounds.y + roiPtsYCoordinates[currPtIndex]) + d11 * d10;
        double d14 = d - d11;
        int i2 = (int)d14;
        for (byte b = 0; b <= i2; b++) {
          int i3 = (int)d3 + b;
          
          if (i3 < totalDistArray.length) {

            
            for (byte b6 = 0; b6 < n; b6++) {
              double d15 = Math.cos(d8) * (b2 - b6);
              double d16 = Math.sin(d8) * (b2 - b6);
              double d17 = d12 + d15;
              double d18 = d13 + d16;
              floatProcessor.putPixelValue(i3, b6, paramImageProcessor.getInterpolatedValue(d17, d18));
              String str = String.valueOf(d17);
            } 

            d4 = d12; d5 = d13;
          } 
          d12 += d9;
          d13 += d10;
        } 
        d3 += d;
        d2 = d14 - i2;
      } 
    } 









    
    ImageProcessor imageProcessor1 = floatProcessor.duplicate();
    imageProcessor1.medianFilter();
    imageProcessor1.smooth();




    
    ImageProcessor imageProcessor2 = imageProcessor1.duplicate();
    int i1 = imageProcessor2.getWidth();
    float[][] arrayOfFloat = imageProcessor2.getFloatArray();
    
    byte b4 = 5;
    for (byte b5 = 0; b5 < i1; b5++) {
      
      float f = (arrayOfFloat[b5][b4 - 1] - arrayOfFloat[b5][n - b4]) / (n - b4 * 2 + 1);
      for (byte b = b4; b < n - b4; ) { arrayOfFloat[b5][b] = arrayOfFloat[b5][b - 1] - f; b++; }
    
    } 
    
    imageProcessor2.setFloatArray(arrayOfFloat);




    
    ImageProcessor imageProcessor3 = floatProcessor.duplicate();

    
    imageProcessor3.copyBits(imageProcessor2, 0, 0, 4);

    
    ImageProcessor imageProcessor4 = imageProcessor3.convertToShort(false);
    ImagePlus imagePlus = new ImagePlus("subtracted", imageProcessor4);
    
    imagePlus.show();


    
    FileSaver fileSaver = new FileSaver(imagePlus);
    fileSaver.saveAsText();
  }
}