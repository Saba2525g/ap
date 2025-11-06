package exp03;

import java.util.Scanner;

public class Main_E3_3 {

    private int[][] matrix;
    private int rows, cols;

    public Main_E3_3() {
        Scanner input = new Scanner(System.in);

        System.out.print("Enter number of rows: ");
        rows = input.nextInt();

        System.out.print("Enter number of columns: ");
        cols = input.nextInt();

        matrix = new int[rows][cols];

        System.out.println("Enter matrix elements:");
        fillMatrix(input);

        findMaxRowSum();

        input.close();
    }

    private void fillMatrix(Scanner input) {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                matrix[i][j] = input.nextInt();
            }
        }
    }

    private void findMaxRowSum() {
        int maxSum = Integer.MIN_VALUE;
        int maxRow = 0;

        for (int i = 0; i < rows; i++) {
            int sum = 0;
            for (int j = 0; j < cols; j++) {
                sum += matrix[i][j];
            }

            if (sum > maxSum) {
                maxSum = sum;
                maxRow = i;
            }
        }

        System.out.println("The row with maximum sum is: Row " + (maxRow + 1));
        System.out.println("Maximum sum = " + maxSum);
    }

    public static void main(String[] args) {
        new Main_E3_3();
    }
}
