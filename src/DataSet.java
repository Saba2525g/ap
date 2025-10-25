import java.util.Scanner; //E6.5

 class E6_5 {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        DataSet data = new DataSet(); // make a new DataSet object to save numbers

        System.out.println("Enter numbers (enter 0 to stop):");

        while (true) {
            double num = input.nextDouble();
            if (num == 0) break;
            data.add(num); // send this number to the DataSet
        }


        System.out.println("Average: " + data.getAverage());
        System.out.println("Smallest: " + data.getSmallest());
        System.out.println("Largest: " + data.getLargest());
        System.out.println("Range: " + data.getRange());

        input.close();
    }
}

// This class will hold the numbers and calculate average, smallest, largest, and range
class DataSet {
    private double sum = 0; // to keep the total sum of all numbers
    private double smallest = Double.MAX_VALUE; // start with a very big number
    private double largest = Double.MIN_VALUE;  // start with a very small number
    private int count = 0; // how many numbers we have added

    // method to add a new number
    public void add(double value) {
        sum += value;
        count++;


        if (value < smallest) {
            smallest = value;
        }


        if (value > largest) {
            largest = value;
        }
    }

    public double getAverage() {
        if (count == 0) return 0;
        return sum / count;
    }


    public double getSmallest() {
        return smallest;
    }


    public double getLargest() {
        return largest;
    }


    public double getRange() {
        return largest - smallest;
    }
}

